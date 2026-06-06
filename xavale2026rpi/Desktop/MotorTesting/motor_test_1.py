# motor_test_1 - created 4/2/26

# first motor testing doc

# update log:

# 4/2/26

# gotta run these in the terminal before running

# # Create a venv (recommended, keeps things tidy)
# python -m venv --system-site-packages moteus-venv
# source moteus-venv/bin/activate

# # Install both — moteus is the API, moteus-pi3hat is the transport layer
# pip install moteus moteus-pi3hat

# then I pasted the main body from claude

# 4/5/26

# I'm playing around with the velocity limit, but it looks good!

# I tried the position controller and didn't like that very much, 
# it's still shaky but that's on the calibration side - velocity control
# looks really, really good


# code:

servo_bus_map = {1: [3]}  # CAN bus 1 → controller ID 1
# I changed to 2 because I moved motors, but the key is the CAN bus, and the value is the list wiht the controller IDs on the CAN bus, so I could daisy chain


# the script controls the velocity at 2!
import asyncio
import math
import moteus
import moteus_pi3hat


async def main():
    # Set up the pi3hat transport — adjust bus and ID to match your wiring
    transport = moteus_pi3hat.Pi3HatRouter(
        #servo_bus_map={1: [1]},  # CAN bus 1, controller ID 1
        servo_bus_map={1: [2]},  # CAN bus 1, controller ID 2
        # servo_bus_map={1: [3]},  # CAN bus 1, controller ID 3
    )

    controller = moteus.Controller(id=2, transport=transport)

    # Always stop first to clear any fault state
    await controller.set_stop()
    await asyncio.sleep(0.5)

    print("Starting position control loop...")
    try:
        N = 2 # this will be the number of periods
        for i in range(200):
            # Spin at 0.5 rev/s, no fixed position target (nan = velocity mode via position interface)
            #state = await controller.set_position(
            #    position=math.nan,
            #    velocity=1.5*math.sin(N*2*math.pi*i/200),         # faster
            #    maximum_torque=1.0,   # more torque
            #    query=True
            #)

            # fixed velocity (caused a fault 102)
            # state = await controller.set_position(
            #     position=math.nan,
            #     velocity=1,        # faster
            #     maximum_torque=1.0,   # more torque
            #     query=True
            # )

            
            # Position state - not really great
            state = await controller.set_position(
                position=math.sin(N*2*math.pi*i/200),
                velocity=math.nan,         # faster
                maximum_torque=1.0,   # more torque
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

