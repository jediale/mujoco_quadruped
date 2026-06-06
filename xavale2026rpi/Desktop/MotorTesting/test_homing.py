import asyncio
import math
import moteus
import moteus_pi3hat
import time

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
    state_1 = await controller_1.set_stop(query=True)
    starting_position_1 = state_1.values[moteus.Register.POSITION]

    state_2 = await controller_2.set_stop(query=True)
    starting_position_2 = state_2.values[moteus.Register.POSITION]

    state_3 = await controller_3.set_stop(query=True)
    starting_position_3 = state_3.values[moteus.Register.POSITION]

    state_4 = await controller_4.set_stop(query=True)
    starting_position_4 = state_4.values[moteus.Register.POSITION]

    state_5 = await controller_5.set_stop(query=True)
    starting_position_5 = state_5.values[moteus.Register.POSITION]

    state_6 = await controller_6.set_stop(query=True)
    starting_position_6 = state_6.values[moteus.Register.POSITION]

    state_7 = await controller_7.set_stop(query=True)
    starting_position_7 = state_7.values[moteus.Register.POSITION]

    state_8 = await controller_8.set_stop(query=True)
    starting_position_8 = state_8.values[moteus.Register.POSITION]

    state_9 = await controller_9.set_stop(query=True)
    starting_position_9 = state_9.values[moteus.Register.POSITION]

    state_10 = await controller_10.set_stop(query=True)
    starting_position_10 = state_10.values[moteus.Register.POSITION]

    state_11 = await controller_11.set_stop(query=True)
    starting_position_11 = state_11.values[moteus.Register.POSITION]

    state_12 = await controller_12.set_stop(query=True)
    starting_position_12 = state_12.values[moteus.Register.POSITION]

    # Consolidate baseline variables
    starts = [
        starting_position_1, starting_position_2, starting_position_3,
        starting_position_4, starting_position_5, starting_position_6,
        starting_position_7, starting_position_8, starting_position_9,
        starting_position_10, starting_position_11, starting_position_12
    ]

    # notes on backlash -3.8 is actually -1.8 according to measurement  but I'm moving it
    deltas = [0, -0.7, 3.7, 0, -1.1, -4.1, 0, 0.8, -4.0, 0, 1, -1.8]
    
    # Pre-calculate absolute target endpoints matching your exact direction arithmetic
    # lots of weights based on tuning, front legs extend less than the back
    targets = [
        starts[0] + deltas[0],
        starts[1] + 1.6*deltas[1],
        starts[2] + 1.1*deltas[2],
        starts[3] - deltas[3],
        starts[4] - 1.3*deltas[4],
        starts[5] + 1.3*deltas[5],
        starts[6] + deltas[6],
        starts[7] + 2.2*deltas[7],
        starts[8] + 2.5*deltas[8],
        starts[9] - deltas[9],
        starts[10] - 2.5*deltas[10],
        starts[11] - 2.3*deltas[11]
    ]

    # -------------------------------------------------------------------------
    # 📈 GENERATE 200-STEP INTERPOLATED TRAJECTORY MATRIX
    # -------------------------------------------------------------------------
    STEPS = 200
    trajectory = []
    
    for step_idx in range(STEPS):
        # Calculate interpolation factor tracking linearly from 0.0 to 1.0
        alpha = step_idx / (STEPS - 1)
        
        # Linear interpolation formula: start + alpha * (target - start)
        step_positions = [
            starts[m_idx] + alpha * (targets[m_idx] - starts[m_idx])
            for m_idx in range(12)
        ]
        trajectory.append(step_positions)

    print(f"Generated trajectory profile. Total micro-steps: {len(trajectory)}")
    print("Starting streaming trajectory control loop...")
    
    try:
        # Loop through each calculated slice sequentially
        for step_idx, targets_slice in enumerate(trajectory):
            loop_start = time.perf_counter()

            # Pass the interpolated slice values down the serial commands
            state_1 = await controller_1.set_position(
                position=targets_slice[0], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_2 = await controller_2.set_position(
                position=targets_slice[1], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_3 = await controller_3.set_position(
                position=targets_slice[2], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_4 = await controller_4.set_position(
                position=targets_slice[3], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_5 = await controller_5.set_position(
                position=targets_slice[4], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_6 = await controller_6.set_position(
                position=targets_slice[5], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_7 = await controller_7.set_position(
                position=targets_slice[6], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_8 = await controller_8.set_position(
                position=targets_slice[7], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_9 = await controller_9.set_position(
                position=targets_slice[8], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_10 = await controller_10.set_position(
                position=targets_slice[9], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_11 = await controller_11.set_position(
                position=targets_slice[10], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_12 = await controller_12.set_position(
                position=targets_slice[11], velocity=0.0, maximum_torque=1.0, query=True
            )

            # Print telemetry tracking at 20-step intervals to avoid console flooding
            if step_idx % 20 == 0:
                print(f"Step {step_idx}/{STEPS}")
                print(f"  C1 Pos: {state_1.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_1.values[moteus.Register.FAULT])}) | "
                      f"  C2 Pos: {state_2.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_2.values[moteus.Register.FAULT])}) | "
                      f"  C3 Pos: {state_3.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_3.values[moteus.Register.FAULT])}) | ")
                print(f"  C4 Pos: {state_4.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_4.values[moteus.Register.FAULT])}) | "
                      f"  C5 Pos: {state_5.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_5.values[moteus.Register.FAULT])}) | "
                      f"  C6 Pos: {state_6.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_6.values[moteus.Register.FAULT])}) | ")
                print(f"  C7 Pos: {state_7.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_7.values[moteus.Register.FAULT])}) | "
                      f"  C8 Pos: {state_8.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_8.values[moteus.Register.FAULT])}) | "
                      f"  C9 Pos: {state_9.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_9.values[moteus.Register.FAULT])}) | ")
                print(f"  C10 Pos: {state_10.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_10.values[moteus.Register.FAULT])}) | "
                      f"  C11 Pos: {state_11.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_11.values[moteus.Register.FAULT])}) | "
                      f"  C12 Pos: {state_12.values[moteus.Register.POSITION]:.2f} (Frt: {int(state_12.values[moteus.Register.FAULT])}) | ")

            # 🛑 CRITICAL WARNING REMINDER FOR THE SEQUENTIAL STRUCTURE:
            # 12 sequential awaits take ~15-25ms. To avoid triggering the internal 
            # safety watchdog fault on the motor, we must keep this loop rate tight.
            # 0.005 (5ms) acts as a placeholder yield so the OS can process I/O.
            await asyncio.sleep(0.005)

    finally:
        print("Stopping...")
        while True:
            # Pass the interpolated slice values down the serial commands
            state_1 = await controller_1.set_position(
                position=targets[0], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_2 = await controller_2.set_position(
                position=targets[1], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_3 = await controller_3.set_position(
                position=targets[2], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_4 = await controller_4.set_position(
                position=targets[3], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_5 = await controller_5.set_position(
                position=targets[4], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_6 = await controller_6.set_position(
                position=targets[5], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_7 = await controller_7.set_position(
                position=targets[6], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_8 = await controller_8.set_position(
                position=targets[7], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_9 = await controller_9.set_position(
                position=targets[8], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_10 = await controller_10.set_position(
                position=targets[9], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_11 = await controller_11.set_position(
                position=targets[10], velocity=0.0, maximum_torque=1.0, query=True
            )
            state_12 = await controller_12.set_position(
                position=targets[11], velocity=0.0, maximum_torque=1.0, query=True
            )
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
