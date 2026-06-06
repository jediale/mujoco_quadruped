import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={2: [4,5,6]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_4 = moteus.Controller(id=4, transport=transport)
    controller_5 = moteus.Controller(id=5, transport=transport)
    controller_6 = moteus.Controller(id=6, transport=transport)

    # 3. Stop both to clear faults
    await controller_4.set_stop()
    await controller_5.set_stop()
    await controller_6.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_4 = await controller_4.set_stop(query=True)  # or use set_position with query=True
    starting_position_4 = state_4.values[moteus.Register.POSITION]

    state_5= await controller_5.set_stop(query=True)  # or use set_position with query=True
    starting_position_5 = state_5.values[moteus.Register.POSITION]

    state_6 = await controller_6.set_stop(query=True)  # or use set_position with query=True
    starting_position_6 = state_6.values[moteus.Register.POSITION]

    print("Starting dual motor control loop...")
    try:
        N = 2 
        for i in range(200):
            command =  math.sin(N * 2 * math.pi * i / 200 * 0.5)
            
            # Or just await them sequentially:
            state_4 = await controller_4.set_position(
                position=starting_position_4 + command,
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

            state_6 = await controller_6.set_position(
                position=starting_position_6 + command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_4 and state_5 and state_6:
                print(f"  C1 Pos: {state_4.values[moteus.Register.POSITION]:.2f} | "
                      f"  C4 Pos: {state_5.values[moteus.Register.POSITION]:.2f} | "
                       f"  C7 Pos: {state_6.values[moteus.Register.POSITION]:.2f} | ")

            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_4.set_stop()
        await controller_5.set_stop()
        await controller_6.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
