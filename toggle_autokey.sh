#! /bin/bash

## toggle du programme autokey
user=$(whoami)

## autokey n'ouvre qu'une session à la fois par user, même si lancé plusieurs fois. On peut donc killer un pid unique
pid=$(ps -u $user -a | grep autokey | grep -v grep | grep -v toggle | awk '{print $1}')
echo $pid
if [[ $pid == '' ]]
then 
    autokey > /dev/null 2>&1 &
else
    kill $pid > /dev/null 2>&1 &
fi