"""
Module scenarios.py
Définit les différents scénarios de circulation et leur gestion.
"""

class Scenario:
    """
    Représente un scénario de simulation avec ses paramètres.
    """
    def __init__(self, name, green_duration, orange_duration, red_duration, vehicle_speed, vehicle_frequency):
        self.name = name
        self.green_duration = green_duration
        self.orange_duration = orange_duration
        self.red_duration = red_duration
        self.vehicle_speed = vehicle_speed
        self.vehicle_frequency = vehicle_frequency

class ScenarioManager:
    """
    Gère le scénario actuel et synchronise les deux feux du carrefour.
    """
    def __init__(self, light_v, light_h):
        self.light_v = light_v
        self.light_h = light_h
        
        # Scénarios prédéfinis
        self.scenarios = {
            "Normale": Scenario("Normale", 120, 40, 30, 2, 35),
            "Heure de pointe": Scenario("Heure de pointe", 200, 40, 30, 1.5, 12),
            "Mode nuit": Scenario("Mode nuit", 0, 0, 0, 3, 60),
            "Manuel": Scenario("Manuel", 120, 40, 30, 2, 35)
        }
        
        self.current_scenario_name = "Normale"
        self.cycle_state = "VERT_V"
        self.timer = 0
        self.all_red_duration = 30
        
        self._apply_scenario("Normale")

    def set_scenario(self, name: str):
        if name in self.scenarios:
            self.current_scenario_name = name
            self._apply_scenario(name)
            self.timer = 0
            self.cycle_state = "VERT_V"

    def get_current_scenario(self) -> str:
        return self.current_scenario_name

    def get_params(self):
        scenario = self.scenarios[self.current_scenario_name]
        return {
            "speed": scenario.vehicle_speed,
            "frequency": scenario.vehicle_frequency
        }

    def _apply_scenario(self, name):
        scenario = self.scenarios[name]
        night = (name == "Mode nuit")
        manual = (name == "Manuel")
        
        for light in [self.light_v, self.light_h]:
            light.is_night_mode = night
            light.is_manual = manual
            if not night and not manual:
                light.set_durations(scenario.green_duration, scenario.orange_duration, 0) # On gère le rouge via la synchro

    def update(self):
        """
        Gère la synchronisation des deux feux.
        """
        if self.current_scenario_name in ["Mode nuit"]:
            self.light_v.is_night_mode = True
            self.light_h.is_night_mode = True
            return

        if self.current_scenario_name == "Manuel":
            return

        self.timer += 1
        scenario = self.scenarios[self.current_scenario_name]
        
        # Logique de cycle synchronisé :
        # VERT_V -> ORANGE_V -> ALL_RED -> VERT_H -> ORANGE_H -> ALL_RED
        if self.cycle_state == "VERT_V":
            self.light_v.set_state("VERT")
            self.light_h.set_state("ROUGE")
            if self.timer >= scenario.green_duration:
                self.cycle_state = "ORANGE_V"
                self.timer = 0
                
        elif self.cycle_state == "ORANGE_V":
            self.light_v.set_state("ORANGE")
            self.light_h.set_state("ROUGE")
            if self.timer >= scenario.orange_duration:
                self.cycle_state = "ALL_RED_V_TO_H"
                self.timer = 0
                
        elif self.cycle_state == "ALL_RED_V_TO_H":
            self.light_v.set_state("ROUGE")
            self.light_h.set_state("ROUGE")
            if self.timer >= self.all_red_duration:
                self.cycle_state = "VERT_H"
                self.timer = 0
                
        elif self.cycle_state == "VERT_H":
            self.light_v.set_state("ROUGE")
            self.light_h.set_state("VERT")
            if self.timer >= scenario.green_duration:
                self.cycle_state = "ORANGE_H"
                self.timer = 0
                
        elif self.cycle_state == "ORANGE_H":
            self.light_v.set_state("ROUGE")
            self.light_h.set_state("ORANGE")
            if self.timer >= scenario.orange_duration:
                self.cycle_state = "ALL_RED_H_TO_V"
                self.timer = 0
                
        elif self.cycle_state == "ALL_RED_H_TO_V":
            self.light_v.set_state("ROUGE")
            self.light_h.set_state("ROUGE")
            if self.timer >= self.all_red_duration:
                self.cycle_state = "VERT_V"
                self.timer = 0
