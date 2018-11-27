#! /bin/bash
### script pour ajuster la luminosité de l'écran eDP1
## tags : screen, ecran, backlight, retroeclairage, luminosite

## ce script permettra de contrôler la luminosite de l'écran en passant par la commande xbacklight
## pourquoi un script ?
##	- pour mettre un seuil bas au niveau de luminosité que peut atteindre l''écran. En effet, si on reste apppuyé sur le bouton, on préfère buter sur un écran à faible luminosité que sur un écran noir

## de la même façon que kbd_backlight, ce script sera accessible par lien symbolique depuis /usr/local/bin

# min que l'on souhaite autoriser (le max est déjà géré par xbacklight et vaut 100
min=1

# step: represent the difference between previous and next brightness
step=2
previous=$(xbacklight -get)

if [[ $1 == "inc" ]]
then 
	#echo "inc reconnu !  : on laisse xbacklight calculer seul la valeur d'arrivee"
	xbacklight -inc $step

elif [[ $1 == "dec" ]]
then
	#echo "dec reconnu ! "

	next=$(echo "$previous - $step" |bc -l)

	#echo "next vaut desormais : $next"
	if [[ $(bc -l <<<"$next <= $min") = 1 ]]
	then 
		:
		#echo "on ne diminuera pas davantage"
	else
		xbacklight -dec $step
	fi
else
	#echo "argument ni inc ni dec"
	exit 1
fi
exit 0

