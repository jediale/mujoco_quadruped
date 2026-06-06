import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1], 2:[4], 3:[7], 4:[10]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_1 = moteus.Controller(id=1, transport=transport)
    controller_4 = moteus.Controller(id=4, transport=transport)
    controller_7 = moteus.Controller(id=7, transport=transport)
    controller_10 = moteus.Controller(id=10, transport=transport)

    # 3. Stop both to clear faults
    await controller_1.set_stop()
    await controller_4.set_stop()
    await controller_7.set_stop()
    await controller_10.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_1 = await controller_1.set_stop(query=True)  # or use set_position with query=True
    starting_position_1 = state_1.values[moteus.Register.POSITION]

    state_4 = await controller_4.set_stop(query=True)  # or use set_position with query=True
    starting_position_4 = state_4.values[moteus.Register.POSITION]

    state_7 = await controller_7.set_stop(query=True)  # or use set_position with query=True
    starting_position_7 = state_7.values[moteus.Register.POSITION]

    state_10 = await controller_10.set_stop(query=True)  # or use set_position with query=True
    starting_position_10 = state_10.values[moteus.Register.POSITION]


    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_1 = await controller_1.set_position(
                position=starting_position_1 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_4 = await controller_4.set_position(
                position=starting_position_4 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_7 = await controller_7.set_position(
                position=starting_position_7 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_10 = await controller_10.set_position(
                position=starting_position_10 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_1 and state_4 and state_7 and state_10:
                print(f"  C1 Pos: {state_1.values[moteus.Register.POSITION]:.2f} | "
                      f"  C4 Pos: {state_4.values[moteus.Register.POSITION]:.2f} | "
                       f"  C7 Pos: {state_7.values[moteus.Register.POSITION]:.2f} | "
                        f"  C10 Pos: {state_10.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_1.set_stop()
        await controller_4.set_stop()
        await controller_7.set_stop()
        await controller_10.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
