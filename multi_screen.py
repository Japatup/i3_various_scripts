#! /usr/bin/python3

import subprocess as sp
import re
import argparse

### fixed params ###
M_screen = ["eDP1"]
M_pasink = ["alsa_output.pci-0000_00_1b.0.analog-stereo"]
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

group_audio = parser.add_mutually_exclusive_group()
group_audio.add_argument("-M", "--audio_main",help="move audio signal to the main pulse audio sink (defined at the beginning of the program)" ,action="store_true")
group_audio.add_argument("-G", "--audio_guest",help="move audio signal to the guest pulse audio sink" ,action="store_true")

parser.add_argument("-c","--confirm", help="print the shell command about to be called and ask confirmation before launching it. Can be used as a verbose mode for checking, debugging and understanding things",action="store_true")

args = parser.parse_args()
## parmi les arguments de display : 
args_display = {k:v for (k,v) in args.__dict__.items() if k in ["main", "guest", "right", "left", "up", "down", "iso"]}
## lequel est à True ?
W_layout = [k for (k,v) in args_display.items() if v == True]
W_layout = W_layout[0] if len(W_layout) == 1 else None

## parmi les arguments de audio
args_audio = {k:v for (k,v) in args.__dict__.items() if k in ["audio_main", "audio_guest"]}
## lequel est à True ?
W_audio = [k for (k,v) in args_audio.items() if v == True]
W_audio = W_audio[0] if len(W_audio) == 1 else None
# W_audio = "audio_main" ## pour test
######################

### functions ###

## screen functions

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

## audio functions

def get_E_pasinks(wanted_keys = None, verbose = False):
    """
    returns a list of existing pulse audio sinks.
    To know which ones are currently available, ask (at least) for the "Ports" key
    Then, use the get_C_pasinks function on the E_pasinks list
    """
    # wanted_keys = ["Name", "Ports"]
    # wanted_keys = None
    
    ## récup sortie pactl
    pactl_output = sp.Popen("pactl list sinks", shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    
    ## init
    sinks = []
    n_sink = -1
    actual_key = None
    for (ii,x_ii) in enumerate(pactl_output):
        # ii = 31
        # x_ii = pactl_output[ii]
        if verbose : 
            print(str(ii) + ":" + x_ii)
        tmp_search = re.search(r'^Sink\s+#(?P<num_sink>[0-9]+)',x_ii)
        if tmp_search is not None:
            if verbose:
                print("### nouveau sink : " + tmp_search.group("num_sink"))
            n_sink +=1
            sinks.append({"n_sink":tmp_search.group("num_sink")})
            continue
            
        ## cas des 1 tab
        tmp_search = re.search(r'^\t(?!\t)(?P<pactl_key>.*?)\s*:\s*(?P<pactl_value>.*)$',x_ii)
        if tmp_search is not None:
            if verbose:
                print("### new key : " + tmp_search.group("pactl_key"))
            actual_key = tmp_search.group("pactl_key")
            if wanted_keys is not None and actual_key is not None and actual_key not in wanted_keys : 
                actual_key = None
                continue
            if tmp_search.group("pactl_value") is not None and tmp_search.group("pactl_value") != '':
                if verbose:
                    print("### new value direct : " + tmp_search.group("pactl_value"))
                sinks[n_sink].update({actual_key:tmp_search.group("pactl_value")})
            else:
                if verbose:
                    print("### no_value : creation of empty dict")
                sinks[n_sink].update({actual_key:{}})
            continue
            
        ## cas des 2 tabs
        tmp_search = re.search(r'^\t\t(?P<pactl_key>.*?)\s*[=:]\s*(?P<pactl_value>.*)$',x_ii)
        if tmp_search is not None and actual_key is not None:
            if verbose:
                print("### new sub key : " + tmp_search.group("pactl_key"))
            if tmp_search.group("pactl_value") is not None and tmp_search.group("pactl_value") != '':
                if verbose:
                    print("### new sub value : " + tmp_search.group("pactl_value"))
                sinks[n_sink][actual_key].update({tmp_search.group("pactl_key"):tmp_search.group("pactl_value")})
            continue
    return(sinks)

def get_C_pasinks(existing_pasinks, ports_key="Ports", name_key = "Name"):
    """
    Takes a list of existing pulse audio sinks as returned by the get_E_pasinks function, and determines which ones are currently available (ie connected) thanks to the Ports value of the pactl output
    """
    tmp = [[re.search(r'^.*\(priority\s*:\s*[0-9]*(,\s*(?P<status>.*)\))?',jj).group("status") for jj in ii[ports_key].values()] for ii in existing_pasinks]
    tmp = [1 if "available" in ii or None in ii else 0 for ii in tmp]
    tmp = [existing_pasinks[ii][name_key] for ii in range(len(existing_pasinks)) if tmp[ii] == 1]
    return(tmp)

def get_G_pasink(M_sink, C_sink):
    """
    returns 'the other available pulse audio sinks', the guest sink. G sink is dynamically found among connected sinks (C_pasinks), only if there is just one connected sink in addition to the principal sink (M_pasink) whose name is static (defined in params)
    """
    G_sink = set(C_sink) - set(M_sink)
    assert len(G_sink) <= 1, "Too much screens sinks, can't define which one is your guest sink. Stopping"
    return(list(G_sink))

def get_E_pasink_inputs():
    """
    returns a list of currently active sinks_inputs (only their pulse audio id)
    """
    tmp = sp.Popen("pactl list sink-inputs short", shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
    E_sink_inputs = [ii.split("\t")[0] for ii in tmp]
    return(E_sink_inputs)

### cases ###

## actions on layout

if W_layout is not None:
    ## 0) détermination de G, A, C et W ____
    A_screens = get_A_screens()
    C_screens = get_C_screens()
    G_screen = get_G_screen(M_screen, C_screens)

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
    T_screens_command = ["--output {screen} {rp} {a} --auto".format(screen = ii, rp = rel_pos_ref_command[W_layout], a = A_screens[0]) for ii in T_screens]
    T_screens_command = " ".join(T_screens_command) ## to prepare 3+ screens gestion
    
    command = " ".join([C_screens_command, T_screens_command])
    command = "xrandr " + command
    call_command(command, command_name = "xrandr command", ask_confirm_flag = args.confirm)
    
## actions on audio

if W_audio is not None:
    ## 0bis) détermination de E, C, G et W ____
    E_pasinks = get_E_pasinks(wanted_keys = ["Name","Ports"])
    C_pasinks = get_C_pasinks(E_pasinks)
    G_pasink = get_G_pasink(M_pasink, C_pasinks)
    
    ## 1bis) déplacement des sink inputs vers le sink choisi
    ## détermination du W_pasink
    W_pasink = M_pasink if W_audio == "audio_main" else G_pasink
    
    if len(W_pasink) == 1:
        ## détermination des sink inputs à migrer
        E_pasink_inputs = get_E_pasink_inputs()
        if len(E_pasink_inputs) == 0 and args.confirm:
            print("no sink_inputs to move. Make sure some audio signal is currently played")
        ## écriture de la commande
        command = ["pactl move-sink-input {sink_input} {sink}".format(sink_input = ii, sink = W_pasink[0]) for ii in E_pasink_inputs]
        command = " ; ".join(command)
        if re.match(r"^\s?$", command) is None: ## ie si command est rens
            call_command(command, command_name = "pactl command", ask_confirm_flag = args.confirm)
            
    elif len(W_pasink) == 0:
        raise Exception("Be sure the guest pulse audio sink is available (have you connected your HDMI/DP/whatever output ?")
