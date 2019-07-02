import evdev
import yaml
import subprocess
import socket
import _thread


def main():
    # Let's import our lock.
    global runned
    # Load the from the device path in the config
    device = evdev.InputDevice(cfg['device'])

    # Saving key IDs to a static variable. I don't really know if it helps, but makes the code more readable.
    key1, key2 = cfg['combination_keys']

    # Let's define some "locks" to use in the function, as we need them to know the state of each key.
    # They will be true when the key is "down" (or "holded down") and false when key is "up"
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
        if ctrl_r and ctrl_l and not runned:
            # runned is needed to actually skip multiple "holding" events, this way the event never repeats until
            # the lock is resetted by the server.
            runned = True
            # Spawn a new thread for calling the process as missing that will block the main thread.
            _thread.start_new_thread(run, (True,))


def config():
    # We will load some config file to actually customize the behavior of the script.
    with open('config.yml', 'r') as cfg_file:
        # We will use yaml full loader. This can make a security issue, but it's easier to handle.
        return yaml.load(cfg_file, Loader=yaml.FullLoader)


def server():
    # Let's import our lock
    global runned
    # Create the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to the interface in the config
    s.bind((cfg['host'], cfg['port']))

    # And listen
    s.listen(1)

    # The "while true" doesn't impact performance, since s.accept() is blocking
    while True:
        # Set two vars we need. the connection, and the address (of the remote client). These will be returned from
        # s.accept() method.
        conn, addr = s.accept()
        try:
            # Receive the data
            data = conn.recv(1024)
            # If the data is null, something went seriously wrong.
            if not data:
                break
            # If the data is the text "run" then let's fire up the post_process
            if "run" in str(data).strip():
                # Reset "runned" state, so we can start over again
                runned = False
                # Spawn a new thread for calling the process as missing that will block the main thread.
                _thread.start_new_thread(run, (False,))
        # Just in case something screws up with the connection, let's handle that.
        except socket.error:
            print("Error while handling socket.")
            break
        # And a catch all exception helps wrapping it up, helping the user to discover the exception.
        except Exception as e:
            print("Fatal error! " + str(e))
            break
    # Dispose the connection. We no longer need it.
    conn.close()


def run(start_process):
    # Running the command specified in the config. (in a try block to catch any error)
    # Note: start_process is a boolean: if true, it will run pre_command(s),
    # if false it will run post_command(s).
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
    # Create a lock var to never repeat the commands multiple times.
    runned = False
    # Running server on another thread, to be asynchronous from the first one.
    server_th = _thread.start_new_thread(server, ())
    # Start the program.
    main()
