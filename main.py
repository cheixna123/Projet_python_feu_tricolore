"""
Fichier Main.py - Orchestrateur du projet Feu Tricolore.
Version Finale Intégrée.
"""
import time
import random
import turtle
import _tkinter
from turtle_scene import (init_screen, dessiner_decor_pro, TrafficLightVisual, 
                          dessiner_toute_l_interface, THEME_JOUR, THEME_NUIT)
from vehicles import Vehicle
from traffic_light import TrafficLight
from scenarios import ScenarioManager
from database import Database
from logger import Logger

# --- 1. INITIALISATION DES SYSTÈMES ---
# Base de données et Logger
db = Database("simulation_feux.db")
logger = Logger(db)

# Logique métier (Modèle)
feu_v = TrafficLight("Axe Vertical")
feu_h = TrafficLight("Axe Horizontal")
manager = ScenarioManager(feu_v, feu_h)
logger.log_action("SYSTEM", "Démarrage simulation", "INIT", "Normale")

# --- 2. INITIALISATION GRAPHIQUE ---
theme_actuel = THEME_JOUR
ecran = init_screen(theme_actuel)

# Tortues pour le rendu
pen_decor = turtle.Turtle()
pen_decor.hideturtle()
pen_ui = turtle.Turtle()
pen_ui.hideturtle()

# Création des visuels de feux
feu_N = TrafficLightVisual(-110, 110, "vertical")  # Gère le flux Nord -> Sud
feu_S = TrafficLightVisual(110, -110, "vertical")  # Gère le flux Sud -> Nord
feu_E = TrafficLightVisual(110, 110, "horizontal") # Gère le flux Est -> Ouest
feu_W = TrafficLightVisual(-110, -110, "horizontal")# Gère le flux Ouest -> Est

visuals = [feu_N, feu_S, feu_E, feu_W]

# Liste des voitures
liste_voitures = []

# --- 3. VARIABLES GLOBALES DE CONTRÔLE ---
is_paused = False
manual_mode_active = False # Pour savoir si on affiche les boutons manuels

def redraw_all():
    """Redessine le décor, la structure des feux et l'interface."""
    # 1. Décor (Fond)
    dessiner_decor_pro(theme_actuel, pen_decor)
    
    # 2. Structure des feux (Poteaux)
    for visual in visuals:
        visual.dessiner_structure()
        state = feu_v.get_state() if visual in [feu_N, feu_S] else feu_h.get_state()
        visual.update_color(state, force=True)

    # 3. Interface
    # Mapping du nom du scénario
    mode_map = {
        "Normale": "NORMAL",
        "Heure de pointe": "PANIQUE",
        "Mode nuit": "NUIT",
        "Manuel": "PANNE"
    }
    mode_visuel = mode_map.get(manager.get_current_scenario(), "NORMAL")
    manual_active = (manager.get_current_scenario() == "Manuel")
    
    dessiner_toute_l_interface(pen_ui, mode_visuel, is_paused, manual_active)
    
    ecran.update()

redraw_all()

