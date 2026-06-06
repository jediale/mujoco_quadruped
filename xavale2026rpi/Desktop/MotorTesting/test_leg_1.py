import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_1 = moteus.Controller(id=1, transport=transport)
    controller_2 = moteus.Controller(id=2, transport=transport)
    controller_3 = moteus.Controller(id=3, transport=transport)

    # 3. Stop both to clear faults
    await controller_1.set_stop()
    await controller_2.set_stop()
    await controller_3.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_1 = await controller_1.set_stop(query=True)  # or use set_position with query=True
    starting_position_1 = state_1.values[moteus.Register.POSITION]

    state_2 = await controller_2.set_stop(query=True)  # or use set_position with query=True
    starting_position_2 = state_2.values[moteus.Register.POSITION]

    state_3 = await controller_3.set_stop(query=True)  # or use set_position with query=True
    starting_position_3 = state_3.values[moteus.Register.POSITION]

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
            
            state_2 = await controller_2.set_position(
                position=starting_position_2 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_3 = await controller_3.set_position(
                position=starting_position_3 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_1 and state_2 and state_3:
                print(f"  C1 Pos: {state_1.values[moteus.Register.POSITION]:.2f} | "
                      f"  C4 Pos: {state_2.values[moteus.Register.POSITION]:.2f} | "
                       f"  C7 Pos: {state_3.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_1.set_stop()
        await controller_2.set_stop()
        await controller_3.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
