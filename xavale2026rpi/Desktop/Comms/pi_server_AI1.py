import asyncio
import websockets
import json
import time
from datetime import datetime
import moteus
import moteus_pi3hat

# Thread-safe/Global tracking list
positions = [0.0] * 12

# Global references for controllers so handle_client can access them
controllers = {}

async def main():
    global positions, controllers

    # 1. Setup transport for all buses
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3], 2:[4,5,6], 3: [7,8,9], 4:[10,11,12]}, 
    )

    # 2. Instantiate ALL 12 controllers dynamically
    for id_num in range(1, 13):
        controllers[id_num] = moteus.Controller(id=id_num, transport=transport)

    # 3. Stop all to clear faults simultaneously
    # (By creating tasks, they send commands concurrently rather than waiting one-by-one)
    stop_tasks = [controllers[i].set_stop() for i in range(1, 13)]
    await asyncio.gather(*stop_tasks)
    await asyncio.sleep(0.5)

    # 4. Query initial positions
    for i in range(1, 13):
        state = await controllers[i].set_stop(query=True)
        positions[i-1] = state.values[moteus.Register.POSITION]

    print(f"Initial Positions: {positions}")
    print("Initialization Complete")

    # 5. Nested client handler to easily access initialized controllers
    async def handle_client(websocket):
        print("Laptop connected")
        try:
            async for message in websocket:
                # RECEIVING (SENSE)
                data = json.loads(message)
                packet = data.get('packet', [])
                state_msg = data.get('state', 'still')
                
                print(f"Received - Packet: {packet}, State: {state_msg}")

                # RESPOND (THINK) -> Fetch fresh data from the motors!
                # Note: Querying 12 motors one-by-one can take a few milliseconds.
                for i in range(1, 13):
                    # Querying via set_position with no movement targets acts as a query.
                    # Adjust if you intend to send commands here based on the 'packet' data.
                    motor_state = await controllers[i].set_position(query=True)
                    positions[i-1] = motor_state.values[moteus.Register.POSITION]

                # SENDING (ACT)
                response = {
                    'timestamp': datetime.now().isoformat(),
                    'received_packet': packet,
                    'received_state': state_msg,
                    'motor_positions': positions,
                    'server_time': time.time()
                }
                
                await websocket.send(json.dumps(response))
                print(f"Sent response at {response['timestamp']}")
                
        except websockets.exceptions.ConnectionClosedOK:
            print("Laptop disconnected safely.")
        except Exception as e:
            print(f"Error in websocket loop: {e}")

    # 6. Start the network listener
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        # Keeps the server running indefinitely
        await asyncio.Future() 

if __name__ == "__main__":
    # One unified entry point for the event loop
    asyncio.run(main())