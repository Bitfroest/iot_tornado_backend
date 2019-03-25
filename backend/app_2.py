from tornado import websocket, web, ioloop, gen, escape, httpserver, options
import json
from bson import json_util
import datetime

from config import config
import momoko

import psycopg2
from psycopg2.extras import RealDictCursor

import os
import signal
import logging
import tornado.ioloop
import traceback

is_closing = False
cl = []
clients = set()

REACT_FOLDER = "./build/"

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class BaseException(web.HTTPError):
    pass

class BaseHandler(web.RequestHandler):
    @property
    def db(self):
        return self.application.db

'''
https://gist.github.com/mminer/5464753
'''
class JsonHandler(BaseHandler):
    """Request handler where requests and responses speak JSON."""
    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))

    def write_json(self):
        output = json_util.dumps(self.response)
        self.write(output)

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("./build/index.html")

class IndexReactStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or not os.path.exists('./build/' + url_path):
            url_path = 'index.html'

        return super(IndexReactStaticFileHandler, self).parse_url_path(url_path)

class SensorTypesHandler(JsonHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        global cl
        #db = self.settings['db']
        cl = []
        #db.sensor.find({}).each(self.each)
        try:
            cursor = yield self.db.execute("SELECT * FROM sensor_type", cursor_factory=RealDictCursor)
            self.response = cursor.fetchall()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def post(self):
        data = self.request.arguments
        sql = "INSERT INTO sensor_type(name, typedef) VALUES(%s, %s) RETURNING id, name, typedef;"
        if 'name' in data and 'typedef' in data:
            name = data.get("name", "")
            typedef = data.get("typedef", "")
            cursor = yield self.db.execute(sql, (name,json.dumps(typedef),) , cursor_factory=RealDictCursor)
            self.response = cursor.fetchone()
            self.write_json()
        else:
            error = {"error": {"name": "Parameter invalid.","typedef":"Parameter invalid."}}
            self.write_error(status_code=400,message=error)

class SensorTypeHandler(JsonHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self, id):
        try:
            cursor = yield self.db.execute("SELECT * FROM sensor_type WHERE sensor_type.id = %s", (id,), cursor_factory=RealDictCursor)
            self.response = cursor.fetchone()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def delete(self, id):
        try:
            cursor = yield self.db.execute("DELETE FROM sensor_type WHERE sensor_type.id = %s RETURNING *", (id,), cursor_factory=RealDictCursor)
            self.response = cursor.fetchone()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def put(self, id):
        data = self.request.arguments
        sql = "UPDATE sensor_type SET name = %s, typedef = %s WHERE sensor_type.id = %s RETURNING id, name, typedef;"
        if 'name' in data and 'typedef' in data:
            name = data.get("name")
            typedef = data.get("typedef")
            try:
                cursor = yield self.db.execute(sql, (name,json.dumps(typedef),id,) , cursor_factory=RealDictCursor)
            except (psycopg2.Warning, psycopg2.Error) as error:
                logging.error(error.pgerror)
                logging.error(error.diag.message_detail)
                raise BaseException(reason=error.diag.message_detail, status_code=400)
            else:
                self.response = cursor.fetchone()
                self.write_json()
        else:
            error = {"error": {"name": "Parameter invalid.","typedef":"Parameter invalid."}}
            self.write_error(status_code=400,message=error)


class SensorsHandler(JsonHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        global cl
        #db = self.settings['db']
        cl = []
        #db.sensor.find({}).each(self.each)
        try:
            cursor = yield self.db.execute("SELECT *, st_asgeojson(coordinates)::json as coordinatesjson FROM sensor", cursor_factory=RealDictCursor)
            self.response = cursor.fetchall()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def post(self):
        data = self.request.arguments
        sql = "INSERT INTO sensor(name, note, id_sensor_type) VALUES(%s, %s, %s) RETURNING id, name, note, id_sensor_type;"
        if 'name' in data and 'note' in data and 'id_sensor_type' in data:

            name = data.get("name", "")
            note = data.get("note", "")
            id_sensor_type = data.get("id_sensor_type")
            logging.error(str(id_sensor_type))
            if id_sensor_type is None:
                raise BaseException(reason='Wrong Sensor Type ID.', status_code=400)
            try:
                cursor = yield self.db.execute(sql, (name,note,id_sensor_type,) , cursor_factory=RealDictCursor)
            except (psycopg2.Warning, psycopg2.Error) as error:
                logging.error(error.pgerror)
                logging.error(error.diag.message_detail)
                raise BaseException(reason=error.diag.message_detail, status_code=400)
            else:
                self.response = cursor.fetchone()
            self.write_json()
        else:
            error = {"error": {"name": "Parameter invalid.","note":"Parameter invalid.","id_sensor_type":"Parameter invalid."}}
            self.write_error(status_code=400,message=error)

class SensorHandler(JsonHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self, sensor_id):
        try:
            cursor = yield self.db.execute("SELECT *, st_asgeojson(coordinates)::json as coordinatesjson FROM sensor WHERE sensor.id = %s", (sensor_id,), cursor_factory=RealDictCursor)
            self.response = cursor.fetchone()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def delete(self, sensor_id):
        try:
            cursor = yield self.db.execute("DELETE FROM sensor WHERE sensor.id = %s RETURNING *", (sensor_id,), cursor_factory=RealDictCursor)
            self.response = cursor.fetchone()
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})

    @web.asynchronous
    @gen.coroutine
    def put(self, sensor_id):
        data = self.request.arguments
        sql = "UPDATE sensor SET name = %s, note = %s, id_sensor_type = %s, coordinates = ST_SetSRID(ST_MakePoint(%s, %s), 4326) WHERE sensor.id = %s RETURNING id, name, note, id_sensor_type;"
        if 'name' in data and 'note' in data and 'id_sensor_type' in data:
            name = data.get("name")
            note = data.get("note")
            id_sensor_type = data.get("id_sensor_type")
            coordinates = data.get("coordinates")
            try:
                cursor = yield self.db.execute(sql, (name, note, id_sensor_type, coordinates[0], coordinates[1], sensor_id,) , cursor_factory=RealDictCursor)
            except (psycopg2.Warning, psycopg2.Error) as error:
                logging.error(error.pgerror)
                logging.error(error.diag.message_detail)
                raise BaseException(reason=error.diag.message_detail, status_code=400)
            else:
                self.response = cursor.fetchone()
            self.write_json()
        else:
            error = {"error": {"name": "Parameter invalid.","note":"Parameter invalid.","id_sensor_type":"Parameter invalid."}}
            self.write_error(status_code=400,message=error)

