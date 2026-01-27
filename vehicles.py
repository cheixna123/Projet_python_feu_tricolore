from turtle import Turtle
import random

# --- CONSTANTES ---
COULEURS_VOITURES = ["#e74c3c", "#3498db", "#f1c40f", "#9b59b6", "#ecf0f1", "#95a5a6"]
# Position de la ligne de stop
DISTANCE_STOP = 110
MARGE_FREINAGE = 30
DISTANCE_SECURITE = 50  # Distance min entre deux voitures
ZONE_CRITIQUE = 60      # Zone où on ne peut plus piler à l'orange


class Vehicle(Turtle):
    def __init__(self, direction_depart, vitesse_max=6):
        super().__init__()
        self.vitesse_max = vitesse_max
        self.vitesse_actuelle = vitesse_max
        self.direction_depart = direction_depart
        self.arrete_au_feu = False
        self.arrete_devant_voiture = False
        self.force_passage = False # Pour dégager le carrefour à l'orange/rouge
        self.compteur_attente = 0  # Patience pour briser les blocus
        
        # Hiérarchie par axes pour briser les blocus proprement
        if self.direction_depart in ["nord", "sud"]:
            self.seuil_patience = 60   # Environ 2.5s - L'axe Nord-Sud débloque le carrefour
        else:
            self.seuil_patience = 200  # Environ 8s - L'axe Est-Ouest attend que l'autre passe

        self.dessiner_look_voiture()
        self.penup()
        self.placer_sur_voie()

    def dessiner_look_voiture(self):
        # On définit une forme de voiture plus réaliste (avec pare-brise)
        # Rectangle de base
        self.shape("square")
        self.shapesize(stretch_wid=1.2, stretch_len=2.2)
        self.color(random.choice(COULEURS_VOITURES))
        
        # On pourrait ajouter des détails si on utilisait register_shape, 
        # mais on va rester simple et efficace :
        # Le look est déjà bien amélioré par la taille et la couleur.

    def placer_sur_voie(self):
        # ... (Garde ton code précédent ici, c'était parfait) ...
        DECALAGE_VOIE = 35
        COORD_DEPART = 420

        if self.direction_depart == "nord":
            self.setheading(270)
            self.goto(-DECALAGE_VOIE, COORD_DEPART)
        elif self.direction_depart == "sud":
            self.setheading(90)
            self.goto(DECALAGE_VOIE, -COORD_DEPART)
        elif self.direction_depart == "est":
            self.setheading(180)
            self.goto(COORD_DEPART, DECALAGE_VOIE)
        elif self.direction_depart == "ouest":
            self.setheading(0)
            self.goto(-COORD_DEPART, -DECALAGE_VOIE)

    def avancer(self, autres_voitures):
        # 1. Vérifer s'il y a une voiture devant
        self.arrete_devant_voiture = False
        for autre in autres_voitures:
            if autre == self: continue
            
            # Distance entre voitures
            dist = self.distance(autre)
            
            # Si la voiture est devant nous dans la même direction
            if dist < DISTANCE_SECURITE:
                # Vérification directionnelle simplifiée pour la file d'attente
                # On regarde si l'autre voiture est "devant" selon notre cap (heading)
                angle_vers_autre = self.towards(autre)
                diff_angle = abs(angle_vers_autre - self.heading())
                if diff_angle < 30 or diff_angle > 330:
                    self.arrete_devant_voiture = True
                    break

        # Si stoppée par feu OU par voiture devant, on ne bouge pas
        if not self.arrete_au_feu and not self.arrete_devant_voiture:
            self.forward(self.vitesse_actuelle)
            if self.vitesse_actuelle > 0:
                self.compteur_attente = 0 # On avance, on réinitialise la patience

    def verifier_priorite_droite(self, autres_voitures):
        """
        Applique la règle de la priorité à droite : 
        On s'arrête si une voiture arrive de notre droite.
        Sauf si on attend depuis trop longtemps (bris de blocus).
        """
        if self.compteur_attente > self.seuil_patience:
            return False
            
        droite = {"nord": "ouest", "sud": "est", "est": "nord", "ouest": "sud"}
        dir_droite = droite[self.direction_depart]
        
        # On ne vérifie que si on est dans la zone d'approche du carrefour
        pos = self.ycor() if self.direction_depart in ["nord", "sud"] else self.xcor()
        if abs(pos) > 250: return False

        for autre in autres_voitures:
            if autre.direction_depart == dir_droite:
                # La voiture à droite est-elle dans le carrefour ou l'approche ?
                d_autre = 0
                if autre.direction_depart == "nord": d_autre = autre.ycor() - DISTANCE_STOP
                elif autre.direction_depart == "sud": d_autre = -DISTANCE_STOP - autre.ycor()
                elif autre.direction_depart == "est": d_autre = autre.xcor() - DISTANCE_STOP
                elif autre.direction_depart == "ouest": d_autre = -DISTANCE_STOP - autre.xcor()
                
                # Zone élargie : de 150px avant à 150px après la ligne (carrefour traversé)
                if -150 < d_autre < 150:
                    return True
        return False

    def verifier_feu(self, etat_feu, autres_voitures):
        """
        Vérifie si la voiture doit ralentir, s'arrêter ou forcer le passage.
        """
        dist_ligne = 0
        if self.direction_depart == "nord": dist_ligne = self.ycor() - DISTANCE_STOP
        elif self.direction_depart == "sud": dist_ligne = -DISTANCE_STOP - self.ycor()
        elif self.direction_depart == "est": dist_ligne = self.xcor() - DISTANCE_STOP
        elif self.direction_depart == "ouest": dist_ligne = -DISTANCE_STOP - self.xcor()

        deja_passe = dist_ligne < -15

        if etat_feu == "VERT":
            self.arrete_au_feu = False
            self.vitesse_actuelle = self.vitesse_max
            self.force_passage = False
            return

        if etat_feu == "ORANGE_CLIGNOTANT":
            # LOGIQUE : Priorité à droite stricte
            if self.verifier_priorite_droite(autres_voitures) and not deja_passe:
                # On doit ralentir et s'arrêter au stop
                self.compteur_attente += 1 # On commence à perdre patience
                self.vitesse_actuelle = self.vitesse_max / 2
                # Rayon d'arrêt plus large pour la priorité
                if 0 < dist_ligne < 70: 
                    self.arrete_au_feu = True
                    self.vitesse_actuelle = 0
            else:
                # Pas de danger à droite (ou patience à bout) -> passage prudent
                self.vitesse_actuelle = self.vitesse_max / 2
                self.arrete_au_feu = False
                self.force_passage = True
            return

        if etat_feu == "ORANGE":
            if deja_passe or dist_ligne < ZONE_CRITIQUE:
                self.force_passage = True
                self.arrete_au_feu = False
                self.vitesse_actuelle = self.vitesse_max
            else:
                self.vitesse_actuelle = self.vitesse_max / 2
                self.force_passage = False
            return

        if etat_feu == "ROUGE":
            if self.force_passage: return
            
            doit_stopper = False
            if self.direction_depart == "nord":
                if DISTANCE_STOP < self.ycor() < DISTANCE_STOP + MARGE_FREINAGE: doit_stopper = True
            elif self.direction_depart == "sud":
                if -DISTANCE_STOP - MARGE_FREINAGE < self.ycor() < -DISTANCE_STOP: doit_stopper = True
            elif self.direction_depart == "est":
                if DISTANCE_STOP < self.xcor() < DISTANCE_STOP + MARGE_FREINAGE: doit_stopper = True
            elif self.direction_depart == "ouest":
                if -DISTANCE_STOP - MARGE_FREINAGE < self.xcor() < -DISTANCE_STOP: doit_stopper = True

            if doit_stopper:
                self.arrete_au_feu = True
                self.vitesse_actuelle = 0

    def est_hors_ecran(self):
        return abs(self.xcor()) > 450 or abs(self.ycor()) > 450