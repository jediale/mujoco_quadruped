import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1, 2]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_1 = moteus.Controller(id=1, transport=transport)
    controller_2 = moteus.Controller(id=2, transport=transport)

    # 3. Stop both to clear faults
    await controller_1.set_stop()
    await controller_2.set_stop()
    await asyncio.sleep(0.5)

    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            velocity_cmd_2 = 1.5 * math.sin(N * 2 * math.pi * i / 200)
            velocity_cmd_1 = 1.5 * math.sin(N * 2 * math.pi * i / 200 + math.pi/2)
            
            # 4. Use transport.cycle to send both commands in one CAN frame (more efficient)
            # Or just await them sequentially:
            state_1 = await controller_1.set_position(
                position=math.nan,
                velocity=velocity_cmd_1,
                maximum_torque=1.0,
                query=True
            )
            
            state_2 = await controller_2.set_position(
                position=math.nan,
                velocity=velocity_cmd_2,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_1 and state_2:
                print(f"C1 Vel: {state_1.values[moteus.Register.VELOCITY]:.2f} | "
                      f"C3 Vel: {state_2.values[moteus.Register.VELOCITY]:.2f}")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_1.set_stop()
        await controller_2.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
