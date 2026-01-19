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
        self.vehicle_frequency = vehicle_frequency  # Plus la valeur est petite, plus c'est fréquent

class ScenarioManager:
    """
    Gère le scénario actuel et fournit les paramètres aux autres modules.
    """
    def __init__(self, traffic_light):
        self.traffic_light = traffic_light
        self.scenarios = {
            "Normal": Scenario("Normal", 100, 20, 100, 2, 50),
            "Heure de pointe": Scenario("Heure de pointe", 150, 20, 80, 1, 20),
            "Mode nuit": Scenario("Mode nuit", 0, 0, 0, 3, 100),
            "Manuel": Scenario("Manuel", 100, 20, 100, 2, 50)
        }
        self.current_scenario_name = "Normal"
        self._apply_scenario(self.scenarios["Normal"])

    def set_scenario(self, name: str):
        """
        Change le scénario actuel par son nom.
        """
        if name in self.scenarios:
            self.current_scenario_name = name
            scenario = self.scenarios[name]
            self._apply_scenario(scenario)
            print(f"Scénario changé pour : {name}")

    def get_current_scenario(self) -> str:
        """Retourne le nom du scénario actuel."""
        return self.current_scenario_name

    def get_params(self):
        """Retourne les paramètres de circulation du scénario actuel."""
        scenario = self.scenarios[self.current_scenario_name]
        return {
            "speed": scenario.vehicle_speed,
            "frequency": scenario.vehicle_frequency
        }

    def _apply_scenario(self, scenario):
        """Applique les paramètres du scénario au feu tricolore."""
        if scenario.name == "Mode nuit":
            self.traffic_light.toggle_night_mode(True)
            self.traffic_light.toggle_manual(False)
        elif scenario.name == "Manuel":
            self.traffic_light.toggle_night_mode(False)
            self.traffic_light.toggle_manual(True)
        else:
            self.traffic_light.toggle_night_mode(False)
            self.traffic_light.toggle_manual(False)
            self.traffic_light.set_durations(
                scenario.green_duration,
                scenario.orange_duration,
                scenario.red_duration
            )
