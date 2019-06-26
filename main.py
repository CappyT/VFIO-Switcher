import evdev
import yaml
import subprocess
import socket
from threading import Thread
import _thread


def main():
    # Using the ID will ensure the device is always picked, even if its ID changes.
    device = evdev.InputDevice(cfg['device'])

    # Saving key IDs to a static variable. I don't really know if it helps, but makes the code more readable.
    key1, key2 = cfg['combination_keys']

    # Let's define some "locks" to use in the function, as we need them to know the state of each keys
    ctrl_r, ctrl_l = False, False

    for event in device.read_loop():
        if event.code == key1 and event.value == 1:
            # CTRL_L is down, setting its lock to true
            ctrl_l = True
        if event.code == key1 and event.value == 0:
            # CTRL_L is up, setting its lock to false
            ctrl_l = False
        if event.code == key2 and event.value == 1:
            # CTRL_R is down, setting its lock to true
            ctrl_r = True
        if event.code == key2 and event.value == 0:
            # CTRL_R is up, setting its lock to false
            ctrl_r = False
        if ctrl_r and ctrl_l and event.value == 1:
            # event.value is needed to actually catch the keydown event and not the "Holding" one, this way, the event
            # never repeats.
            # Spawn a new thread for calling the process as missing that will block the main thread.
            th = Thread(target=run, args=(True,))
            # Set daemonic mode. This way, the thread exits by itself in the background and quits after it finishes.
            th.setDaemon(True)
            th.run()


def config():
    # We will load some config file to actually customize the behavior of the script.
    with open('config.yml', 'r') as cfg_file:
        # We will use yaml full loader. This can make a security issue, but it's easier to handle.
        return yaml.load(cfg_file, Loader=yaml.FullLoader)


def server():
    # Create the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((cfg['host'], cfg['port']))

    s.listen(1)
    conn, addr = s.accept()

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # If the data is text "run" then let's fire up the post_process
            if "run" in str(data).strip():
                # Spawn a new thread for calling the process as missing that will block the main thread.
                th = Thread(target=run, args=(False,))
                # Set daemonic mode. This way, the thread exits by itself in the background and quits after it finishes.
                th.setDaemon(True)
                th.run()
        except socket.error:
            print("Error while handling socket.")
            break
    conn.close()


def run(start_process):
    # Running the command (in a try block to catch any error) (start_process is a boolean, if true,
    # it will run pre, if false it will run post
    if start_process:
        try:
            for command in cfg['pre_command']:
                subprocess.Popen(command, shell=cfg['shell_mode'])
        except Exception as e:
            print("Error while pre_command: " + str(e))
    if not start_process:
        try:
            for command in cfg['post_command']:
                subprocess.Popen(command, shell=cfg['shell_mode'])
        except Exception as e:
            print("Error while post_command: " + str(e))


if __name__ == "__main__":
    # Load the config and store it in cfg var. So we don't need to read it every time.
    cfg = config()
    # Running server on another thread, to be asynchronous from the first one.
    server_th = _thread.start_new_thread(server, ())
    # Start the program.
    main()
