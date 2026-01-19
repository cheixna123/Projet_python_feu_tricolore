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
    CLIGNOTANT = "CLIGNOTANT"

    def __init__(self, green_duration=10, orange_duration=3, red_duration=10):
        """
        Initialise le feu tricolore avec des durées par défaut.
        
        :param green_duration: Durée du feu vert en ticks/secondes
        :param orange_duration: Durée du feu orange en ticks/secondes
        :param red_duration: Durée du feu rouge en ticks/secondes
        """
        self.durations = {
            self.VERT: green_duration,
            self.ORANGE: orange_duration,
            self.ROUGE: red_duration
        }
        
        self.state = self.ROUGE
        self.timer = 0
        self.is_manual = False
        self.is_night_mode = False
        self.blink_state = False  # Pour l'orange clignotant

    def get_state(self) -> str:
        """
        Retourne l'état actuel du feu.
        Si en mode nuit, peut retourner "ORANGE" ou "OFF" selon le clignotement.
        """
        if self.is_night_mode:
            return self.ORANGE if self.blink_state else "OFF"
        return self.state

    def set_state(self, state: str):
        """
        Force l'état du feu (utile pour le mode manuel ou initialisation).
        """
        if state in [self.VERT, self.ORANGE, self.ROUGE, self.CLIGNOTANT]:
            self.state = state
            self.timer = 0

    def set_durations(self, green: int, orange: int, red: int):
        """
        Met à jour les durées des feux selon le scénario.
        """
        self.durations[self.VERT] = green
        self.durations[self.ORANGE] = orange
        self.durations[self.ROUGE] = red

    def toggle_manual(self, manual: bool):
        """Active ou désactive le mode manuel."""
        self.is_manual = manual

    def toggle_night_mode(self, night: bool):
        """Active ou désactive le mode nuit (orange clignotant)."""
        self.is_night_mode = night
        self.timer = 0

    def update(self):
        """
        Met à jour l'état du feu en fonction du temps qui passe.
        Cette méthode doit être appelée à chaque 'tick' de la simulation.
        """
        if self.is_night_mode:
            self.timer += 1
            if self.timer >= 5:  # Clignote toutes les 5 unités de temps
                self.blink_state = not self.blink_state
                self.timer = 0
            return

        if self.is_manual:
            return  # En mode manuel, on ne change pas d'état automatiquement

        self.timer += 1
        
        # Logique de cycle automatique : VERT -> ORANGE -> ROUGE -> VERT
        current_limit = self.durations.get(self.state, 10)
        
        if self.timer >= current_limit:
            self.timer = 0
            if self.state == self.VERT:
                self.state = self.ORANGE
            elif self.state == self.ORANGE:
                self.state = self.ROUGE
            elif self.state == self.ROUGE:
                self.state = self.VERT
