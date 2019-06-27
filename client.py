import socket
import sys
from pynput import keyboard


def main():
    global current
    current = set()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def on_press(key):
    global current
    if any([key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}]):
        current.add(key)
        if all(k in current for k in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}):
            connect()


def on_release(key):
    global current
    if any([key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}]):
        current.remove(key)


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((sys.argv[1], int(sys.argv[2])))
        s.sendall(b'run')
        s.close()
    except Exception as e:
        print("Exception occourred while connecting: " + str(e))


if __name__ == "__main__":
    main()
