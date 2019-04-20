#! /usr/bin/python3

# si vers 1 : 
#     - chope A, détermine K par setdiff avec W, puis xrandr --output K --off --output W --auto

# si vers 2 : 
#     - si clone : OK
#     - si 2 vers 2 : OK : xrandr --output B --rel_pos P --auto
#     - si 1 vers 2 : 
#         - signifie que A est length 1
#         - détermine W par setdiff avec A
#         - xrandr --output W --rel_pos A --auto

import sys
import subprocess as sp
import re
from itertools import chain 
import timeit

### fixed params ###
P_screen = ["eDP1"]
####################

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

def get_B_screen(P_screen, C_screens):
    """
    returns 'the other available screen', the B screen. B screen is dynamically found among connected screens (C_screens), only if there is just one connected screen in addition the the principal screen (P_screen) whose name is static (defined in params)
    """
    B_screen = set(C_screens) - set(P_screen)
    assert len(B_screen) <= 1, "Too much screens detected, can't define which one is your B screen. Stopping"
    return(list(B_screen))

def get_delta_screens(begin_list, end_list):
    """
    returns the list of screens to switch on or off to pass from begin_list to end_list
    """
    D_screens = set(begin_list) - set(end_list)
    return(list(D_screens))

## 0) détermination de B, A, C et W____
A_screens = get_A_screens()
C_screens = get_C_screens()
B_screen = get_B_screen(P_screen, C_screens)
# W_screens = # à monter selon les paramètres en entrée
# W_screens = B_screen
# W_screens = P_screen

## 1) cas vers 1 ____
K_screens = get_delta_screens(A_screens, W_screens)
K_screens_command = " ".join(["--output {} --off".format(ii) for ii in K_screens]) if len(K_screens) > 0 else ""

## détermination des écrans à allumer (T_screens)
T_screens = get_delta_screens(W_screens, A_screens)
T_screens_command = " ".join(["--output {} --auto".format(ii) for ii in T_screens]) if len(T_screens) > 0 else ""

## command :
command = " ".join([K_screens_command, T_screens_command])
if re.match(r"^\s?$", command) is None: ## ie si command est rens
    command = "xrandr " + command
    sp.Popen(command, shell = True)








v_full_shell="""
sp.Popen('xrandr |grep " connected" |awk \\'{print $1}\\'',shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()"""

v_python="""
xrandr_output = sp.Popen("xrandr",shell = True, stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
xrandr_output = [ii for ii in xrandr_output if re.search(r"(?<!dis)connected",ii) is not None]
xrandr_output = [re.split("\\s+",ii)[0] for ii in xrandr_output]"""

import timeit
timeit.timeit(v_full_shell, number = 500, globals=globals()) ## 2.21
timeit.timeit(v_python, number = 500, globals=globals()) ##1.82


