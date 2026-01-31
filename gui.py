import tkinter as tk
from database import Database
from logger import Logger

class GUI:
    def __init__(self, root, light_v, light_h, manager, logger, update_callback):
 
        self.root = root
        self.light_v = light_v
        self.light_h = light_h
        self.manager = manager
        self.logger = logger
        self.update_callback = update_callback
        self.current_scenario = manager.get_current_scenario()

        # Frame pour les boutons
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT, padx=10)

        # Boutons principaux
        tk.Button(self.frame, text="Play", width=12, command=self.play).pack(pady=2)
        tk.Button(self.frame, text="Pause", width=12, command=self.pause).pack(pady=2)
        tk.Button(self.frame, text="Stop/Reset", width=12, command=self.stop).pack(pady=2)

        # Sélecteur de scénario
        tk.Label(self.frame, text="Scénario").pack(pady=5)
        self.scenario_var = tk.StringVar(value=self.current_scenario)
        options = ["Normale", "Heure de pointe", "Mode nuit", "Manuel"]
        self.scenario_menu = tk.OptionMenu(self.frame, self.scenario_var, *options, command=self.change_scenario)
        self.scenario_menu.pack(pady=2)

        # Contrôles manuels 
        tk.Label(self.frame, text="Feu Manuel (Mode Manuel)").pack(pady=5)
        
        # Bouton pour basculer les axes en mode manuel
        tk.Button(self.frame, text="Basculer Axes", width=12, command=self.toggle_manual_lights).pack(pady=1)

        # Indicateurs du feu actuel (V et H)
        self.indicator_v = tk.Label(self.frame, text=f"Vertical: {self.light_v.get_state()}", bg="gray", width=15)
        self.indicator_v.pack(pady=5)
        
        self.indicator_h = tk.Label(self.frame, text=f"Horizontal: {self.light_h.get_state()}", bg="gray", width=15)
        self.indicator_h.pack(pady=5)

    def play(self):
        self.logger.log_action("BOUTON", "Play appuyé", self.light_v.get_state(), self.current_scenario)
        self.update_callback("play")

    def pause(self):
        self.logger.log_action("BOUTON", "Pause appuyé", self.light_v.get_state(), self.current_scenario)
        self.update_callback("pause")

    def stop(self):
        self.logger.log_action("BOUTON", "Stop appuyé", self.light_v.get_state(), self.current_scenario)
        self.update_callback("stop")

    def change_scenario(self, value):
        self.current_scenario = value
        self.manager.set_scenario(value)
        self.logger.log_action("SCENARIO", f"Changement → {value}", self.light_v.get_state(), value)
        self.update_callback("scenario", value)
        self.update_indicator()

    def toggle_manual_lights(self):
       
        if self.current_scenario == "Manuel":
            if self.light_v.get_state() == "VERT":
                self.light_v.set_state("ROUGE")
                self.light_h.set_state("VERT")
            else:
                self.light_v.set_state("VERT")
                self.light_h.set_state("ROUGE")
            self.update_indicator()

    def update_indicator(self):
        def get_color(state):
            return {"ROUGE":"red", "ORANGE":"orange", "VERT":"green", "ORANGE_CLIGNOTANT":"orange"}.get(state, "gray")
        
        self.indicator_v.config(text=f"Vertical: {self.light_v.get_state()}", bg=get_color(self.light_v.get_state()))
        self.indicator_h.config(text=f"Horizontal: {self.light_h.get_state()}", bg=get_color(self.light_h.get_state()))
