"""
Fichier Main.py - Orchestrateur du projet Feu Tricolore.
Relie l'interface, la logique métier, l'animation Turtle et la base de données.
"""
import time
import random
import tkinter as tk
from turtle_scene import (init_screen, dessiner_decor_pro, TrafficLightVisual, 
                          THEME_JOUR, THEME_NUIT)
from vehicles import Vehicle
from traffic_light import TrafficLight
from scenarios import ScenarioManager
from database import Database
from logger import Logger
from gui import GUI

# --- INITIALISATION ---
# 1. Base de données et Logger
db = Database("simulation_feux.db")
logger = Logger(db)

# 2. Logique métier
feu_v = TrafficLight("Axe Vertical")
feu_h = TrafficLight("Axe Horizontal")
manager = ScenarioManager(feu_v, feu_h)

# 3. Graphismes (Turtle)
ecran = init_screen(THEME_JOUR)
# On cache le curseur turtle par défaut et on désactive les animations auto
import turtle
turtle.tracer(0) 

v_visuals = [
    TrafficLightVisual(-110, 110, "vertical"), 
    TrafficLightVisual(110, -110, "vertical")
]
h_visuals = [
    TrafficLightVisual(110, 110, "horizontal"),
    TrafficLightVisual(-110, -110, "horizontal")
]

# Dessin initial du décor
dessiner_decor_pro(THEME_JOUR)
ecran.update()

# 4. Variables de contrôle
running = False
liste_voitures = []

def update_callback(action, value=None):
    """Callback pour les interactions de la GUI."""
    global running, list_voitures
    if action == "play":
        running = True
    elif action == "pause":
        running = False
    elif action == "stop":
        running = False
        # Réinitialisation simple
        for v in liste_voitures:
            v.hideturtle()
            v.clear()
        liste_voitures.clear()
        ecran.update()
    elif action == "scenario":
        # Le manager a déjà été mis à jour par la GUI
        theme = THEME_NUIT if value == "Mode nuit" else THEME_JOUR
        ecran.bgcolor(theme["herbe"])
        dessiner_decor_pro(theme)

# 5. Interface Utilisateur (Tkinter)
# On récupère le canvas de turtle pour y intégrer Tkinter si possible, 
# mais ici on va créer une fenêtre Tkinter séparée ou utiliser celle de turtle.
root = tk.Tk()
root.title("Contrôle Carrefour")
root.geometry("250x450")
gui = GUI(root, feu_v, feu_h, manager, logger, update_callback)

# --- BOUCLE PRINCIPALE ---
def run_simulation():
    global running, liste_voitures
    
    if running:
        # 1. Mise à jour de la logique
        manager.update()
        
        # 2. Mise à jour des visuels des feux
        state_v = feu_v.get_state()
        state_h = feu_h.get_state()
        
        # Gestion du clignotement pour le visuel
        blink = (int(time.time() * 2) % 2 == 0) # Simple clignotement visuel
        
        for visual in v_visuals:
            visual.update_color(state_v, blink if state_v == "ORANGE_CLIGNOTANT" else False)
        for visual in h_visuals:
            visual.update_color(state_h, blink if state_h == "ORANGE_CLIGNOTANT" else False)
            
        # 3. Gestion des voitures
        params = manager.get_params()
        if random.randint(1, params["frequency"]) == 1:
            sens = random.choice(["nord", "sud", "est", "ouest"])
            v = Vehicle(sens, vitesse_max=params["speed"])
            liste_voitures.append(v)
            
        for v in liste_voitures:
            current_light = state_v if v.direction_depart in ["nord", "sud"] else state_h
            v.verifier_feu(current_light, liste_voitures)
            v.avancer(liste_voitures)
            
        # Nettoyage
        for v in liste_voitures[:]:
            if v.est_hors_ecran():
                v.hideturtle()
                v.clear()
                liste_voitures.remove(v)
        
        # Mise à jour GUI (indicateurs)
        gui.update_indicator()
        
        # Rendu final
        ecran.update()
    
    # Rappel de la fonction (équivalent de la boucle while mais non-bloquant pour Tkinter)
    root.after(40, run_simulation)

# Lancer la boucle de simulation
root.after(0, run_simulation)

# Démarrer l'interface (bloquant)
root.mainloop()
