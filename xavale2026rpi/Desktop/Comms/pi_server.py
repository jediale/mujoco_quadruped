import asyncio
import websockets
import json
import time
from datetime import datetime
import math
import moteus
import moteus_pi3hat

positions = [0]*12

async def pre_loop():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3], 2:[4,5,6], 3: [7,8,9], 4:[10,11,12]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_1 = moteus.Controller(id=1, transport=transport)
    controller_2 = moteus.Controller(id=2, transport=transport)
    controller_3 = moteus.Controller(id=3, transport=transport)
    controller_4 = moteus.Controller(id=4, transport=transport)
    controller_5 = moteus.Controller(id=5, transport=transport)
    controller_6 = moteus.Controller(id=6, transport=transport)
    controller_7 = moteus.Controller(id=7, transport=transport)
    controller_8 = moteus.Controller(id=8, transport=transport)
    controller_9 = moteus.Controller(id=9, transport=transport)
    controller_10 = moteus.Controller(id=10, transport=transport)
    controller_11 = moteus.Controller(id=11, transport=transport)
    controller_12 = moteus.Controller(id=12, transport=transport)

    # 3. Stop both to clear faults
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
    await asyncio.sleep(0.5)

    # Query the current position and store in the positions list
    state_1 = await controller_1.set_stop(query=True)  # or use set_position with query=True
    starting_position_1 = state_1.values[moteus.Register.POSITION]
    positions[0] = starting_position_1

    state_2 = await controller_2.set_stop(query=True)  # or use set_position with query=True
    starting_position_2 = state_2.values[moteus.Register.POSITION]
    positions[1] = starting_position_2

    state_3 = await controller_3.set_stop(query=True)  # or use set_position with query=True
    starting_position_3 = state_3.values[moteus.Register.POSITION]
    positions[2] = starting_position_3

    state_4 = await controller_4.set_stop(query=True)  # or use set_position with query=True
    starting_position_4 = state_4.values[moteus.Register.POSITION]
    positions[3] = starting_position_4

    state_5= await controller_5.set_stop(query=True)  # or use set_position with query=True
    starting_position_5 = state_5.values[moteus.Register.POSITION]
    positions[4] = starting_position_5

    state_6 = await controller_6.set_stop(query=True)  # or use set_position with query=True
    starting_position_6 = state_6.values[moteus.Register.POSITION]
    positions[5] = starting_position_6

    state_7 = await controller_7.set_stop(query=True)  # or use set_position with query=True
    starting_position_7 = state_7.values[moteus.Register.POSITION]
    positions[6] = starting_position_7

    state_8= await controller_8.set_stop(query=True)  # or use set_position with query=True
    starting_position_8 = state_8.values[moteus.Register.POSITION]
    positions[7] = starting_position_8

    state_9 = await controller_9.set_stop(query=True)  # or use set_position with query=True
    starting_position_9 = state_9.values[moteus.Register.POSITION]
    positions[8] = starting_position_9

    state_10 = await controller_10.set_stop(query=True)  # or use set_position with query=True
    starting_position_10 = state_10.values[moteus.Register.POSITION]
    positions[9] = starting_position_10

    state_11= await controller_11.set_stop(query=True)  # or use set_position with query=True
    starting_position_11 = state_11.values[moteus.Register.POSITION]
    positions[10] = starting_position_11

    state_12 = await controller_12.set_stop(query=True)  # or use set_position with query=True
    starting_position_12 = state_12.values[moteus.Register.POSITION]
    positions[11] = starting_position_12

    print(f"Initial Positions: {positions}")
    print("Initialization Complete")


# this happens when the network connection is established. main loop stuff! no need for initialization or anything here
async def handle_client(websocket):
    print("Laptop connected")
    try:
        # data-driven loop that runs ONLY when data is received from the laptop
        async for message in websocket:

            # RECEIVING (SENSE)

            # this decodes the json message
            data = json.loads(message)
            # packet is an array
            packet = data.get('packet', [])
            # state is a string but only 'still'?
            state = data.get('state', 'still')
            
            print(f"Received - Packet: {packet}, State: {state}")

            # RESPOND (THINK)

            # Optional: Print status for both
            positions[0]=state_1.values[moteus.Register.POSITION]
            positions[1]=state_2.values[moteus.Register.POSITION]
            positions[2]=state_3.values[moteus.Register.POSITION]
            positions[3]=state_4.values[moteus.Register.POSITION]
            positions[4]=state_5.values[moteus.Register.POSITION]
            positions[5]=state_6.values[moteus.Register.POSITION]
            positions[6]=state_7.values[moteus.Register.POSITION]
            positions[7]=state_8.values[moteus.Register.POSITION]
            positions[8]=state_9.values[moteus.Register.POSITION]
            positions[9]=state_10.values[moteus.Register.POSITION]
            positions[10]=state_11.values[moteus.Register.POSITION]
            positions[11]=state_12.values[moteus.Register.POSITION]

            # SENDING (ACT)
            
            # Generate response -> this is information that will be sent, and this is where we want to query the current positions of the motors. 
            
            # all of the data sent over

            # ngl, it is crucial that all data be in here on both ends... this is because the only screen that will be available will be on the laptop, 
            # so if I want to confirm anything abotut the data on the motors, for example, or on the pi, then I need to see what it's sending and receiving
            # at the same time, so on the laptop I will be able to show what the received motor positions are and the data that I am sending, as well as what the rpi is receiving?

            response = {
                'timestamp': datetime.now().isoformat(),
                'received_packet': packet,
                'received_state': state,
                'motor_positions': positions,
                'server_time': time.time()
            }
            
            # this actually sends it over! then we go up to the top of the loop and wait again
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


# "pre-communication loop" - initialize all of the motors
asyncio.run(pre_loop())

# "main loop" - I can probably run this affter intitialization sequences
asyncio.run(main())