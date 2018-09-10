#!/bin/bash

## tags : airplane mode, mode avion, fn f2, nmcli, raccourci clavier, net 
## on, net off

## ce script permettra plusieurs choses :
##	- que tous les users puissent écrire dans le fichier /sys/class/leds/asus-wireless::airplane/brightness
##	- de modifier le statut nmcli networking, et de synchroniser la led du mode avion

## il sera placé (via un lien) dans /usr/local/bin et prendra le nom plane_mode.sh
## on autorisera (pour chaque boot) l'ensemble des users à utiliser le script avec la manip suivante : 
# echo "/bin/bash /usr/local/bin/plane_mode allowusers" >> /etc/rc.local
## 
## et enfin, on ajoutera un alias à notre .zshrc : 
# alias "plane_mode"="/bin/bash /usr/local/bin/plane_mode"

## le script pourra notamment prendre les valeurs suivantes : 

#$ plane_mode toggle 
#$ plane_mode on
#$ plane_mode off
#$ plane_mode allowusers

## et on se chargera par la suite de créer les raccourcis clavier qui vont bien :)
path="/sys/class/leds/asus-wireless::airplane"

# echo "vérif que le path est bon : "
# echo $(ls $path)

#previous=$(cat ${path}/brightness)

function turn_led_on {
	echo 1 > ${path}/brightness
}

function turn_led_off {
	echo 0 > ${path}/brightness
}

function turn_wifi_on {
    /bin/bash -c "nmcli radio wifi on"
    # nmcli networking on
}

function turn_wifi_off {
    /bin/bash -c "nmcli radio wifi off"
    # nmcli networking off
}

case "$1" in
 on)
    turn_wifi_off
	turn_led_on
	exit 0
  ;;
 off)
	turn_wifi_on
	turn_led_off
	exit 0
  ;;
 toggle)
 	previous=$(nmcli radio wifi)
	if [[ $previous = "activé" ]]
	then
		turn_wifi_off
		turn_led_on
		exit 0
	elif [[ $previous = "désactivé" ]]
	then
		turn_wifi_on
		turn_led_off
		exit 0
	else
		echo "en previous, on a ca : $previous"
		exit 1
	fi
  ;;
 sync_led)
 	previous=$(nmcli radio wifi)
	if [[ $previous = "activé" ]]
	then
		turn_led_off
		exit 0
	elif [[ $previous = "désactivé" ]]
	then
		turn_led_on
		exit 0
	else
		echo "en previous, on a ca : $previous"
		exit 1
	fi
	 exit 0
  ;;
 allowusers)
	 chmod a+w ${path}/brightness
  ;;
 disallowusers)
	 chmod o-w ${path}/brightness
	 chmod g-w ${path}/brightness
	 exit 0
  ;;
 *)
	 echo "on n'est rentré dans aucune condition --> revoir la valeur de l'argument passé au script"
	 exit 1
  ;;
esac
