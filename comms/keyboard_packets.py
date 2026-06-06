from pynput import keyboard

packet = [0,0,0,0,0,0,0,0,0,0,0,0] 

state = "still"

def on_press(key):

    global state

    # try:
    #     print(f'Key pressed: {key.char}')
    # except AttributeError:
    #     print(f'Special key pressed: {key}')
    try:
        if key.char == "1":
            packet[0] = packet[0] + 1
        elif key.char == "2":
            packet[1] = packet[1] + 1
        elif key.char == "3":
            packet[2] = packet[2] + 1
        elif key.char == "4":
            packet[3] = packet[3] + 1
        elif key.char == "5":
            packet[4] = packet[4] + 1
        elif key.char == "6":
            packet[5] = packet[5] + 1
        elif key.char == "7":
            packet[6] = packet[6] + 1
        elif key.char == "8":
            packet[7] = packet[7] + 1
        elif key.char == "9":
            packet[8] = packet[8] + 1
        elif key.char == "0":
            packet[9] = packet[9] + 1
        elif key.char == "-":
            packet[10] = packet[10] + 1
        elif key.char == "=":
            packet[11] = packet[11] + 1
        elif key.char == "q":
            packet[0] = packet[0] - 1
        elif key.char == "w":
            packet[1] = packet[1] - 1
        elif key.char == "e":
            packet[2] = packet[2] - 1
        elif key.char == "r":
            packet[3] = packet[3] - 1
        elif key.char == "t":
            packet[4] = packet[4] - 1
        elif key.char == "y":
            packet[5] = packet[5] - 1
        elif key.char == "u":
            packet[6] = packet[6] - 1
        elif key.char == "i":
            packet[7] = packet[7] - 1
        elif key.char == "o":
            packet[8] = packet[8] - 1
        elif key.char == "p":
            packet[9] = packet[9] - 1
        elif key.char == "[":
            packet[10] = packet[10] - 1
        elif key.char == "]":
            packet[11] = packet[11] - 1

        print(str(key))
        
        if key.char == "j":
            state = "left"
        elif key.char == "m":
            state = "back"
        elif key.char == "l":
            state = "right"
        elif key.char == "k":
            state = "forward"
        elif key.char == " ":
            state = "still"
    except AttributeError:
        pass




    print(" ",packet, state)

    # this might be an appropriate place to send the packet? assuming that for manual control testing, we only have to snend the packet when pressed

    

    # some kind of update_packet() function would be useful to define and use here

    # whatever packet is, it gets sent as a command to the script on the pi, which from there is going to update and store the most local value and either use that to command actuators individually or use the state and go into a forward, left, right, back mode!

    # control is local-level autonomous (actuator) and second-level hard-coded / autonomous (legs), otherwise it's manual stuff




def on_release(key):
    if key == keyboard.Key.esc:
        print("ESC pressed - exiting")
        return False
    
    # this will be what to ADD to the starting position, always RELATIVE



with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
