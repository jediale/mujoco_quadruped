import asyncio
import websockets
import json

async def handle_client(websocket):
    print("Laptop connected")
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received from laptop: {data}")
            
            # Process the packet and state
            # e.g., send motor commands, run calibration
            
            # Send response back
            response = {
                'status': 'ok',
                'received': data,
                'motor_positions': [10.5, 20.3, 15.1],  # Example: real sensor data
                'temperature': 45.2
            }
            await websocket.send(json.dumps(response))
            print(f"Sent to laptop: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())