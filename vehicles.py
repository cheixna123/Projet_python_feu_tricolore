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
            self.seuil_patience = 300  # Environ 12s - Confirmé blocus
        else:
            self.seuil_patience = 1000 # Environ 40s - Attend l'autre axe

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
            # Réinitialisation patience dès qu'on bouge
            if self.vitesse_actuelle > 0:
                self.compteur_attente = 0

    def verifier_priorite_droite(self, autres_voitures, dist_ma_ligne, ignore_priority=False):
        """
        Applique la règle de la priorité à droite STRICTE.
        On n'active le radar que si on approche du carrefour (110px).
        """
        if ignore_priority: return False
        
        # On ne s'occupe de la priorité que si on approche réellement
        if dist_ma_ligne > 110: return False
            
        droite = {"nord": "ouest", "sud": "est", "est": "nord", "ouest": "sud"}
        dir_droite = droite[self.direction_depart]
        
        for autre in autres_voitures:
            if autre.direction_depart == dir_droite:
                # Distance de l'autre par rapport à SA ligne de stop
                d_autre = 0
                if autre.direction_depart == "nord": d_autre = autre.ycor() - DISTANCE_STOP
                elif autre.direction_depart == "sud": d_autre = -DISTANCE_STOP - autre.ycor()
                elif autre.direction_depart == "est": d_autre = autre.xcor() - DISTANCE_STOP
                elif autre.direction_depart == "ouest": d_autre = -DISTANCE_STOP - autre.xcor()
                
                # BLOCAGE : Si la voiture de droite approche (120px)
                # OU si elle est encore dans le carrefour (n'a pas fini de libérer la voie)
                if -130 < d_autre < 120:
                    return True
        return False

    def verifier_feu(self, etat_feu, autres_voitures, ns_wave_active=False, cooldown_active=False):
        """
        Vérifie si la voiture doit ralentir, s'arrêter ou forcer le passage.
        """
        # ...
        dist_ligne = 0
        if self.direction_depart == "nord": dist_ligne = self.ycor() - DISTANCE_STOP
        elif self.direction_depart == "sud": dist_ligne = -DISTANCE_STOP - self.ycor()
        elif self.direction_depart == "est": dist_ligne = self.xcor() - DISTANCE_STOP
        elif self.direction_depart == "ouest": dist_ligne = -DISTANCE_STOP - self.xcor()

        deja_passe = dist_ligne < -15

        # SÉCURITÉ ABSOLUE : Cooldown post-vague
        if cooldown_active and not deja_passe:
            self.vitesse_actuelle = 0
            self.arrete_au_feu = True
            return

        if etat_feu == "VERT":
            self.arrete_au_feu = False
            self.vitesse_actuelle = self.vitesse_max
            self.force_passage = False
            return

        if etat_feu == "ORANGE_CLIGNOTANT":
            # 1. SI DÉJÀ ENGAGÉ : On dégage au plus vite
            if deja_passe:
                self.vitesse_actuelle = self.vitesse_max
                self.arrete_au_feu = False
                return

            # 2. RADAR D'ENGAGEMENT INTELLIGENT : 
            # On s'arrête seulement si l'axe PERPENDICULAIRE est déjà engagé.
            axe_perpendiculaire_libre = True
            for autre in autres_voitures:
                if autre != self and (abs(autre.xcor()) < 80 and abs(autre.ycor()) < 80):
                    # Si je suis NS, je ne m'arrête que si l'autre est EW
                    est_perpendiculaire = False
                    if self.direction_depart in ["nord", "sud"] and autre.direction_depart in ["est", "ouest"]:
                        est_perpendiculaire = True
                    elif self.direction_depart in ["est", "ouest"] and autre.direction_depart in ["nord", "sud"]:
                        est_perpendiculaire = True
                        
                    if est_perpendiculaire:
                        axe_perpendiculaire_libre = False
                        break
            
            if not axe_perpendiculaire_libre:
                # Quelqu'un barre la route, on attend à la ligne
                if 0 < dist_ligne < 70:
                    self.vitesse_actuelle = 0
                    self.arrete_au_feu = True
                else:
                    self.vitesse_actuelle = self.vitesse_max / 2
                return

            # 3. PRIORITÉ À DROITE (Sauf si vague NS active)
            is_ns = self.direction_depart in ["nord", "sud"]
            ignore = ns_wave_active and is_ns
            
            if self.verifier_priorite_droite(autres_voitures, dist_ligne, ignore_priority=ignore):
                # On s'arrête pour la priorité
                if 0 < dist_ligne < 70:
                    self.compteur_attente += 1
                    self.vitesse_actuelle = 0
                    self.arrete_au_feu = True
                else:
                    self.vitesse_actuelle = self.vitesse_max / 2
            else:
                # Tout est clair : Engagement prudent
                self.vitesse_actuelle = self.vitesse_max
                self.arrete_au_feu = False
                if ignore: self.force_passage = True
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