class monitor:
    """des moniteurs des moniteurs encore des moniteurs"""
    
    ## objets de classe
    monitor_list = []
    
    def __init__(self, nom, primary = None, on = None, resolution = None, position_x = None, position_y = None, orientation = None, pa_sink = None, chosen_audio = None, use_it = None, near_monitors = {"above" : None ,"below" : None ,"right" : None ,"left" : None}, same_as_screen = None, only_screen = None):
    # def __init__(self, nom, primary = None, on = None, resolution = None, position_x = None, position_y = None, orientation = None, pa_sink = None, chosen_audio = None, use_it = None, same_as_screen = None, only_screen = None):
        self.nom = nom
        self.primary = primary
        self.on = on
        self.resolution = resolution
        self.position_x = position_x
        self.position_y = position_y
        self.orientation = orientation
        self.pa_sink = pa_sink
        self.chosen_audio = chosen_audio
        # self._above_screen = above_screen
        # self._below_screen = below_screen
        # self._right_screen = right_screen
        # self._left_screen = left_screen
        self._same_as_screen = same_as_screen
        self._only_screen = only_screen
        self._near_monitors = near_monitors
        
        ## à l'ajout d'un monitor, on récupère son nom dans la monitor_list
        monitor.monitor_list.append(self)
    
    @classmethod
    def initialize_screens(cls, instantiate = True):
        ## on réinit la liste, pour éviter que plusieurs init gonflent la liste de doublons
        del cls.monitor_list[:]
        
        ## récupération des infos de xrandr
        xrandr_output = sp.Popen("xrandr",stdout = sp.PIPE).communicate()[0].decode('utf-8').splitlines()
        
        ## filtre des écrans connectés
        xrandr_output = [ii for ii in xrandr_output if re.search(r"(?<!dis)connected",ii) is not None]
        
        ## extraction des infos de la sortie xrandr et remplissage de screen_list
        screen_list = []
        for ii in xrandr_output:
            # ii = xrandr_output[0]
            tmp_re = re.search(r"^(?P<name>[a-zA-Z0-9]*)\s*(?P<connected_status>\w*)\s*(?P<primary_status>primary)?\s*(?P<resolution>\d*x\d*.*)?\s*\(.*",ii)
            if tmp_re is not None:
                screen_list.append({
                     "nom": tmp_re.group('name')
                    ,"primary":{True:None,tmp_re.group('primary_status')=="primary":"primary"}[True]
                    ,"on":{True:None,tmp_re.group('resolution') is not None:"on"}[True]
                })
        
        ## création des objets écrans si instantiate == True
        if instantiate:
            for ii in screen_list:            
                    [monitor(
                        nom = ii["nom"]
                        ,primary = ii["primary"]
                        ,on = ii["on"])
                        for ii in screen_list]
        return(screen_list)
    
    def __repr__(self):
        tmp_repr = []
        ## transfo du dico en liste de tuples, puis sort selon la key
        tmp = [(ii[0], ii[1]) for ii in self.__dict__.items()]
        tmp.sort(key = lambda x:x[0])
        for (clef, valeur) in tmp:
            valeur = "" if valeur is None else valeur
            tmp_repr.append("   " + clef + " : " + str(valeur))
        return("\n"+"\n".join(tmp_repr)+"\n")
        
    def initialize_position(self):
        self.position_x = 0
        self.position_y = 0
    
    def initialize_position_if_needed(self):
        if self.position_x is None and self.position_y is None :
            self.initialize_position()
        
    @classmethod
    def assert_is_monitor(cls,a):
        if not type(a) is monitor:
            raise TypeError("your object is not a monitor")
            
    # def set_relative_pos(self, other_monitor, relative_position):
    #     ## check other_monitor
    #     monitor.assert_is_monitor(other_monitor)    
    ## set relative positions according to other monitor
    
    ## les attributs de positionnement relatifs : pourront sauter si notre dictionnaire property-like near_monitors fonctionne
    ## above
    # @property
    # def above_screen(self):
    #     return(self._above_screen)
        
    # @above_screen.setter
    # def above_screen(self, new_screen):
    #     monitor.assert_is_monitor(new_screen)
    #     if self == new_screen:
    #         raise ValueError("You can't place a screen next to itself ! To twin a screen, you want to use the same_as_screen attribute")
    #     self._above_screen = new_screen
        
    # @above_screen.deleter
    # def above_screen(self):
    #     self._above_screen = None
        
    # ## below
    # @property
    # def below_screen(self):
    #     return(self._below_screen)
        
    # @below_screen.setter
    # def below_screen(self, new_screen):
    #     monitor.assert_is_monitor(new_screen)
    #     if self == new_screen:
    #         raise ValueError("You can't place a screen next to itself ! To twin a screen, you want to use the same_as_screen attribute")
    #     self._below_screen = new_screen
        
    # @below_screen.deleter
    # def below_screen(self):
    #     self._below_screen = None
        
    # ## right
    # @property 
    # def right_screen(self):
    #     return(self._right_screen)
        
    # @right_screen.setter
    # def right_screen(self, new_screen):
    #     monitor.assert_is_monitor(new_screen)
    #     if self == new_screen:
    #         raise ValueError("You can't place a screen next to itself ! To twin a screen, you want to use the same_as_screen attribute")
    #     self._right_screen = new_screen
        
    # @right_screen.deleter
    # def right_screen(self):
    #     self._right_screen = None
        
    # ## left
    # @property 
    # def left_screen(self):
    #     return(self._left_screen)
        
    # @left_screen.setter
    # def left_screen(self, new_screen):
    #     monitor.assert_is_monitor(new_screen)
    #     if self == new_screen:
    #         raise ValueError("You can't place a screen next to itself ! To twin a screen, you want to use the same_as_screen attribute")
    #     self._left_screen = new_screen
        
    # @left_screen.deleter
    # def left_screen(self):
    #     self._left_screen = None
    
    ## same_as_screen
    @property 
    def same_as_screen(self):
        return(self._same_as_screen)
    
    @same_as_screen.setter
    def same_as_screen(self, new_screen):
        ## vérification de la valeur donnée : c'est bien une instance de monitors, ou alors None
        if new_screen is not None:
            monitor.assert_is_monitor(new_screen)
        
        ## vérification qu'on est pas en train de mettre un monitor iso à lui-même
        if self == new_screen:
            raise ValueError("your screen is already iso with itself !")
        
        ## prévenance du reinit de near_monitors si lui et same_as_screen non None
        if new_screen is not None and max([ii is not None for ii in self._near_monitors.values()]):
            print("/!\\ : near_monitors configuration reinitialized")
            # for (ii,jj) in self._near_monitors.items(): 
            #     jj = None
            del self.near_monitors
        
        ## prévenance du réinit de _only_screen :
        if new_screen is not None and self._only_screen is True:
            print("/!\\ : only_screen configuration reinitialized")
            del self.only_screen
        
        ## affectation des nouvelles valeurs, conservation des anciennes
        self._same_as_screen = new_screen
        
    @same_as_screen.deleter
    def same_as_screen(self):
        self._same_as_screen = None
    
    ## only_screen
    @property
    def only_screen(self):
        return(self._only_screen)
        
    @only_screen.setter
    def only_screen(self, new_status):
        ## vérification de la valeur donnée : c'est bien True ou False (None est la valeur donnée automatiquement par la classe monitor)
        if not new_status in [True, False]:
            raise ValueError("only_screen is a bolean flag : must be True or False")
       
        ## prévenance du reinit de near_monitors si lui et only_screen non None
        if new_status is True and max([ii is not None for ii in self._near_monitors.values()]):
            print("/!\\ : near_monitors configuration reinitialized")
            # for (ii,jj) in self._near_monitors.items(): 
            #     jj = None
            del self.near_monitors
        
        ## prévenance du réinit de _same_as_screen :
        if new_status is True and self._same_as_screen is not None:
            print("/!\\ : same_as_screen configuration reinitialized")
            del self.same_as_screen
        
        ## affectation des nouvelles valeurs, conservation des anciennes
        self._only_screen = new_status
            
    @only_screen.deleter
    def only_screen(self):
        self._only_screen = None
                
    ## near_monitors
    @property
    def near_monitors(self):
        return(self._near_monitors)
    
    @near_monitors.setter
    def near_monitors(self, new_near_monitors):
        ## vérification des clefs du dico : les mots clefs doivent être les bons
        possible_positions = ["above","below","right","left"]
        if not (min([ii in possible_positions for ii in new_near_monitors.keys()])):
            raise ValueError('keys of the near_monitors dict must be among "above","below","right",and "left"')
            
        ## vérification des valeurs du dico : ce sont bien tous les instances de monitors, ou alors None
        [monitor.assert_is_monitor(ii) for ii in new_near_monitors.values() if ii is not None]
        
        ## vérification qu'on est pas en train de mettre un monitor à côté de lui-même
        if max([self == ii for ii in new_near_monitors.values()]):
            raise ValueError("You can't place a screen next to itself ! To twin a screen, you want to use the same_as_screen attribute")
        
        ## prévenance du réinit de _same_as_screen :
        if max([ii is not None for ii in new_near_monitors.values()]) and self._same_as_screen is not None:
            print("/!\\ : same_as_screen configuration reinitialized")
            del self.same_as_screen
        
        ## prévenance du réinit de _same_as_screen :
        if max([ii is not None for ii in new_near_monitors.values()]) and self._only_screen is True:
            print("/!\\ : only_screen configuration reinitialized")
            del self.only_screen
                    
        ## affectation des nouvelles valeurs, conservation des anciennes
        for (ii,jj) in new_near_monitors.items():
            self._near_monitors[ii] = jj
        
    @near_monitors.deleter
    def near_monitors(self):
        for (ii) in self._near_monitors.keys():
            self._near_monitors[ii] = None
        
    @classmethod
    def list_screens_on(cls):
        return([ii for ii in cls.monitor_list if ii.on=='on'])
    
    @classmethod
    def list_screens_to_be_turned_on(cls):
        ## on chope le premier écran ayant un flag only_screen True, 
        tmp = [ii for ii in cls.monitor_list if ii._only_screen==True]
        ## on prévient s'il y avait plusieurs écrans avec only_screen à True
        if len(tmp) > 1:
            print("/!\\ : several screens are set to be alone. We chose " + chosen_screen.nom)
        ## si on a au moins 1 écran en only screen, on return l'écran en question
        elif len(tmp) >= 1 :
            chosen_screen = tmp[0]
            return([chosen_screen])
        
        ## sinon, on cherche si on a des same_as_screen
        ## 1 : les écrans qui ont un attribut _same_as_screen non nul
        tmp = [ii for ii in cls.monitor_list if ii._same_as_screen is not None]
        ## 2 : niveau du dessous
        tmp2 = [ii._same_as_screen for ii in tmp]
        
        tmp.extend(tmp2)
        if len(tmp) >= 1:
            return(list(set(tmp)))
        
        ## sinon, on cherche si on a des near_monitors
        ## 1 : les écrans qui ont un attribut _near_monitors non nul
        tmp = [ii for ii in cls.monitor_list if ii._near_monitors is not None]
        ## 2 : niveau du dessous
        tmp2 = [ii._near_monitors for ii in tmp]
        
        tmp.extend(tmp2)
        if len(tmp) >= 1:
            return(list(set(tmp)))

