

async def main():




            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_1.set_stop()
        await controller_2.set_stop()
        await controller_3.set_stop()
        await controller_4.set_stop()
        await controller_5.set_stop()
        await controller_6.set_stop()
        await controller_7.set_stop()
        await controller_8.set_stop()
        await controller_9.set_stop()
        await controller_10.set_stop()
        await controller_11.set_stop()
        await controller_12.set_stop()

#

import math
import moteus
import moteus_pi3hat
import asyncio
import websockets
import json
import time
from datetime import datetime

async def initialize_motors():
    """Setup all 12 motors across 4 buses"""
    global controllers, starting_positions
    global motor_ids = list(range(1, 13))
    global positions = [0]*12
    
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }, 
    )

    
    controllers = {mid: moteus.Controller(id=mid, transport=transport) for mid in motor_ids}

    print("Stopping all motors...")
    for mid in motor_ids:
        try:
            await asyncio.wait_for(controllers[mid].set_stop(), timeout=3.0)
            print(f"Motor {mid} stopped")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"ERROR stopping motor {mid}: {e}")
    
    await asyncio.sleep(1.0)

    print("Querying starting positions...")
    for mid in motor_ids:
        try:
            state = await asyncio.wait_for(
                controllers[mid].set_position(position=math.nan, query=True),
                timeout=3.0
            )
            starting_positions[mid] = state.values[moteus.Register.POSITION]
            positions[mid] = starting_positions[mid]
            print(f"Motor {mid}: {starting_positions[mid]:.2f}")
            await asyncio.sleep(0.2)
        except Exception as e:
            print(f"ERROR querying motor {mid}: {e}")
            starting_positions[mid] = 0.0
            positions[mid] = 0.0

async def handle_client(websocket):
    print("Laptop connected")
    try:
        async for message in websocket:
            data = json.loads(message)
            packet = data.get('packet', [])
            state = data.get('state', 'still')
            
            print(f"Received - Packet: {packet}, State: {state}")

            for mid in motor_ids:
                state = await asyncio.wait_for(
                    controllers[mid].set_position(position=math.nan, query=True),
                    timeout=3.0
                )
                positions[mid] = state.values[moteus.Register.POSITION]
            
            # Generate response with current timestamp and mock motor positions
            response = {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'received_packet': packet,
                'received_state': state,
                'motor_positions': positions,
                'temperature': 45.2,
                'server_time': time.time()
            }
            
            await websocket.send(json.dumps(response))
            print(f"Sent response at {response['timestamp']}")
            
    except Exception as e:
        print(f"Error: {e}")

async def main():

    print("Initializing 12 motors...")
    await initialize_motors()

    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())