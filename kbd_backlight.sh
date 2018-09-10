#!/bin/bash

## tags : kbd_backlight, retroeclairage_clavier
## source : https://wiki.archlinux.org/index.php/ASUS_G55VW#keyboard_backlight_script


## ce script permettra à tous les users d'écrire dans le fichier /sys/class/leds/asus::kbd_backlight/brightness, qui contrôle directement le rétroéclairage de clavier.
## il sera placé (via un lien) dans /usr/local/share et prendra le nom kbd_backlight
## on autorisera (pour chaque boot) l'ensemble des users à utiliser le script avec la manip suivante : 
# echo "/bin/bash /usr/local/bin/kbd_backlight allowusers" >> /etc/rc.local
## 
## et enfin, on ajoutera un alias à notre .zshrc : 
# alias -g "kbd_backlight"="/bin/bash /usr/local/bin/kbd_backlight"

## le script pourra notamment prendre les valeurs suivantes : 

#$ kbd_backlight up
#$ kbd_backlight down
#$ kbd_backlight max
#$ kbd_backlight off
#$ kbd_backlight night
#$ kbd_backlight 2
#$ kbd_backlight show

## et on se chargera par la suite de créer les raccourcis clavier qui vont bien :)
path="/sys/class/leds/asus::kbd_backlight"
#path="/sys/class/leds/asus\:\:kbd_backlight"

# max should be 3
max=$(cat ${path}/max_brightness)
# step: represent the difference between previous and next brightness
step=1
previous=$(cat ${path}/brightness)

function commit {
	if [[ $1 = [0-9]* ]]
	then 
		if [[ $1 -gt $max ]]
		then 
			next=$max
		elif [[ $1 -lt 0 ]]
		then 
			next=0
		else 
			next=$1
		fi
		echo $next >> ${path}/brightness
		exit 0
	else 
		exit 1
	fi
}

case "$1" in
 up)
     commit $(($previous + $step))
  ;;
 down)
     commit $(($previous - $step))
  ;;
 max)
	 commit $max
  ;;
 on)
	 $0 max
  ;;
 off)
	 commit 0
  ;;
 show)
	 echo $previous
  ;;
 night)
	 commit 1 
	 ;;
 allowusers)
	 # Allow members of users group to change brightness
#	 chgrp r2 ${path}/brightness
#	 chmod g+w ${path}/brightness
	 chmod a+w ${path}/brightness
  ;;
 disallowusers)
	 # Allow members of users group to change brightness
#	 chgrp root ${path}/brightness
#	 chmod g-w ${path}/brightness
	 chmod o-w ${path}/brightness
	 chmod g-w ${path}/brightness

  ;;
 *)
	 commit	$1
esac

exit 0
