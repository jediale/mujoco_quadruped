import asyncio
import websockets
import json
import time
from datetime import datetime

# this happens when the network connection is established. main loop stuff! no need for initialization or anything here
async def handle_client(websocket):
    print("Laptop connected")
    try:
        # data-driven loop that runs ONLY when data is received from the laptop
        async for message in websocket:

            # this decodes the json message
            data = json.loads(message)
            # packet is an array
            packet = data.get('packet', [])
            # state is a string but only 'still'?
            state = data.get('state', 'still')
            
            print(f"Received - Packet: {packet}, State: {state}")
            
            # Generate response -> this is information that will be sent, and this is where we want to query the current positions of the motors. 
            
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'received_packet': packet,
                'received_state': state,
                'motor_positions': [
                    10.5 + packet[0] * 0.1,  # Mock position based on packet[0]
                    20.3 + packet[1] * 0.1,
                    15.1 + packet[2] * 0.1,
                    25.0 + packet[3] * 0.1,
                    30.2 + packet[4] * 0.1,
                    18.7 + packet[5] * 0.1,
                    22.4 + packet[6] * 0.1,
                    19.9 + packet[7] * 0.1,
                    24.1 + packet[8] * 0.1,
                    21.5 + packet[9] * 0.1,
                    23.3 + packet[10] * 0.1,
                    20.8 + packet[11] * 0.1,
                ],
                'temperature': 45.2,
                'server_time': time.time()
            }
            
            await websocket.send(json.dumps(response))
            print(f"Sent response at {response['timestamp']}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # creates the network listener
    async with websockets.serve(handle_client, "localhost", 8765):
        # waits until the laptop connects. when someone does, it triggers "handle_client()"
        print("Server running on ws://localhost:8765")
        await asyncio.Future()


# "main loop" - I can probably run this affter intitialization sequences
asyncio.run(main())