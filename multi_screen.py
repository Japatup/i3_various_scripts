#! /usr/bin/python3

import subprocess as sp
import re
import argparse

### fixed params ###
M_screen = ["eDP1"]
####################

### dynamic params ###
parser = argparse.ArgumentParser(description="calls xrandr to easily manage two screens")
group_display = parser.add_mutually_exclusive_group()
group_display.add_argument("-m", "--main",help="display only the main screen" ,action="store_true")
group_display.add_argument("-g", "--guest",help="display only the guest screen" ,action="store_true")
group_display.add_argument("-r", "--right",help="if only one screen is turned on, display the other one at its right. If both screens are turned on, the right one will be the guest screen" ,action="store_true")
group_display.add_argument("-l", "--left",help="if only one screen is turned on, display the other one at its left. If both screens are turned on, the left one will be the guest screen" ,action="store_true")
group_display.add_argument("-u", "--up",help="if only one screen is turned on, display the other one above. If both screens are turned on, the above one will be the guest screen" ,action="store_true")
group_display.add_argument("-d", "--down",help="if only one screen is turned on, display the other one under. If both screens are turned on, the under one will be the guest screen" ,action="store_true")
group_display.add_argument("-i", "--iso",help="clone both screens" ,action="store_true")
parser.add_argument("-c","--confirm", help="print the shell command about to be called and ask confirmation before launching it",action="store_true")

args = parser.parse_args()
## parmi les arguments de display : 
args_display = {k:v for (k,v) in args.__dict__.items() if k in ["main", "guest", "right", "left", "up", "down", "iso"]}
## lequel est à True ?
W_layout = [k for (k,v) in args_display.items() if v == True]
W_layout = W_layout[0] if len(W_layout) == 1 else None

######################

### functions ###
def get_C_screens():
    """
    returns connected screens, active or that could be activated
    """
    # xrandr_output = sp.Popen("xrandr |grep -e \"\\sconnected\" |awk '{print $1}'",shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    ## full python way :
    xrandr_output = sp.Popen("xrandr",shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    xrandr_output = [ii for ii in xrandr_output if re.search(r"(?<!dis)connected",ii) is not None]
    xrandr_output = [re.split("\\s+",ii)[0] for ii in xrandr_output]
    return(xrandr_output)

def get_A_screens():
    """
    returns active screens, that are currently displaying graphic interface
    """
    # xrandr_output = sp.Popen("xrandr |grep -e \"\\sconnected\" |awk '{print $1}'",shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    ## full python way :
    xrandr_output = sp.Popen("xrandr --listactivemonitors",shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    xrandr_output = [re.search(r".*\s+(?P<screen>.*)$",ii).group("screen") for ii in xrandr_output if re.search(r"[0-9]+:.*",ii) is not None]
    return(xrandr_output)

def get_G_screen(M_screen, C_screens):
    """
    returns 'the other available screen', the B screen. B screen is dynamically found among connected screens (C_screens), only if there is just one connected screen in addition the the principal screen (M_screen) whose name is static (defined in params)
    """
    G_screen = set(C_screens) - set(M_screen)
    assert len(G_screen) <= 1, "Too much screens detected, can't define which one is your B screen. Stopping"
    return(list(G_screen))

def get_delta_screens(begin_list, end_list):
    """
    returns the list of screens to switch on or off to pass from begin_list to end_list
    """
    D_screens = set(begin_list) - set(end_list)
    return(list(D_screens))

def call_command(command, command_name = "command", ask_confirm_flag = False):
    """
    launches a command, directly or asking confirmation
    """
    if ask_confirm_flag:
        print(command_name + " : \n" + command)
        choice = input("execute command ?(y/n)")
        if choice.upper() == "Y":
            sp.Popen(command, shell = True)
        else : pass
    else:
        sp.Popen(command, shell = True)


## 0) détermination de G, A, C et W ____
A_screens = get_A_screens()
C_screens = get_C_screens()
G_screen = get_G_screen(M_screen, C_screens)
# W_screens = # à monter selon les paramètres en entrée
# W_screens = G_screen
# W_screens = M_screen

if W_layout in ["main", "guest"]:
    ## 1) cas 1 : go to one screen ____
    ## détermination du W_screens
    W_screens = M_screen if W_layout == "main" else G_screen
    
    if len(W_screens) < 1:
        raise Exception("Wanted screens are not connected. Be sure to connect another screen")
        
    ## les screens à éteindre (K_screens)
    K_screens = get_delta_screens(A_screens, W_screens)
    K_screens_command = " ".join(["--output {} --off".format(ii) for ii in K_screens]) if len(K_screens) > 0 else ""
    
    ## les screens à allumer (T_screens)
    T_screens = W_screens ## on peut les rallumer dans tous les cas, même si déjà allumés --> Peut éviter un cas bloquant si tous les écrans se retrouvent éteints
    T_screens_command = " ".join(["--output {} --auto".format(ii) for ii in T_screens]) if len(T_screens) > 0 else ""
    
    ## command :
    command = " ".join([K_screens_command, T_screens_command])
    if re.match(r"^\s?$", command) is None: ## ie si command est rens
        command = "xrandr " + command
        call_command(command, command_name = "xrandr command", ask_confirm_flag = args.confirm)
    
elif W_layout in ["right", "left", "up", "down", "iso"]:
    ## 2) cas 2 :  go to two screen ____
    ## vient-on de 1 ou deux écrans actifs ?
    rel_pos_ref_command = {"right":"--right-of","left":"--left-of","up":"--above","down":"--below","iso":"--same-as"}
    if len(A_screens) == 1:
        T_screens = get_delta_screens(C_screens, A_screens)
    elif len(A_screens) in [0,2]:
        T_screens = G_screen
    else:
        raise Exception("Too much active screens, can't define which one is your B screen. Stopping")
    
    if len(T_screens) < 1:
        raise Exception("Wanted screens are not connected. Be sure to connect another screen")
    
    ## les screens connectés, à remettre en auto
    ## (Permet de pouvoir passer d'une situation en 2 écrans off à la situation extended voulue d'un coup (autrement, seul le G_screen s'allume))
    C_screens_command = ["--output {screen} --auto".format(screen = ii) for ii in C_screens] ## remet en auto les screens connectés. 
    C_screens_command = " ".join(C_screens_command)
    
    ## le screen vers lequel on étend le layout
    T_screens_command = ["--output {screen} {rp} {a}".format(screen = ii, rp = rel_pos_ref_command[W_layout], a = A_screens[0]) for ii in T_screens]
    T_screens_command = " ".join(T_screens_command) + " --auto" ## to prepare 3+ screens gestion
    
    command = " ".join([C_screens_command, T_screens_command])
    command = "xrandr " + command
    call_command(command, command_name = "xrandr command", ask_confirm_flag = args.confirm)