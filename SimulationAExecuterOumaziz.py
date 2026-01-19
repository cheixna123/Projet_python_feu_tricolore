import time
import random
import turtle
import _tkinter
from turtle_scene import (init_screen, dessiner_decor_pro, TrafficLightVisual, 
                          dessiner_toute_l_interface, THEME_JOUR, THEME_NUIT)
from vehicles import Vehicle

# --- CONFIGURATION INITIALE ---
mode_simulation = "NORMAL"
theme_actuel = THEME_JOUR
ecran = init_screen(theme_actuel)

# Tortues séparées pour optimiser les redessins
pen_decor = turtle.Turtle()
pen_decor.hideturtle()
pen_ui = turtle.Turtle()
pen_ui.hideturtle()

def redraw_all():
    # On redessine le décor et l'interface
    dessiner_decor_pro(theme_actuel, pen_decor)
    dessiner_toute_l_interface(pen_ui, mode_simulation)
    ecran.update()

redraw_all()

# --- CRÉATION DES FEUX ---
# Positionnés sur les coins des trottoirs
feu_N = TrafficLightVisual(-110, 110, "vertical")  # Gère le flux Nord -> Sud
feu_S = TrafficLightVisual(110, -110, "vertical")  # Gère le flux Sud -> Nord
feu_E = TrafficLightVisual(110, 110, "horizontal") # Gère le flux Est -> Ouest
feu_W = TrafficLightVisual(-110, -110, "horizontal")# Gère le flux Ouest -> Est

# --- VARIABLES D'ÉTAT ---
etat_cycle = "VERT_V"
timer_cycle = 0
DUREE_VERT = 120
DUREE_ORANGE = 40
DUREE_ALL_RED = 30
liste_voitures = []

def update_visuels_feux(etat_v, etat_h, flash=False):
    feu_N.update_color(etat_v, flash)
    feu_S.update_color(etat_v, flash)
    feu_E.update_color(etat_h, flash)
    feu_W.update_color(etat_h, flash)

def gerer_clic(x, y):
    global mode_simulation, theme_actuel, timer_cycle, etat_cycle
    # Détection des clics sur le bandeau supérieur (y entre 350 et 400)
    if 350 <= y <= 400:
        if -210 <= x <= -100: mode_simulation = "NORMAL"
        elif -90 <= x <= 20: mode_simulation = "PANIQUE"
        elif 30 <= x <= 140: mode_simulation = "NUIT"
        elif 150 <= x <= 260: mode_simulation = "PANNE"
        
        # Mise à jour immédiate
        theme_actuel = THEME_NUIT if mode_simulation == "NUIT" else THEME_JOUR
        ecran.bgcolor(theme_actuel["herbe"])
        timer_cycle = 0
        etat_cycle = "VERT_V"
        redraw_all()

ecran.onclick(gerer_clic)

# ==================================
# === BOUCLE PRINCIPALE DU JEU ===
# ==================================
encours = True

while encours:
    try:
        time.sleep(0.04)
        timer_cycle += 1
        
        # 1. LOGIQUE DES FEUX SELON LE MODE
        v_light, h_light = "ROUGE", "ROUGE"
        flash_orange = (timer_cycle // 10) % 2 == 0

        if mode_simulation in ["NUIT", "PANNE"]:
            v_light = h_light = "ORANGE_CLIGNOTANT"
        else:
            if etat_cycle == "VERT_V":
                v_light, h_light = "VERT", "ROUGE"
                if timer_cycle >= DUREE_VERT: etat_cycle = "ORANGE_V"; timer_cycle = 0
            elif etat_cycle == "ORANGE_V":
                v_light, h_light = "ORANGE", "ROUGE"
                if timer_cycle >= DUREE_ORANGE: etat_cycle = "ALL_RED_V_TO_H"; timer_cycle = 0
            elif etat_cycle == "ALL_RED_V_TO_H":
                v_light, h_light = "ROUGE", "ROUGE"
                if timer_cycle >= DUREE_ALL_RED: etat_cycle = "VERT_H"; timer_cycle = 0
            elif etat_cycle == "VERT_H":
                v_light, h_light = "ROUGE", "VERT"
                if timer_cycle >= DUREE_VERT: etat_cycle = "ORANGE_H"; timer_cycle = 0
            elif etat_cycle == "ORANGE_H":
                v_light, h_light = "ROUGE", "ORANGE"
                if timer_cycle >= DUREE_ORANGE: etat_cycle = "ALL_RED_H_TO_V"; timer_cycle = 0
            elif etat_cycle == "ALL_RED_H_TO_V":
                v_light, h_light = "ROUGE", "ROUGE"
                if timer_cycle >= DUREE_ALL_RED: etat_cycle = "VERT_V"; timer_cycle = 0

        update_visuels_feux(v_light, h_light, flash_orange)

        # 2. GESTION DES VOITURES
        chance_spawn = 35 
        if mode_simulation == "PANIQUE": chance_spawn = 12
        elif mode_simulation == "NUIT": chance_spawn = 60
        
        if random.randint(1, chance_spawn) == 1:
            sens = random.choice(["nord", "sud", "est", "ouest"])
            liste_voitures.append(Vehicle(sens))

        for voiture in liste_voitures:
            voiture.verifier_feu(v_light if voiture.direction_depart in ["nord", "sud"] else h_light, liste_voitures)
            voiture.avancer(liste_voitures)

        # 3. NETTOYAGE
        for v in liste_voitures[:]:
            if v.est_hors_ecran():
                v.hideturtle()
                v.clear()
                liste_voitures.remove(v)

        ecran.update()
        
    except (turtle.Terminator, _tkinter.TclError, KeyboardInterrupt):
        encours = False
        break
    except Exception as e:
        print(f"Erreur simulation : {e}")
        encours = False
        break

try:
    ecran.mainloop()
except:
    pass