import asyncio
import moteus
import math

async def main():
    c = moteus.Controller()

    print("Applying open-loop voltage...")

    while True:
        await c.set_position(
            position=math.nan,     # do not use position loop
            velocity=0.0,
            kp_scale=0.0,          # disable position control
            kd_scale=0.0,          # disable velocity control
            feedforward_torque=0.2,  # <-- this applies torque
            maximum_torque=0.3,
            query=False,
        )

asyncio.run(main())