a/b
b/c

a = [1]
a = [[1]]
a.append([2,3])
a.extend([2,3])

type(a) is list
[ii for little in a for ii in little if type(little) is not list]

[ii if type(ii) is list else for ii in a if type(ii) is list]

[ii for little in a for ii in little]
[ii for little in a for ii in little]
if type(little) is list else 0 

def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def flatten2(S):
    if type(S) != list:
        return([S])
    elif len(S) == 0:
        return(S)
    else:
        return flatten2(S[0]) + flatten2(S[1:])

flatten2(a)
a = [1,[2,3]]
a = [1,[2,3],[4,[5,6,7]]]
a[1:]
    cas 3 : return(f2(1) + f2([[2,3]]))
    f2(1) :
        cas 1: return[1]
    f2([[2,3]]) : 
        cas 3 : return(f2([2,3]) + f2([]))


## test 1 : pas concluant
def funct1(x):
    return(id(x))
    # return(id(x[0]))

def funct2(x):
    # return(id(x))
    return(id(x[0]))
    
a=[1,2]
print("vraie adresse de a " + str(id(a)) + " vs " + str(funct1(a)))
print("vraie adresse de a[0] " + str(id(a[0])) + " vs " + str(funct1(a[0])))

a="a"
print("vraie adresse de a " + str(id(a)) + " vs " + str(funct1(a)))
print("vraie adresse de a[0] " + str(id(a[0])) + " vs " + str(funct1(a[0])))

