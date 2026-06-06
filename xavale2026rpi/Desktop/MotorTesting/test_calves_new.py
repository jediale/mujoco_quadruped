import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3], 2:[4,5,6], 3:[7,8,9], 4:[10,11,12]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_3 = moteus.Controller(id=3, transport=transport)
    controller_6 = moteus.Controller(id=6, transport=transport)
    controller_9 = moteus.Controller(id=9, transport=transport)
    controller_12 = moteus.Controller(id=12, transport=transport)

    # 3. Stop both to clear faults
    await controller_3.set_stop()
    await controller_6.set_stop()
    await controller_9.set_stop()
    await controller_12.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_3 = await controller_3.set_stop(query=True)  # or use set_position with query=True
    starting_position_3 = state_3.values[moteus.Register.POSITION]

    state_6 = await controller_6.set_stop(query=True)  # or use set_position with query=True
    starting_position_6 = state_6.values[moteus.Register.POSITION]

    state_9 = await controller_9.set_stop(query=True)  # or use set_position with query=True
    starting_position_9 = state_9.values[moteus.Register.POSITION]

    state_12 = await controller_12.set_stop(query=True)  # or use set_position with query=True
    starting_position_12 = state_12.values[moteus.Register.POSITION]


    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_3 = await controller_3.set_position(
                position=starting_position_3 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_6 = await controller_6.set_position(
                position=starting_position_6 + command,
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

            state_12 = await controller_12.set_position(
                position=starting_position_12 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_3 and state_6 and state_9 and state_12:
                print(f"  C3 Pos: {state_3.values[moteus.Register.POSITION]:.2f} | "
                      f"  C6 Pos: {state_6.values[moteus.Register.POSITION]:.2f} | "
                       f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} | "
                        f"  C12 Pos: {state_12.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_3.set_stop()
        await controller_6.set_stop()
        await controller_9.set_stop()
        await controller_12.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
