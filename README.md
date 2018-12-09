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
