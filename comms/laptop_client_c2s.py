import asyncio
import websockets
import json

async def send_command(host, port, data):
    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(data))
        response = await websocket.recv()
        print(f"Response: {response}")
        return json.loads(response)

# Example usage
async def main():
    data = {'packet': [1, 2, 3], 'state': 'forward'}
    await send_command('localhost', 8765, data)

asyncio.run(main())