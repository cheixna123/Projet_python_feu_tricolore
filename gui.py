import tkinter as tk
from database import Database
from logger import Logger

class GUI:
    def __init__(self, root, traffic_light, logger, update_callback):
        """
        root: fenêtre Tkinter
        traffic_light: instance de TrafficLight
        logger: instance de Logger
        update_callback: fonction à appeler pour redessiner le feu/voitures
        """
        self.root = root
        self.traffic_light = traffic_light
        self.logger = logger
        self.update_callback = update_callback
        self.current_scenario = traffic_light.scenario.name

        # Frame pour les boutons
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT, padx=10)

        # Boutons principaux
        tk.Button(self.frame, text="Play", width=12, command=self.play).pack(pady=2)
        tk.Button(self.frame, text="Pause", width=12, command=self.pause).pack(pady=2)
        tk.Button(self.frame, text="Stop", width=12, command=self.stop).pack(pady=2)
        tk.Button(self.frame, text="Reset", width=12, command=self.reset).pack(pady=2)

        # Sélecteur de scénario
        tk.Label(self.frame, text="Scénario").pack(pady=5)
        self.scenario_var = tk.StringVar(value=self.current_scenario)
        options = ["Normale", "Heure de pointe", "Mode nuit", "Manuel"]
        self.scenario_menu = tk.OptionMenu(self.frame, self.scenario_var, *options, command=self.change_scenario)
        self.scenario_menu.pack(pady=2)

        # Boutons feu manuel
        tk.Label(self.frame, text="Feu Manuel").pack(pady=5)
        tk.Button(self.frame, text="Vert", width=12, command=lambda: self.change_fire("VERT")).pack(pady=1)
        tk.Button(self.frame, text="Orange", width=12, command=lambda: self.change_fire("ORANGE")).pack(pady=1)
        tk.Button(self.frame, text="Rouge", width=12, command=lambda: self.change_fire("ROUGE")).pack(pady=1)

        # Indicateur du feu actuel
        self.indicator = tk.Label(self.frame, text=f"Feu: {self.traffic_light.current_state}", bg="red", width=12)
        self.indicator.pack(pady=10)

    # Boutons principaux
    def play(self):
        self.logger.log_action("BOUTON", "Play appuyé", self.traffic_light.current_state, self.current_scenario)
        print("Simulation démarrée")
        # Appeler la fonction pour démarrer la simulation
        self.update_callback("play")

    def pause(self):
        self.logger.log_action("BOUTON", "Pause appuyé", self.traffic_light.current_state, self.current_scenario)
        print("Simulation en pause")
        self.update_callback("pause")

    def stop(self):
        self.logger.log_action("BOUTON", "Stop appuyé", self.traffic_light.current_state, self.current_scenario)
        print("Simulation arrêtée")
        self.update_callback("stop")

    def reset(self):
        self.logger.log_action("BOUTON", "Reset appuyé", self.traffic_light.current_state, self.current_scenario)
        print("Simulation réinitialisée")
        self.update_callback("reset")

    # Changement de scénario
    def change_scenario(self, value):
        self.current_scenario = value
        self.logger.log_action("SCENARIO", f"Changement scénario → {value}", self.traffic_light.current_state, value)
        print(f"Scénario changé → {value}")
        self.update_callback("scenario", value)

    # Changement manuel du feu
    def change_fire(self, state):
        self.traffic_light.change_state(state)
        self.logger.log_action("FEU", f"Changement manuel → {state}", self.traffic_light.current_state, self.current_scenario)
        print(f"Feu manuel → {state}")
        self.update_callback("fire", state)
        self.update_indicator()

    # Mise à jour de l’indicateur
    def update_indicator(self):
        color = {"ROUGE":"red", "ORANGE":"orange", "VERT":"green"}.get(self.traffic_light.current_state, "gray")
        self.indicator.config(text=f"Feu: {self.traffic_light.current_state}", bg=color)
