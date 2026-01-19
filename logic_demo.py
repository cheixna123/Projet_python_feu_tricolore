"""
Script de démonstration de la logique métier (Modèle).
Permet de vérifier le fonctionnement des feux et des scénarios sans interface graphique.
"""
from traffic_light import TrafficLight
from scenarios import ScenarioManager
import time

def demo():
    print("=== Démo Logique Feu Tricolore ===")
    
    # 1. Création du feu
    feu = TrafficLight(green_duration=5, orange_duration=2, red_duration=5)
    
    # 2. Création du gestionnaire de scénarios
    manager = ScenarioManager(feu)
    
    print(f"\nScénario initial : {manager.get_current_scenario()}")
    
    # Simulation de quelques cycles
    for i in range(15):
        feu.update()
        print(f"Tick {i+1}: État = {feu.get_state()} (Timer = {feu.timer})")

    # 3. Changement de scénario : Mode Nuit
    print("\n--- Passage en Mode Nuit ---")
    manager.set_scenario("Mode nuit")
    for i in range(10):
        feu.update()
        print(f"Tick {i+1}: État = {feu.get_state()}")

    # 4. Changement de scénario : Heure de pointe
    print("\n--- Passage en Heure de pointe ---")
    manager.set_scenario("Heure de pointe")
    params = manager.get_params()
    print(f"Paramètres circulation : Vitesse={params['speed']}, Fréquence={params['frequency']}")
    for i in range(5):
        feu.update()
        print(f"Tick {i+1}: État = {feu.get_state()} (Timer = {feu.timer})")

    print("\n=== Fin de la démo ===")

if __name__ == "__main__":
    demo()
