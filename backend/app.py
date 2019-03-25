from tornado import websocket, web, ioloop, gen, escape
import json
import motor.motor_tornado
from bson import json_util
import pprint
from django.core.serializers.json import DjangoJSONEncoder
from bson.objectid import ObjectId
import datetime

cl = []
clients = set()

class MongoAwareEncoder(DjangoJSONEncoder):
    """JSON encoder class that adds support for Mongo objectids."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return super(MongoAwareEncoder, self).default(o)

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    @gen.coroutine
    def do_find(self,sensor_id):
        db = self.settings['db']
        cursor = db.data.find({'sensor_id': ObjectId(sensor_id)})
        cl = []
        for document in (yield cursor.to_list(length=100)):
            cl.append(document)
        self.write_message(json_util.dumps({'results':cl, 'sensor_id': sensor_id}))

    @gen.coroutine
    def do_count(self):
        db = self.settings['db']
        n = yield db.data.find().count()
        self.write_message(json_util.dumps({'count':n}))

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def open(self, sensor_id):
        self.sensor_id = sensor_id
        clients.add(self)
        self.write_message(u"Id: " + sensor_id)
        yield self.do_count()
        yield self.do_find(sensor_id)

    @gen.coroutine
    def on_message(self, message):
        self.write_message(u"You said: " + message)
        res = yield db.data.insert_one({'sensor_id': ObjectId(self.sensor_id), 'value': float(message), 'created': datetime.datetime.utcnow()})
        document = yield db.data.find_one({'_id': ObjectId(res.inserted_id)})
        for client in [x for x in clients if x.sensor_id == self.sensor_id]:
            client.write_message(json_util.dumps({'result': document}))

    def on_close(self):
        if self in clients:
            clients.remove(self)

class SensorsHandler(web.RequestHandler):
    def each(self, message, error):
        if error:
            raise error
        elif message:
            cl.append(message)
        else:
            # Iteration complete
            print('done')
            print(str(cl))
            self.write(json_util.dumps({'results':cl}))
            self.finish()


    @web.asynchronous
    def get(self):
        global cl
        db = self.settings['db']
        self.set_header('Content-Type', 'application/json')
        cl = []
        db.sensor.find({}).each(self.each)

    @web.asynchronous
    @gen.coroutine
    def post(self):
        data = escape.json_decode(self.request.body)
        res = yield db.sensor.insert_one(data)
        document = yield db.sensor.find_one({'_id': ObjectId(res.inserted_id)})
        self.write(json_util.dumps({'result': document}))

class SensorHandler(web.RequestHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self, sensor_id):
        db = self.settings['db']
        self.set_header('Content-Type', 'application/json')
        res = yield db.sensor.find_one({'_id': ObjectId(sensor_id)})
        self.write(json_util.dumps({'result': res}))

    @web.asynchronous
    @gen.coroutine
    def patch(self, sensor_id):
        #name = self.get_argument('name')
        data = escape.json_decode(self.request.body)
        #print(data)
        #print(json.loads(self.request.body.decode('utf-8')))
        res = yield db.sensor.update_one({'_id': ObjectId(sensor_id)}, {'$set': data})
        self.write(json_util.dumps({'count': res.modified_count}))


class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self):
        pass

client = motor.motor_tornado.MotorClient()
db = client.iot

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws/(.*)', SocketHandler),
    (r'/api', ApiHandler),
    (r'/sensors', SensorsHandler),
    (r'/sensor/(.*)', SensorHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'})
], db=db)

if __name__ == '__main__':
    client = motor.motor_tornado.MotorClient('localhost', 27017)
    db = client.iot
    print(db)
    app.listen(8888)
    ioloop.IOLoop.instance().start()