class SensorDataHandler(JsonHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self, sensor_id):
        try:
            sql = """SELECT dataperkey.id, dataperkey.value, dataperkey.id_sensor, dataperkey.timestamp, dataperkey.created FROM (
                SELECT
                  v.key as key, max(timestamp)
                FROM data, jsonb_each(data.value) as v
                WHERE id_sensor = %s GROUP BY v.key
                ) as lasttime JOIN (
                SELECT
                  id,jsonb_build_object(v.key, v.value) as value, v.key as key, id_sensor, timestamp, created
                FROM data, jsonb_each(data.value) as v
                WHERE id_sensor = %s
                ) as dataperkey ON lasttime.key = dataperkey.key WHERE lasttime.max = dataperkey.timestamp"""
            #sql = "SELECT * FROM data WHERE id_sensor = %s ORDER BY timestamp ASC LIMIT 100" #LIMIT 100
            cursor = yield self.db.execute(sql, (sensor_id,sensor_id,) , cursor_factory=RealDictCursor)
            cl = []
            for document in cursor.fetchall():
                cl.append(document)
            self.response = {'results':cl, 'id_sensor': sensor_id}
            self.write_json()
        except Exception as error:
            self.write_error(status_code=400,message={"error": error})


    @web.asynchronous
    @gen.coroutine
    def post(self, sensor_id):
        data = self.request.arguments
        sql = "INSERT INTO data(value, id_sensor, timestamp, created) VALUES(%s, %s, %s, %s) RETURNING id, value, id_sensor, timestamp, created;"
        print(data)
        value = data.get("value")
        if value is None:
            raise BaseException(reason='Value must be not None.', status_code=400)
        id_sensor = sensor_id
        timestamp = data.get("timestamp", datetime.datetime.utcnow())
        created = datetime.datetime.utcnow()
        try:
            cursor = yield self.application.db.execute(sql, (json.dumps(value),id_sensor,timestamp,created,) , cursor_factory=RealDictCursor)
        except (psycopg2.Warning, psycopg2.Error) as error:
            logging.error(error.pgerror)
            logging.error(error.diag.message_detail)
            raise BaseException(reason=error.diag.message_detail, status_code=400)
        else:
            fetch = cursor.fetchone()
            document = json_util.dumps(fetch)
            for client in [x for x in clients if x.sensor_id == sensor_id]:
                client.write_message(document)
            self.response = fetch
            self.write_json()

