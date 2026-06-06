import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [2], 2:[5], 3:[8], 4:[11]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_2 = moteus.Controller(id=2, transport=transport)
    controller_5 = moteus.Controller(id=5, transport=transport)
    controller_8 = moteus.Controller(id=8, transport=transport)
    controller_11 = moteus.Controller(id=11, transport=transport)

    # 3. Stop both to clear faults
    await controller_2.set_stop()
    await controller_5.set_stop()
    await controller_8.set_stop()
    await controller_11.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_2 = await controller_2.set_stop(query=True)  # or use set_position with query=True
    starting_position_2 = state_2.values[moteus.Register.POSITION]

    state_5 = await controller_5.set_stop(query=True)  # or use set_position with query=True
    starting_position_5 = state_5.values[moteus.Register.POSITION]

    state_8 = await controller_8.set_stop(query=True)  # or use set_position with query=True
    starting_position_8 = state_8.values[moteus.Register.POSITION]

    state_11 = await controller_11.set_stop(query=True)  # or use set_position with query=True
    starting_position_11 = state_11.values[moteus.Register.POSITION]


    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_2 = await controller_2.set_position(
                position=starting_position_2 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_5 = await controller_5.set_position(
                position=starting_position_5 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_8 = await controller_8.set_position(
                position=starting_position_8 + command,
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

            # Optional: Print status for both
            if state_2 and state_5 and state_8 and state_11:
                print(f"  C2 Pos: {state_2.values[moteus.Register.POSITION]:.2f} | "
                      f"  C5 Pos: {state_5.values[moteus.Register.POSITION]:.2f} | "
                       f"  C8 Pos: {state_8.values[moteus.Register.POSITION]:.2f} | "
                        f"  C11 Pos: {state_11.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_2.set_stop()
        await controller_5.set_stop()
        await controller_8.set_stop()
        await controller_11.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
