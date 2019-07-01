## Various scripts used with i3

Here are the scripts I use with i3wm, especially to bind functionnalities to Fn keys. You will find more details for these scripts in my `various_wiki` repo.

Some of these scripts interact with `/sys` files to play with leds of my laptop, an **Asus Zenbook UX303L**. Then I guess they may be not directly usable with other hardware, but maybe adaptable.

Btw, each of these scripts should be executable by all users, and copied (possibly as a symlink) in `/usr/local/bin` : 
```bash
chmod a+x my_script.sh
ln -s my_script.sh /usr/local/bin/my_script
```

Here you will find scripts to :
1. turn on/off plane mode and sync the associated led on the keyboard *(depends on network-manager)*
2. manage keyboard backlight level
3. adjust the screen backlight *(depends on xbacklight)*
4. control audio volume and sync it with i3blocks (i3status) bar *(depends on pulseaudio)*
5. mount all mtp devices, even if not root *(depends on jmtpfs)*
6. toggle touchpad device
7. toggle autokey (a brilliant software to define personal keybindings and remap your keyboard. See [here](https://github.com/autokey/autokey) for more details ) 

#### 1. plane mode

This script performs two actions : 
- at boot, it is launched and gives all users write acces on `/sys/class/leds/asus-wireless::airplane/brightness` file, that is watched by the kernel to accordingly turn on/off the plane-mode led. That way, all users will be allowed to play with the led, and not only root.
- during session, it manages radio commands via **network-manager** to enable/disable wifi connections. Feel free to adapt it so it may work with wicd or wpa :)

Things to do : 
- execute `plane_mod allowusers` as root at each boot. You may for instance add it in your `/etc/rc.local` file. *NB : On debian 9, `/etc/rc.local` doesn't exist anymore. You will have to create it and make a service launch it. For more details, you can see the kbd_backlight.md wiki of my wiki repo, where the operation is explained.*
- symlink the script to `/usr/local/bin` so it will be available for the users.
- launch `plane_mode sync_led` at boot (not necessarily as root). It will sync the led with the state of the radio connections. Just can just add it in an exec in your i3 config file :*
    ```
    exec /bin/bash -c "plane_mode sync_led"
    ```
- add a keybinding (in your i3 config file) to call `plane_mode toggle` : 
    ```
    bindcode 255 exec plane_mode toggle
    ## 255 matches the Fn+f2 key : find your key with xev
    ```

#### 2. keyboard backlight

The principle is exactly the same as plane mode : giving write rights on a `/sys` file which is mapped with hardware (`/sys/class/leds/asus::kbd_backlight/brightness`), and then modifying it to increase/decrease keyboard backlight. If you have understood plane mod conf, this one won't be a problem :)

#### 3. screen backlight

This script just uses **xbacklight** to control screen brightness. Why a script then ? Only to prevent the brightness level to decrease to 0, since your screen becomes entirely black then... The minimum value you accept to reach is defined in the `min` variable at the beginning of the program, and is 1 by default.

#### 4. audio volume

It's only a call to pactl (**pulseaudio needed**) to change the volume. The script just automatically selects the active audio sink before tying to change the volume. Then, if you have some HDMI connected and the audio output on it, the volume will be changed on hdmi and not on your laptop audio speakers.

The script adds the possibility to launch one other command before closing. I use this feature to send a signal to i3 blocks, which is configured to sync the audio volume when receiving that signal.

#### 5. mount mtp devices
The script uses **jmtpfs** to perform the mount in `/mnt/mtp_device` (you can change the name of the directory at the beginning of the script, variable `mount_dir`).

If you want all users to be able to use it, and not only root, just use a sudo rule (see my android_fichiers_mtp_conf.md wiki in my wiki repo)

#### 6. toggle touchpad device
The scripts uses **xinput** to find current state of your touchpad (monitored by libinput) et toggle it.

To make the program useful you may have to change the touchpad device name at the beginning of the code. You can find your libinput device names with the command `xinput` or `xinput list`.

On my laptop, the touchpad is `"FocalTechPS/2 FocalTech Touchpad"` : 
```
$ xinput
⎡ Virtual core pointer                    	id=2	[master pointer  (3)]
⎜   ↳ Virtual core XTEST pointer              	id=4	[slave  pointer  (2)]
⎜   ↳ FocalTechPS/2 FocalTech Touchpad        	id=13	[slave  pointer  (2)]
⎣ Virtual core keyboard                   	id=3	[master keyboard (2)]
    ↳ Virtual core XTEST keyboard             	id=5	[slave  keyboard (3)]
    ↳ Power Button                            	id=6	[slave  keyboard (3)]
    ↳ Asus Wireless Radio Control             	id=7	[slave  keyboard (3)]
    ↳ Video Bus                               	id=8	[slave  keyboard (3)]
    ↳ Video Bus                               	id=9	[slave  keyboard (3)]
    ↳ Sleep Button                            	id=10	[slave  keyboard (3)]
    ↳ Asus WMI hotkeys                        	id=11	[slave  keyboard (3)]
    ↳ AT Translated Set 2 keyboard            	id=12	[slave  keyboard (3)]
```
    
For more infos on how to bind the program to a key, just read the touchpad_configuration wiki in the `various_wiki` repo.

#### 7. Toggle autokey
A mere bash script used to :

- kill the running instance of Autokey, if one
- else, start a new instance

#### 8. Multi_screen
A python cli script used to easily manipulate both video and audio signals between two screens. It was thought to replace interfaces as [arandr](https://gitlab.com/arandr/arandr) and [pavucontrol](https://gitlab.freedesktop.org/pulseaudio/pavucontrol), but with keyboard keybindings only (faster :) )

##### Here are the commands to use (and to keybind eventually) :

- To use only one screen :
    - `multi_screen --main` : use only your "main" screen (see below)
    - `multi_screen --guest` : use only the "guest" screen (vga, hdmi, dp ...)

- To use both screens :
    - `multi_screen --left`
    - `multi_screen --right`
    - `multi_screen --up`
    - `multi_screen --down`
    - `multi_screen --iso`

        These commands will turn on the currently off screen and position it left, right, above or under the active one. The last command mirrors the two displays.

        If both are already on, then it's the "guest" screen that will be moved left, right, above or under the "main" screen.

- To move audio signal to one _or_ another screen :
    - `multi_screen --audio_main`
    - `multi_screen --audio_guest`

##### Keybindings

As you can see, to move both video and audio signals, you currently use two commands, one for each type. I did this to keep manipulations flexible. That way you may choose to send video to hdmi but to keep audio on your laptop, for headphones output maybe.

Nevertheless, if you want to move both signals, it's still two commands. For this reason, it's preferable to add keybindings to do the job. With mine (see below), I hit `End` to project to my guest screen only, then `Shift+End` to push the audio part as well. Quick and easy :)

Here are the keybindings I personnaly use on i3 (you may visit [my i3config repo](https://github.com/Japatup/i3_config) )
```
## ~/.config/i3/config
mode "multi_screen" {
    bindsym Home exec --no-startup-id multi_screen --main
    bindsym End exec --no-startup-id multi_screen --guest
    bindsym Left exec --no-startup-id multi_screen --left
    bindsym Right exec --no-startup-id multi_screen --right
    bindsym Up exec --no-startup-id multi_screen --up
    bindsym Down exec --no-startup-id multi_screen --down
    bindsym m exec --no-startup-id multi_screen --iso
    bindsym Shift+Left exec --no-startup-id multi_screen --audio_main
    bindsym Shift+Right exec --no-startup-id multi_screen --audio_guest

    # back to normal: Enter or Escape
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

bindsym $mod+F8 mode "multi_screen"
```

##### Configuration
The program is too simple to need config files. Then, all you must customise are two variables at the beginning of the script : `M_screen` and `M_pasink`.

These define the "main" screen and "main" PulseAudio sink names. Typically your laptop screen and audio sink names.

Indeed, the program will automatically find labels of the guest screen, without you to have to tell him if it's a hdmi, vga, display port ... input . However, it finds the guest labels (video and audio) by difference between all connected sources and the main screen properties, that you have to set then.

__How to find your screen and PulseAudio sink names ?__

- for the screen name :
    ```
    ## enter this command while you have no guest screen pluged
    xrandr --listactivemonitors
    ```
    In my case, it does return the name `eDP1`:
    ```
    0: +*eDP1 1366/290x768/160+0+0  eDP1
    ```
- for the audio sink :
    ```
    pactl list sinks short
    ```
    In my case, it will be `alsa_output.pci-0000_00_1b.0.analog-stereo` (the other one being hdmi) :
    ```
    0	alsa_output.pci-0000_00_03.0.hdmi-stereo	module-alsa-card.c	s16le 2ch 48000Hz	SUSPENDED
    1	alsa_output.pci-0000_00_1b.0.analog-stereo	module-alsa-card.c	s16le 2ch 48000Hz	SUSPENDED
    ```
Then for me, the script begins with :
```
### fixed params ###
M_screen = ["eDP1"]
M_pasink = ["alsa_output.pci-0000_00_1b.0.analog-stereo"]
####################
```

##### Dependencies
- Python3 (`aptitude install python3`)
- xrandr (`aptitude install xrandr`)
- pulseaudio (`aptitude install pulseaudio`)

##### Limitations

Currently, the program uses the stdout of the `xrandr` and `pactl` commands to evaluate the presence and the attributes of the guest screen. The formats of these outputs may change with versions of xrandr and pactl, and it would be necessary to adapt the script to handle the changes.

On my machine, I use `xrandr 1.5.0` and `pactl 10.0`. If your versions differ and the script does not work as expected, let me know :)