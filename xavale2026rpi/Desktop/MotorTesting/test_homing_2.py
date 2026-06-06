import asyncio
import math
import moteus
import moteus_pi3hat
import time

async def main():
    # 1. Setup transport for all buses on the Pi3Hat
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map={1: [1,2,3], 2:[4,5,6], 3: [7,8,9], 4:[10,11,12]}, 
    )

    # 2. Instantiate all 12 controllers dynamically in a dictionary
    controllers = {i: moteus.Controller(id=i, transport=transport) for i in range(1, 13)}

    # 3. Stop all concurrently to clear any existing legacy faults
    print("🧹 Resetting motors and clearing legacy faults...")
    await asyncio.gather(*[controllers[i].set_stop() for i in range(1, 13)])
    await asyncio.sleep(0.5)

    # 4. Query all initial positions simultaneously
    print("📊 Fetching starting positions...")
    query_results = await asyncio.gather(*[controllers[i].set_stop(query=True) for i in range(1, 13)])
    starts = [state.values[moteus.Register.POSITION] for state in query_results]
    print(f"Initial Positions: {[round(p, 2) for p in starts]}")

    # Your custom offset weights and directions
    old_deltas = [0, -0.7, 3.7, 0, -1.1, -4.1, 0, 0.8, -4.0, 0, 1, -1.8]
    deltas = [0, 1.7, -3.7, 0, 2.1, 4.1, 0, -0.8, 3.5, 0, -1, 1.8] #negated / flipped and tuned
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
    print(f"Final Positions: {[round(p, 2) for p in targets]}")

    # 📈 GENERATE 200-STEP INTERPOLATED TRAJECTORY MATRIX
    STEPS = 200
    trajectory = []
    for step_idx in range(STEPS):
        alpha = step_idx / (STEPS - 1)
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
            # ✨ FIX: Fire all 12 positional commands concurrently across the CAN lines
            move_tasks = [
                controllers[i].set_position(
                    position=targets_slice[i-1], 
                    velocity=0.0, 
                    maximum_torque=2, 
                    query=True
                )
                for i in range(1, 13)
            ]
            print("before")
            move_results = await asyncio.gather(*move_tasks)
            print("after")

            # Print telemetry tracking at 20-step intervals to avoid console flooding
            if step_idx % 20 == 0:
                print(f"\nStep {step_idx}/{STEPS}")
                for group in range(0, 12, 3):
                    line = ""
                    for j in range(3):
                        idx = group + j
                        pos = move_results[idx].values[moteus.Register.POSITION]
                        flt = int(move_results[idx].values[moteus.Register.FAULT])
                        line += f"C{idx+1} Pos: {pos:.2f} (Frt: {flt}) | "
                    print(line)

            # A 10ms (0.01) pause is highly stable for streaming trajectory steps over CAN
            await asyncio.sleep(0.01)

            print("end of loop!")

        # Hold the final position for a few seconds before quitting
        print("\nTrajectory finished! Holding targets...")
        for _ in range(900):
            await asyncio.gather(*[
                controllers[i].set_position(position=targets[i-1], velocity=0.0, maximum_torque=2.0)
                for i in range(1, 13)
            ])
            await asyncio.sleep(0.01)

    finally:
        # ✨ FIX: Safely stop all motors concurrently upon exit, avoiding infinite loop locks
        print("\n🛑 Shutting down and releasing motor coils safely...")
        await asyncio.gather(*[controllers[i].set_stop() for i in range(1, 13)])

if __name__ == '__main__':
    asyncio.run(main())