import asyncio
import websockets
import json

async def send_and_receive(host, port, data):
    uri = f"ws://{host}:{port}"
    try:
        async with websockets.connect(uri) as websocket:
            # Send data to pi
            await websocket.send(json.dumps(data))
            print(f"Sent to pi: {data}")
            
            # Receive response from pi
            response = await websocket.recv()
            print(f"Received from pi: {response}")
            return json.loads(response)
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    data = {'packet': [1, 2, 3], 'state': 'forward'}
    result = await send_and_receive('localhost', 8765, data)
    if result:
        print(f"Motor positions: {result.get('motor_positions')}")
        print(f"Temperature: {result.get('temperature')}")

if __name__ == "__main__":
    asyncio.run(main())