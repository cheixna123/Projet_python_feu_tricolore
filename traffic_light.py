"""
Module traffic_light.py
Gère la logique d'état d'un feu tricolore.
"""

class TrafficLight:
    """
    Classe représentant un feu tricolore.
    Gère les cycles VERT, ORANGE, ROUGE et le mode CLIGNOTANT.
    """
    
    # Constantes d'état
    VERT = "VERT"
    ORANGE = "ORANGE"
    ROUGE = "ROUGE"
    ORANGE_CLIGNOTANT = "ORANGE_CLIGNOTANT" # Ajouté pour compatibilité véhicules

    def __init__(self, name="Feu", green_duration=100, orange_duration=30, red_duration=100):
        """
        Initialise le feu tricolore.
        """
        self.name = name
        self.durations = {
            self.VERT: green_duration,
            self.ORANGE: orange_duration,
            self.ROUGE: red_duration
        }
        
        self.state = self.ROUGE
        self.timer = 0
        self.is_manual = False
        self.is_night_mode = False
        self.blink_state = False

    def get_state(self) -> str:
        """
        Retourne l'état actuel du feu.
        """
        if self.is_night_mode:
            return self.ORANGE_CLIGNOTANT
        return self.state

    def set_state(self, state: str):
        """
        Force l'état du feu.
        """
        if state in [self.VERT, self.ORANGE, self.ROUGE]:
            self.state = state
            self.timer = 0

    def set_durations(self, green: int, orange: int, red: int):
        """
        Met à jour les durées des feux.
        """
        self.durations[self.VERT] = green
        self.durations[self.ORANGE] = orange
        self.durations[self.ROUGE] = red

    def update(self):
        """
        Met à jour le timer interne. 
        Note: La logique de cycle synchronisée est gérée par le ScenarioManager ou le main.
        """
        self.timer += 1

    def __str__(self):
        return f"{self.name}: {self.get_state()} ({self.timer})"
