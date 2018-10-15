#! /bin/bash

## 0) params
mount_dir="/mnt/mtp_device"

## 1) recuperation des arguments utilisateur
action=$1

## 1) fonctions
function mount_mtp {
	## 1) creation du point de montage
    if [[ ! -d $1 ]]
    then
        mkdir -p $1
    fi
    ## montage  
    if jmtpfs -l > /dev/null 2>&1
    then
        jmtpfs $1 -o allow_other -o uid=1000 -o gid=1000
    else
        echo "jmtpfs must be installed"
    fi
}

function umount_mtp {
    umount $1
}

## execution
if [[ $action == "" ]]
then
    mount_mtp $mount_dir
elif [[ $action == "-u" ]]
then
    umount_mtp $mount_dir
else
    echo "without options, mount_mtp tries to mount any mtp connected device. With -u option, mount_mtp umounts the mtp device. There are currently no other options."
fi
