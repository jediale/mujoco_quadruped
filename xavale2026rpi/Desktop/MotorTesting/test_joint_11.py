# test_2- created 5/18/26

# new motor testing doc, quick by-id individual run

bus = 4
id = 11
servo_bus_map={bus: [id]}

import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # Set up the pi3hat transport — adjust bus and ID to match your wiring
    transport = moteus_pi3hat.Pi3HatRouter(servo_bus_map)  # CAN bus 1, controller ID 1

    controller = moteus.Controller(id=id, transport=transport)

    # Always stop first to clear any fault state
    await controller.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state = await controller.set_stop(query=True)
    starting_position = state.values[moteus.Register.POSITION]

    print(f"DEBUG: Starting position = {starting_position}")
    print(f"DEBUG: Will command positions from {starting_position - 1.0} to {starting_position + 1.0}")

    # Then wait a moment before starting
    await asyncio.sleep(1.0)

    print(f"Starting position control test loop for motor {servo_bus_map[bus]}")

    try:
        N = 1 # this will be the number of periods
        for i in range(200):
            
            # # Velocity state 
            # state = await controller.set_position(
            #     velocity=math.sin(N*2*math.pi*i/200),
            #     position=math.nan,      
            #     maximum_torque=1.0, 
            #     query=True
            # )


            # Position state 
            state = await controller.set_position(
                position=starting_position + math.sin(N*2*math.pi*i/200),
                velocity=math.nan,      
                maximum_torque= 1.0, 
                query=True
            )

            if state:
                print(
                    f"mode={state.values[moteus.Register.MODE]} "
                    f"pos={state.values[moteus.Register.POSITION]:.3f} "
                    f"vel={state.values[moteus.Register.VELOCITY]:.3f} "
                    f"torque={state.values[moteus.Register.TORQUE]:.3f} "
                    f"fault={state.values[moteus.Register.FAULT]}"
                )
            await asyncio.sleep(0.02)  # 50 Hz loop

    finally:
        # Always stop the motor cleanly
        print("Stopping...")
        await controller.set_stop()

asyncio.run(main())

