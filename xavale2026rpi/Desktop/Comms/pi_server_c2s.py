import asyncio
import websockets
import json

async def handle_client(websocket):
    print("Laptop connected")
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
            
            # Do something with the data
            # e.g., command motors, run calibration, etc.
            
            # Send response back
            response = {'status': 'ok', 'received': data}
            await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())