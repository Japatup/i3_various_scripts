#! /usr/bin/python3

## détection du sink pulse audio en cours d'utilisation (local, hdmi ou autre) et gestion du volume

import re
import sys
import subprocess as sp

## 1) récupération de la demande user (du paramère qu'il a mis après volume) ____
args = sys.argv[1:]
# args = ["nom_programme","-5%"][1:]
# args = ["nom_programme","mutee"][1:]

if len(args) != 1:
    raise ValueError("la fonction prend un unique argument !")
    
asked_volume = args[0]
tmp = re.match(r"^([-\+]?\d+%|mute)$",asked_volume)
if tmp is None:
	raise ValueError("""
    l'argument passe a la fonction doit etre : 
    - un volume absolu (80% par ex)
    - un niveau relatif (+5%, -10% par ex)
    - ou la commande mute pour activer / desactiver le son""")

## 2) récupération du running sink, ou du sink par défaut si aucun running
tmp = sp.Popen('pactl list sinks short'.split(), stdout=sp.PIPE)
output, _ = tmp.communicate()
tmp = output.splitlines()
running_sinks = [ii.split(sep = b"\t")[1] for ii in tmp if b"RUNNING" in ii]

## si on n'a pas d'active sink, on remonte le sink par défaut
if len(running_sinks) > 1:
    raise Exception("comment peut-on avoir deux sinks RUNNING au même moment !? --> à creuser")
elif len(running_sinks) == 0:
    tmp = sp.Popen('pacmd stat'.split(), stdout=sp.PIPE)
    output, _ = tmp.communicate()
    tmp = output.splitlines()
    running_sinks = [ii.split(b":")[1] for ii in tmp if b"Default sink name" in ii]
    running_sinks

## le main sink, en str
main_sink = running_sinks[0].decode('utf-8').strip()

## 3) sur le sink choisi, on modifie le volume comme demandé dans les paramètres passés à la fonction

if asked_volume == "mute":
    sp.Popen(["pactl","set-sink-mute",main_sink,"toggle"])
else:
    sp.Popen(["pactl","set-sink-volume",main_sink,asked_volume])
