#! /bin/bash

## parametres (use xinput --list to find your device name, or id)
touchpad_xinput_name="FocalTechPS/2 FocalTech Touchpad"

## récupération du statut enabled or disabled actuel
touchpad_status=$(xinput list-props 13 |awk '{if ($0 ~ "Device Enabled") {print $4}}')

# toggle
if [[ $touchpad_status == 1 ]]
then                 
    xinput disable "$touchpad_xinput_name"
elif [[ $touchpad_status == 0 ]]
then
    xinput enable "$touchpad_xinput_name"
else 
    exit 1
fi

exit 0