## test 2 : pas concluant
def funct1(x):
    return(x + [2])
    # return(id(x[0]))

def funct2(x):
    return(x.append(2))
    # return(id(x[0]))    

a = [1]
funct1(a)
b = funct2(a)


a + [2]
def funct2(x):
    # return(id(x))
    return(id(x[0]))

id(a[0])
    
print(id)
a[1:]
flatten2(a)
a[1:]
    
    
flatten(a)
a[:1] == a[0]

a[0][:1]


flatten(a)
[ii for jj in a for first in ii]
list(chain.from_iterable(a))
list(chain(*a))

b = [jj for ii in a for jj in a]
from itertools import chain
# l=[[1,2,3],[4,5,6], [7], [8,9]]*99
l=[[1,2,3],[4,5,6], [7], [8,9]]
list(chain.from_iterable(l))
        
        
        
    
    
    
    @classmethod
    def update_panel(cls):
        
            
        modop : 
        monter une méthode de classe qui : 
            - renvoit la liste des écrans actuellement on
            - renvoit la liste des écrans qui doivent être allumés après la transformation du layout (selon only_screen, same_as_screen et near_monitor, dans cet ordre)
            - éteint les écrans donnés dans en paramètre dans une liste (ou éteint les écrans en diff entre deux listes : celle des actuellement on et celle des future_on)
            
            - pour only_screen : 
                - (fonction 1) :
                    - prend la liste à allumer en entrée (un seul screen donc)
                    - si nb_screens à allumer > 1, la sorte selon qui est déjà allumé, pour mettre un déjà allumé en premier
                    - et l'allume
  
            - pour same_as_screen
                - (fonction 1) :
                    - prend la liste à allumer en entrée (un seul screen donc)
                    - si nb_screens à allumer > 1, la sorte selon qui est déjà allumé, pour mettre un déjà allumé en premier
                    - et l'allume
             - (fonction 2) :
                    - puis branche les suivants en same_as ce premier
                    
            - pour near_monitors : 
                - (fonction 1) :
                    - prend la liste à allumer en entrée (un seul screen donc)
                    - si nb_screens à allumer > 1, la sorte selon qui est déjà allumé, pour mettre un déjà allumé en premier
                    - et l'allume
                - (fonction 3) :
                    - initialise une liste d'écrans déjà traités, avec le premier écran de la liste
                    - positionne les écrans adjacents de ce screen sur les côtés de ce screen s'il ne sont pas déjà dans la liste des écrans traités, puis les append dans la liste des écrans traités
                    - puis s'applique en récursive à ces écrans
                    - la fonction fait un return (clause if de la fonction récursive) quand l'écran à traiter est déjà dans la liste des écrans traités
                        
                    
                


