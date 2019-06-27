#VFIO-Switcher
######*A custom python3 script to help switching inputs/running programs when evdev switches from and to guest VMs.*


> Note:
> The program will be provided as is, without any explicit nor implicit warranty. If you accuse me of messing up your computer by running this code, i will point my finger and laugh at you.

## How it works
In order to understand how the program works, you first need to know why it was made.

I was having problems switching my monitor inputs automatically when evdev grabs my keyboard and mouse (by default by hitting both CTRL keys) , so I decided to make a script that can execute any command(s) when this happens.

This works by intercepting `/dev/input` when the keyboard/mouse is connected to the host, and by sending a TCP payload when the input is on the guest.
This way, you can execute any script to switch you monitor, usb devices, etc.

## Installation
The script is composed by two parts, one is a client (*client.py*), the other one is a server (*main.py*)

The client requires no dependencies outside of python3 itself (or even neither that, as the code can be statically compiled with cython)
while the server needs PyYaml and evdev.

To install server dependecies, clone the repository and run:

`pip install -r requirements.txt`

Then you can edit the _config.yml_ file according to you preferences and run:

`python3 main.py`

## Usage
While the _config.yml_ file is commented and pretty self-explanatory, here is each value explained in detail:

|Parameter|Notes|
|---------|-----|
|device|This indicates the path to your keyboard in /dev/input|
|pre_command|This is a list of commands that the script will run when switching input from the host to the guest vm. Note that all the commands wll be executed on the **HOST**|
|post_command|This is a list of commands that the script will run when switching input from the guest vm to the host. Note that all the commands wll be executed on the **HOST**|
|shell_mode|If this is set to true (default) the command will be called by the default shell of the user executing the script.
|combination_keys|This is a list of key IDs  that will trigger the switch from the host to the guest. Note that this script will **not** override the default evdev key combination (CTRL_L + CTRL_R)|
|host|On which IP should the TCP server listen for client packet. Note that this interface must be reachable from the vm.|
|port|On which port to listen for the TCP client packet. Note that this port must be reachable from the vm.|

The script has no other special flags or special functions. Any new idea or contribution (via pull request) is welcome.