class SocketHandler(websocket.WebSocketHandler):
    @property
    def db(self):
        return self.application.db

    @gen.coroutine
    def do_find(self,sensor_id):
        sql = """SELECT dataperkey.id, dataperkey.value, dataperkey.id_sensor, dataperkey.timestamp, dataperkey.created FROM (
            SELECT
              v.key as key, max(timestamp)
            FROM data, jsonb_each(data.value) as v
            WHERE id_sensor = %s GROUP BY v.key
            ) as lasttime JOIN (
            SELECT
              id,jsonb_build_object(v.key, v.value) as value, v.key as key, id_sensor, timestamp, created
            FROM data, jsonb_each(data.value) as v
            WHERE id_sensor = %s
            ) as dataperkey ON lasttime.key = dataperkey.key WHERE lasttime.max = dataperkey.timestamp"""
        #sql = "SELECT * FROM data WHERE id_sensor = %s ORDER BY timestamp ASC LIMIT 100" #LIMIT 100
        cursor = yield self.db.execute(sql, (sensor_id,sensor_id,) , cursor_factory=RealDictCursor)
        cl = []
        for document in cursor.fetchall():
            cl.append(document)
        self.write_message(json_util.dumps({'results':cl, 'id_sensor': sensor_id}))


    def check_origin(self, origin):
        return True

    @gen.coroutine
    def open(self, sensor_id):
        self.sensor_id = sensor_id
        clients.add(self)
        #self.write_message(u"Id: " + sensor_id)
        yield self.do_find(sensor_id)

    @gen.coroutine
    def on_message(self, message):
        #self.write_message(u"You said: " + message)
        sql = "INSERT INTO data(value, id_sensor, timestamp, created) VALUES(%s, %s, %s, %s) RETURNING id, value, id_sensor, timestamp, created;"
        data = json.loads(message)
        if 'value' in data:
            value = data.get("value")
            id_sensor = self.sensor_id
            timestamp = data.get("timestamp", datetime.datetime.utcnow())
            created = datetime.datetime.utcnow()
            try:
                cursor = yield self.application.db.execute(sql, (json.dumps(value),id_sensor,timestamp,created,) , cursor_factory=RealDictCursor)
            except (psycopg2.Warning, psycopg2.Error) as error:
                logging.error(error.pgerror)
                logging.error(error.diag.message_detail)
                document = json_util.dumps({"error": {"message": error.diag.message_detail}})
            else:
                document = json_util.dumps(cursor.fetchone())
            for client in [x for x in clients if x.sensor_id == self.sensor_id]:
                client.write_message(document)

    def on_close(self):
        if self in clients:
            clients.remove(self)

def signal_handler(signum, frame):
    global is_closing
    logging.info('exiting...')
    is_closing = True

def try_exit():
    global is_closing
    if is_closing:
        # clean up here
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('exit success')

if __name__ == '__main__':
    options.parse_command_line()
    params = config()
    db_database = params.get('database','userdb')
    db_user = params.get('user', 'postgres')
    db_password = params.get('password', '')
    db_host = params.get('host', 'localhost')
    db_port = params.get('port', 5432)

    dsn = 'dbname=%s user=%s password=%s host=%s port=%s' % (
        db_database, db_user, db_password, db_host, db_port)

    assert (db_database or db_user or db_password or db_host or db_port) is not None, (
        'Please set the following '
        'variables: database, user, password, '
        'host, port in the database.ini file.')

    ioloop.PeriodicCallback(try_exit, 100).start()

    ioloop = ioloop.IOLoop.instance()

    app = web.Application([
        (r'/', IndexHandler),
        (r'/ws/(.*)', SocketHandler),
        #(r'/api', ApiHandler),
        (r'/api/sensors', SensorsHandler),
        (r'/api/sensor/([0-9]*)', SensorHandler),
        (r'/api/sensor/([0-9]*)/data', SensorDataHandler),
        (r'/api/sensortypes', SensorTypesHandler),
        (r'/api/sensortype/(.*)', SensorTypeHandler),
        (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
        (r'/(.*)', IndexReactStaticFileHandler, {'path': './build', 'default_filename': 'index.html'})
    ], debug=True)
    app.db = momoko.Pool(
        dsn=dsn,
        size=1,
        max_size=3,
        ioloop=ioloop,
        setsession=("SET TIME ZONE UTC",),
        raise_connect_errors=False,
    )
    print(app.db)

    future = app.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())

    ioloop.start()

    http_server = httpserver.HTTPServer(app)

    signal.signal(signal.SIGINT, signal_handler)
    http_server.listen(8888)

    ioloop.start()
