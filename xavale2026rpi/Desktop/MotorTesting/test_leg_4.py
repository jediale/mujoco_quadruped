import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={4: [10,11,12]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_10 = moteus.Controller(id=10, transport=transport)
    controller_11 = moteus.Controller(id=11, transport=transport)
    controller_12 = moteus.Controller(id=12, transport=transport)

    # 3. Stop both to clear faults
    await controller_10.set_stop()
    await controller_11.set_stop()
    await controller_12.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_10 = await controller_10.set_stop(query=True)  # or use set_position with query=True
    starting_position_10 = state_10.values[moteus.Register.POSITION]

    state_11= await controller_11.set_stop(query=True)  # or use set_position with query=True
    starting_position_11 = state_11.values[moteus.Register.POSITION]

    state_12 = await controller_12.set_stop(query=True)  # or use set_position with query=True
    starting_position_12 = state_12.values[moteus.Register.POSITION]

    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_10 = await controller_10.set_position(
                position=starting_position_10 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_11 = await controller_11.set_position(
                position=starting_position_11 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_12 = await controller_12.set_position(
                position=starting_position_12 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_10 and state_11 and state_12:
                print(f"  C10 Pos: {state_10.values[moteus.Register.POSITION]:.2f} | "
                      f"  C11 Pos: {state_11.values[moteus.Register.POSITION]:.2f} | "
                       f"  C12 Pos: {state_12.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_10.set_stop()
        await controller_11.set_stop()
        await controller_12.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
