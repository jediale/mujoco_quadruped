import inputs
import time

print("Reading Xbox controller...")
print("Make sure controller is plugged in and move the sticks\n")

try:
    while True:
        try:
            events = inputs.get_gamepad()
            if events:
                for event in events:
                    print(f"{event.ev_type}: {event.state}")
        except inputs.UnpluggedError:
            print("Controller unplugged - reconnecting...")
            time.sleep(1)
            continue
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting...")