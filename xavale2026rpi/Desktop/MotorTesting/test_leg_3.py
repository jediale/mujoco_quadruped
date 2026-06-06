import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={3: [7,8,9]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_7 = moteus.Controller(id=7, transport=transport)
    controller_8 = moteus.Controller(id=8, transport=transport)
    controller_9 = moteus.Controller(id=9, transport=transport)

    # 3. Stop both to clear faults
    await controller_7.set_stop()
    await controller_8.set_stop()
    await controller_9.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_7 = await controller_7.set_stop(query=True)  # or use set_position with query=True
    starting_position_7 = state_7.values[moteus.Register.POSITION]

    state_8= await controller_8.set_stop(query=True)  # or use set_position with query=True
    starting_position_8 = state_8.values[moteus.Register.POSITION]

    state_9 = await controller_9.set_stop(query=True)  # or use set_position with query=True
    starting_position_9 = state_9.values[moteus.Register.POSITION]

    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_7 = await controller_7.set_position(
                position=starting_position_7 + command,
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

            state_9 = await controller_9.set_position(
                position=starting_position_9 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_7  and state_8 and state_9:
            # if state_8 and state_9:
            # if state_9:
                print(f"  C7 Pos: {state_7.values[moteus.Register.POSITION]:.2f} | "
                      f"  C8 Pos: {state_8.values[moteus.Register.POSITION]:.2f} | "
                       f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} | ")

                # print(f"  C8 Pos: {state_8.values[moteus.Register.POSITION]:.2f} | "
                #         f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} | ")

                # print(f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_7.set_stop()
        await controller_8.set_stop()
        await controller_9.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