# --- 4. GESTION DES CLICS (CONTROLEUR) ---
def gerer_clic(x, y):
    global theme_actuel, is_paused, liste_voitures
    
    current_scen = manager.get_current_scenario()
    manual_active = (current_scen == "Manuel")
    need_redraw = False

    # Le panneau est à X > 150. Les boutons commencent à X=240.
    if x < 240:
        return

    # LIGNE 1 : SCÉNARIOS (Y=285 -> zone [285, 310])
    if 285 <= y <= 310:
        nouveau_scenario = None
        if 240 <= x <= 310: nouveau_scenario = "Normale"
        elif 315 <= x <= 385: nouveau_scenario = "Heure de pointe"
        elif 390 <= x <= 460: nouveau_scenario = "Mode nuit"
        elif 465 <= x <= 535: nouveau_scenario = "Manuel"
        
        # ... (reste inchangé)
        if nouveau_scenario and nouveau_scenario != current_scen:
            manager.set_scenario(nouveau_scenario)
            logger.log_action("BOUTON", f"Changement vers {nouveau_scenario}", feu_v.get_state(), nouveau_scenario)
            
            # Gestion immédiate du thème
            new_theme = THEME_NUIT if nouveau_scenario == "Mode nuit" else THEME_JOUR
            if theme_actuel != new_theme:
                theme_actuel = new_theme
                ecran.bgcolor(theme_actuel["herbe"])
            
            need_redraw = True

    # LIGNE 2 : PLAYBACK (Y=235 -> zone [235, 260])
    elif 235 <= y <= 260:
        if 240 <= x <= 310: # PLAY
            if is_paused:
                is_paused = False
                logger.log_action("PLAY", "Reprise simulation", feu_v.get_state(), current_scen)
                need_redraw = True
                
        elif 315 <= x <= 385: # PAUSE
            if not is_paused:
                is_paused = True
                logger.log_action("PAUSE", "Pause simulation", feu_v.get_state(), current_scen)
                need_redraw = True
                
        elif 390 <= x <= 460: # STOP
            is_paused = True
            logger.log_action("STOP", "Arrêt simulation", feu_v.get_state(), current_scen)
            need_redraw = True
            
        elif 465 <= x <= 535: # RESET
            is_paused = True
            # Reset voitures
            for v in liste_voitures:
                v.hideturtle()
                v.clear()
            liste_voitures.clear()
            # Reset Logic
            manager.set_scenario("Normale") # Retour au défaut
            theme_actuel = THEME_JOUR
            ecran.bgcolor(theme_actuel["herbe"])
            logger.log_action("RESET", "Réinitialisation complète", "ROUGE", "Normale")
            need_redraw = True

    # LIGNE 3 : MANUEL (Y=180 -> zone [180, 205])
    elif manual_active and 180 <= y <= 205:
        action = None
        if 240 <= x <= 350: # SWITCH VERTICAL
            action = "SWITCH_V"
        elif 360 <= x <= 470: # SWITCH HORIZONTAL
            action = "SWITCH_H"
            
        if action:
            def cycle_next(light):
                s = light.get_state()
                nex = "VERT" if s == "ROUGE" else "ORANGE" if s == "VERT" else "ROUGE"
                light.set_state(nex)
                
            if action == "SWITCH_V":
                cycle_next(feu_v)
            else:
                cycle_next(feu_h)
            
            logger.log_action("MANUEL", f"Action {action}", feu_v.get_state(), current_scen)
            need_redraw = True

    if need_redraw:
        redraw_all()

ecran.onclick(gerer_clic)

# --- 5. BOUCLE PRINCIPALE (AFFICHEUR) ---
encours = True

while encours:
    try:
        # Toujours rafraîchir la boucle pour recevoir les événements
        # Si pause, on ralentit juste un peu ou on skip l'update logique
        
        if is_paused:
            ecran.update()
            time.sleep(0.1)
            continue
            
        time.sleep(0.04) # Environ 25 FPS
        
        # A. Mise à jour de la logique
        # En mode MANUEL, le manager ne fait rien de spécial à part initialiser
        # Mais on veut garder le timer pour d'éventuels clignotements
        manager.update()
        
        # B. Récupération des états
        etat_v = feu_v.get_state()
        etat_h = feu_h.get_state()
        flash_orange = feu_v.is_night_mode and feu_v.blink_state
        
        # C. Mise à jour des visuels
        # On adapte : 
        display_v = "ORANGE" if etat_v == "ORANGE_CLIGNOTANT" else etat_v
        display_h = "ORANGE" if etat_h == "ORANGE_CLIGNOTANT" else etat_h
        
        do_flash = (etat_v == "ORANGE_CLIGNOTANT") and (int(time.time()*2) % 2 == 0)
        
        feu_N.update_color(display_v, do_flash)
        feu_S.update_color(display_v, do_flash)
        feu_E.update_color(display_h, do_flash)
        feu_W.update_color(display_h, do_flash)

        # D. Gestion des voitures
        params = manager.get_params()
        
        # Spawn
        if random.randint(1, params["frequency"]) == 1:
            sens = random.choice(["nord", "sud", "est", "ouest"])
            liste_voitures.append(Vehicle(sens, vitesse_max=params["speed"]))

        # Déplacement
        for voiture in liste_voitures:
            # On détermine quel feu regarde la voiture
            feu_concerne = etat_v if voiture.direction_depart in ["nord", "sud"] else etat_h
            
            # Compatibilité : les véhicules attendent "ORANGE_CLIGNOTANT" pour savoir quoi faire
            # Mon get_state() le retourne déjà si c'est le cas
            
            voiture.verifier_feu(feu_concerne, liste_voitures)
            voiture.avancer(liste_voitures)

        # E. Nettoyage
        for v in liste_voitures[:]:
            if v.est_hors_ecran():
                v.hideturtle()
                v.clear()
                liste_voitures.remove(v)

        ecran.update()
        
    except (turtle.Terminator, _tkinter.TclError, KeyboardInterrupt):
        print("Arrêt de la simulation.")
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
