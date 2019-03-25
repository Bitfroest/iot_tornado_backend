import asyncio
import websockets    # package to open websockets
import requests     # package for HTTP requests
import json

wsAddress = "ws://localhost:8888/ws/1"

async def hello():
    async with websockets.connect(
            wsAddress) as websocket:
        name = json.dumps({'value': {'battery': 0.35}})

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
