import asyncio
import math
import moteus
import moteus_pi3hat

async def main():
    # 1. Setup transport for both IDs on Bus 1
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3], 2:[4,5,6], 3: [7,8,9], 4:[10,11,12]}, 
    )

    # 2. Instantiate BOTH controllers
    controller_1 = moteus.Controller(id=1, transport=transport)
    controller_2 = moteus.Controller(id=2, transport=transport)
    controller_3 = moteus.Controller(id=3, transport=transport)
    controller_4 = moteus.Controller(id=4, transport=transport)
    controller_5 = moteus.Controller(id=5, transport=transport)
    controller_6 = moteus.Controller(id=6, transport=transport)
    controller_7 = moteus.Controller(id=7, transport=transport)
    controller_8 = moteus.Controller(id=8, transport=transport)
    controller_9 = moteus.Controller(id=9, transport=transport)
    controller_10 = moteus.Controller(id=10, transport=transport)
    controller_11 = moteus.Controller(id=11, transport=transport)
    controller_12 = moteus.Controller(id=12, transport=transport)

    # 3. Stop both to clear faults
    await controller_1.set_stop()
    await controller_2.set_stop()
    await controller_3.set_stop()
    await controller_4.set_stop()
    await controller_5.set_stop()
    await controller_6.set_stop()
    await controller_7.set_stop()
    await controller_8.set_stop()
    await controller_9.set_stop()
    await controller_10.set_stop()
    await controller_11.set_stop()
    await controller_12.set_stop()
    await asyncio.sleep(0.5)

    # Query the current position
    state_1 = await controller_1.set_stop(query=True)  # or use set_position with query=True
    starting_position_1 = state_1.values[moteus.Register.POSITION]

    state_2 = await controller_2.set_stop(query=True)  # or use set_position with query=True
    starting_position_2 = state_2.values[moteus.Register.POSITION]

    state_3 = await controller_3.set_stop(query=True)  # or use set_position with query=True
    starting_position_3 = state_3.values[moteus.Register.POSITION]

    state_4 = await controller_4.set_stop(query=True)  # or use set_position with query=True
    starting_position_4 = state_4.values[moteus.Register.POSITION]

    state_5= await controller_5.set_stop(query=True)  # or use set_position with query=True
    starting_position_5 = state_5.values[moteus.Register.POSITION]

    state_6 = await controller_6.set_stop(query=True)  # or use set_position with query=True
    starting_position_6 = state_6.values[moteus.Register.POSITION]

    state_7 = await controller_7.set_stop(query=True)  # or use set_position with query=True
    starting_position_7 = state_7.values[moteus.Register.POSITION]

    state_8= await controller_8.set_stop(query=True)  # or use set_position with query=True
    starting_position_8 = state_8.values[moteus.Register.POSITION]

    state_9 = await controller_9.set_stop(query=True)  # or use set_position with query=True
    starting_position_9 = state_9.values[moteus.Register.POSITION]

    state_10 = await controller_10.set_stop(query=True)  # or use set_position with query=True
    starting_position_10 = state_10.values[moteus.Register.POSITION]

    state_11= await controller_11.set_stop(query=True)  # or use set_position with query=True
    starting_position_11 = state_11.values[moteus.Register.POSITION]

    state_12 = await controller_12.set_stop(query=True)  # or use set_position with query=True
    starting_position_12 = state_12.values[moteus.Register.POSITION]

    
    print("Starting dual motor control loop...")
    try:
        N = 2 # periods
        T = 200 #timesteps
        for i in range(T):
            command_phaseFLBR =  math.sin(N * 2 * math.pi * i / T * 0.5) #slow
            command_phaseFRBL =  math.sin(N * 2 * math.pi * i / T * 0.5) #slow
            hip_command = 1
            # command =  math.sin(N * 2 * math.pi * i / 200) # mid

            hip_amp = 1
            thigh_amp = 1
            calf_amp = 1
            
            # Or just await them sequentially:

            state_1 = await controller_1.set_position(
                position=starting_position_1 + hip_amp*hip_command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_2 = await controller_2.set_position(
                position=starting_position_2 + thigh_amp*command_phaseFLBR,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_3 = await controller_3.set_position(
                position=starting_position_3 - calf_amp*command_phaseFLBR,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_4 = await controller_4.set_position(
                position=starting_position_4 - hip_amp*hip_command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_5 = await controller_5.set_position(
                position=starting_position_5 - thigh_amp*command_phaseFRBL,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_6 = await controller_6.set_position(
                position=starting_position_6 + calf_amp*command_phaseFRBL,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_7 = await controller_7.set_position(
                position=starting_position_7 + hip_amp*hip_command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_8 = await controller_8.set_position(
                position=starting_position_8 + thigh_amp*command_phaseFLBR,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_9 = await controller_9.set_position(
                position=starting_position_9 - calf_amp*command_phaseFLBR,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_10 = await controller_10.set_position(
                position=starting_position_10 - hip_amp*hip_command,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )
            
            state_11 = await controller_11.set_position(
                position=starting_position_11 - thigh_amp*command_phaseFRBL,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            state_12 = await controller_12.set_position(
                position=starting_position_12 + calf_amp*command_phaseFRBL,
                velocity=math.nan,
                maximum_torque=1.0,
                query=True
            )

            # Optional: Print status for both
            if state_1 and state_2 and state_3 and state_4 and state_5 and state_6 and state_7  and state_8 and state_9 and state_10 and state_11 and state_12:
                print(f"  C1 Pos: {state_1.values[moteus.Register.POSITION]:.2f} | "
                      f"  C2 Pos: {state_2.values[moteus.Register.POSITION]:.2f} | "
                       f"  C3 Pos: {state_3.values[moteus.Register.POSITION]:.2f} | ")
                print(f"  C4 Pos: {state_4.values[moteus.Register.POSITION]:.2f} | "
                      f"  C5 Pos: {state_5.values[moteus.Register.POSITION]:.2f} | "
                       f"  C6 Pos: {state_6.values[moteus.Register.POSITION]:.2f} | ")
                print(f"  C7 Pos: {state_7.values[moteus.Register.POSITION]:.2f} | "
                      f"  C8 Pos: {state_8.values[moteus.Register.POSITION]:.2f} | "
                       f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} | ")
                print(f"  C10 Pos: {state_10.values[moteus.Register.POSITION]:.2f} | "
                      f"  C11 Pos: {state_11.values[moteus.Register.POSITION]:.2f} | "
                       f"  C12 Pos: {state_12.values[moteus.Register.POSITION]:.2f} | ")


            await asyncio.sleep(0.02)

    finally:
        print("Stopping...")
        await controller_1.set_stop()
        await controller_2.set_stop()
        await controller_3.set_stop()
        await controller_4.set_stop()
        await controller_5.set_stop()
        await controller_6.set_stop()
        await controller_7.set_stop()
        await controller_8.set_stop()
        await controller_9.set_stop()
        await controller_10.set_stop()
        await controller_11.set_stop()
        await controller_12.set_stop()

if __name__ == '__main__':
    asyncio.run(main())
