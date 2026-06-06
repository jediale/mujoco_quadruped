# keep 2 the same on this end, add MuJoCo Coverage on laptop

# will have a homing sequence in here

# NOTE actuation is off for homing and for tracking right now

import asyncio
import websockets
import json
import time
from datetime import datetime
import moteus
import moteus_pi3hat
import math

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
    
    # 5. I'll have to add an initialization homing sequence here... (NOTE UNCOMMENT TS)

    print("Homing...")
    old_deltas = [0, -0.7, 3.7, 0, -1.1, -4.1, 0, 0.8, -4.0, 0, 1, -1.8]
    deltas = [0, 1.7, -3.7, 0, 2.1, 4.1, 0, -0.8, 3.5, 0, -1, 1.8] #negated / flipped and tuned
    starts = list(positions)

    targets = [
        starts[0] + deltas[0],
        starts[1] + 1.6*deltas[1],
        starts[2] + 1.1*deltas[2],
        starts[3] - deltas[3],
        starts[4] - 1.3*deltas[4],
        starts[5] + 1.3*deltas[5],
        starts[6] + deltas[6],
        starts[7] + 2.2*deltas[7],
        starts[8] + 2.5*deltas[8],
        starts[9] - deltas[9],
        starts[10] - 2.5*deltas[10],
        starts[11] - 2.3*deltas[11]
    ]

    # -------------------------------------------------------------------------
    # 📈 GENERATE 200-STEP INTERPOLATED TRAJECTORY MATRIX
    # -------------------------------------------------------------------------
    STEPS = 200
    trajectory = []
    
    for step_idx in range(STEPS):
        # Calculate interpolation factor tracking linearly from 0.0 to 1.0
        alpha = step_idx / (STEPS - 1)
        
        # Linear interpolation formula: start + alpha * (target - start)
        step_positions = [
            starts[m_idx] + alpha * (targets[m_idx] - starts[m_idx])
            for m_idx in range(12)
        ]
        trajectory.append(step_positions)

    print(f"Generated trajectory profile. Total micro-steps: {len(trajectory)}")
    print("Starting streaming trajectory control loop...")
    
    
        # Loop through each calculated slice sequentially (NOTE this is where we uncomment)
    for step_idx, targets_slice in enumerate(trajectory):
        homing_tasks = [controllers[i].set_position(position = targets_slice[i-1], velocity = math.nan, maximum_torque=1.5,query=True) for i in range(1,13)]
        await asyncio.gather(*homing_tasks)
        # Pass the interpolated slice values down the serial command
        await asyncio.sleep(0.005)

    # give it some time...
    await asyncio.sleep(10)

    
    # 6.  Query homed positions NOTE: there is a commented out section that does NOT need to come back
    # for i in range(1, 13):
    #     state = await controllers[i].set_stop(query=True)
    #     positions[i-1] = state.values[moteus.Register.POSITION]
    motor_results = await asyncio.gather(*[controllers[i].set_position(query=True) for i in range(1, 13)])
    positions = [state.values[moteus.Register.POSITION] for state in motor_results]

    print(f"Homed Positions: {positions}")

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


                # RESPOND (THINK) -> Fetch fresh data from the motors! Command!

                motor_tasks=[]

                # in init, just read / query
                if state_msg == "init":     
                    for i in range(1, 13):
                            task = controllers[i].set_position(query=True)
                            motor_tasks.append(task)

                # control + sim
                else:
                    # Check if we received a valid 12-motor packet
                    if len(packet) == 12:
                        for i in range(1, 13):
                            # Construct a task that COMMANDS a position AND QUERIES the telemetry
                            task = controllers[i].set_position(
                                position=packet[i-1], 
                                velocity=0.0,              # Adjust if you want feedforward velocity
                                maximum_torque=1.5,        # Safe operation limit
                                query=True                 # Returns current telemetry
                            )
                            motor_tasks.append(task)
                    else:
                        # Fallback: If packet is empty or wrong size, just query current positions safely
                        for i in range(1, 13):
                            task = controllers[i].set_position(query=True)
                            motor_tasks.append(task)
                    # Fire all commands down the CAN lines simultaneously
                motor_results = await asyncio.gather(*motor_tasks)
                # Extract the updated positions from the responses
                for i, motor_state in enumerate(motor_results):
                    positions[i] = motor_state.values[moteus.Register.POSITION]

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