res = monitor.initialize_screens()
s1 = monitor.monitor_list[0]
s1.on
s2 = monitor.monitor_list[0]
s3 = monitor(nom = "screen3!")
s1.near_monitors = {"above" : s3}
s1.same_as_screen = s3
s1.only_screen = True
## reste à faire : 
# - maintenant qu'on a les positionnements relatifs : 
    - fonction de mise en place sur la grille : Dans l'idée il faut simplement mettre tout le monde à off hormis l'actif (ou au moins un actif qui restera actif), puis partir du moniteur actif et positionner tous les autres en fonction. Donc pas spécialement besoin de créer la grile avec des coordonnées au préalable si ?
    Dans cette fonction, on aura donc : 
        - un check des écrans avec valeurs "_"
        - une vérif de si un en mode only et seul à être en mode only. Plus message de prévenance si d'autres screens avaient des "_" remplis également, qui ne sont donc pas pris en compte.
        - puis une vérif des same_as, et message de prévenance si d'autres screens avaient des "_" de near_monitors remplis également, qui ne sont donc pas pris en compte.
        - puis une vérif des near_monitors : 
            - et fonction récursive pour lancer des commandes xrandr à la chaîne (ou incrémenter une unique commande xrandr à lancer ensuite, mais plus compliqué). Eteindre tous les écrans, puis partir d'un des écrans du panel, l'allumer, puis positionner au fur et à mesure les autres écrans autour de lui
            
## bosser sur repr :
## soit ne faire qu'afficher le nom du screen et créer un méthode pour afficher les détails de configuration de l'écran (plus simple), soit gérer les cas particuliers (par ex pour l'affichage de _near_monitors)
## masquer les objets _cachés ?


s1 = monitor.monitor_list[0]

s1.above_screen = s1

monitor.monitor_list[0].set_above_of('e')
type(monitor.monitor_list[0]) is monitor

a = 1
b = 3
{
"nom": 2 if a == 2 else 'bob' if b == 2 else 'bobby'
}
                
                
res = monitor(nom = "bob")
res = monitor.initialize_screens()
monitor.monitor_list

len(dir(monitor.monitor_list[0]))
len(monitor.monitor_list)
list(monitor.monitor_list[0].__dict__)
"\n".join([ii + " : " + jj for (ii,jj) in monitor.monitor_list[0].__dict__.items() if jj is not None])
"\n".join([ii + " : " + jj for (ii,jj) in [oo.__dict__.items() for oo in monitor.monitor_list] if jj is not None])
len([oo.__dict__.items() for oo in monitor.monitor_list])

tmp_repr = []
tmp_ii = 1
for ii in [oo.__dict__.items() for oo in monitor.monitor_list]:
    tmp_repr.append("screen" + str(tmp_ii))
    tmp_ii +=1        
    for (clef, valeur) in ii:    
        if valeur is not None :
            tmp_repr.append("   " + clef + " : " + valeur)
"\n".join(tmp_repr)
print("\n".join(tmp_repr))

len(monitor.monitor_list)
tmp
try:
    del(monitor)
except: 
    print("bob")
    
inspect.ismethod(monitor.monitor_list[0])



tmp = monitor(nom = "first_monitor")
monitor.monitor_list[0]

puis : une boucle pour initialiser tous les monitors en fonction des screens connectés rendus par xrandr
initialiser également le chosen_audio par défaut ?

plus_ou_moins = lambda nb=85, essai=-1: (
    "Gagné !" if essai == nb else
    plus_ou_moins(
        nb,
        int(input(
              {essai < nb: "C'est plus !\n",
               essai > nb: "C'est moins !\n",
               essai < 0: ""}[True]
              + "Entrez un nombre positif: "))))
plus_ou_moins()

a = 3
b={a == 1: "1\n",
a == 2: "2\n"}[True]

age = 17
print({True: "18 ans tout pile",
    age < 18: "mineur",
    age > 18: "majeur"}[True])
{True: "18 ans tout pile",
    age < 18: "mineur",
    age < 18: "franchement mineur",
    age > 18: "majeur"}[True]

entry="baz"
def step1():
    print("1")

def step2():
    print("2")

def step3():
    print("3")

def step4():
    print("4")

step5=lambda:print("5")

for step in {
    "foo": (step1, step2, step3, step4, step5),
    "bar": (step3, step4, step5),
    "baz": (step4, step5)
}.get(entry, ()): step()

for step in {
    True: lambda:print("bob"),
    "foo": (step1, step2, step3, step4, step5),
    "bar": (step3, step4, step5),
    "baz": (step4, step5)
}.get(entry, ()): step()

