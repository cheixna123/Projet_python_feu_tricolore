import turtle
import random

# --- THÈMES DE COULEURS ---
THEME_JOUR = {
    "herbe": "#1a5e1a",
    "texture": "#228B22",
    "asphalte": "#34495e",
    "trottoir": "#95a5a6",
    "bordure": "#bdc3c7",
    "marquage": "#ecf0f1",
    "ligne_centrale": "#f1c40f"
}

THEME_NUIT = {
    "herbe": "#0d200d",
    "texture": "#1a5e1a",
    "asphalte": "#1c2833",
    "trottoir": "#566573",
    "bordure": "#2c3e50",
    "marquage": "#bdc3c7",
    "ligne_centrale": "#d4ac0d"
}

# --- DIMENSIONS ---
LARGEUR_FENETRE = 1100
HAUTEUR_FENETRE = 800
LARGEUR_ROUTE = 160
LARGEUR_TROTTOIR = 30
LARGEUR_TOTALE = LARGEUR_ROUTE + (LARGEUR_TROTTOIR * 2)

class TrafficLightVisual:
    """ Gère l'affichage d'UN feu tricolore avec un look soigné et overhead """

    def __init__(self, x, y, orientation="vertical"):
        self.x = x
        self.y = y
        self.orientation = orientation
        
        # Tortue pour le poteau et le bras (statique)
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.penup()
        
        # Tortue pour les lumières (dynamique)
        self.light_pen = turtle.Turtle()
        self.light_pen.hideturtle()
        self.light_pen.speed(0)
        self.light_pen.penup()
        
        self.dernier_etat = None
        self.dernier_flash = None
        self.dessiner_structure()
        self.update_color("ROUGE")

    def dessiner_structure(self):
        self.pen.clear()
        self.pen.penup()
        self.pen.goto(self.x, self.y)
        self.pen.setheading(90)
        self.pen.color("#7f8c8d")
        self.pen.width(10)
        self.pen.pendown()
        self.pen.forward(120) 
        
        # 2. Le Bras Horizontal
        bx, by = self.pen.pos()
        self.pen.width(6)
        if self.orientation == "vertical":
            # Bras vers le milieu de la route (X)
            dist = -60 if self.x > 0 else 60
            self.pen.setheading(0 if dist > 0 else 180)
        else:
            # Route horizontale, bras vers le milieu (Y)
            dist = -60 if self.y > 0 else 60
            self.pen.setheading(90 if dist < 0 else 270)
        
        self.pen.forward(abs(dist))
        bx, by = self.pen.pos()

        # 3. Le Boîtier (Noir)
        self.pen.penup()
        # On centre le boîtier (40px)
        self.pen.goto(bx - 20, by)
        self.pen.setheading(0)
        self.pen.color("black", "#2c3e50")
        self.pen.begin_fill()
        for _ in range(2):
            self.pen.forward(40)
            self.pen.right(90)
            self.pen.forward(90)
            self.pen.right(90)
        self.pen.end_fill()
        
        # Positions corrigées pour les lumières
        self.light_start_x = bx
        self.light_start_y = by - 18

    def update_color(self, etat, flash=False, force=False):
        if not force and etat == self.dernier_etat and flash == self.dernier_flash:
            return
        self.dernier_etat = etat
        self.dernier_flash = flash
        self.light_pen.clear()

        # Couleurs
        r_on, r_off = "#e74c3c", "#4a1a1a"
        o_on, o_off = "#f39c12", "#583d11"
        v_on, v_off = "#2ecc71", "#1e4d2b"

        c_rouge = r_on if etat == "ROUGE" else r_off
        c_orange = o_off
        if etat == "ORANGE":
            c_orange = o_on
        elif etat == "ORANGE_CLIGNOTANT":
            # VRAI Clignotement : On / Off total
            c_orange = o_on if flash else "#1a1a1a"
        c_vert = v_on if etat == "VERT" else v_off

        self.dessiner_lumiere(self.light_start_x, self.light_start_y, c_rouge)
        self.dessiner_lumiere(self.light_start_x, self.light_start_y - 30, c_orange)
        self.dessiner_lumiere(self.light_start_x, self.light_start_y - 60, c_vert)

    def dessiner_lumiere(self, x, y, couleur):
        self.light_pen.penup()
        self.light_pen.goto(x, y - 12)
        self.light_pen.setheading(0)
        self.light_pen.color("black", couleur)
        self.light_pen.begin_fill()
        self.light_pen.circle(12)
        self.light_pen.end_fill()


def init_screen(theme=THEME_JOUR):
    screen = turtle.Screen()
    screen.title("Simulation Carrefour Pro - A.Oumazize")
    screen.bgcolor(theme["herbe"])
    screen.setup(LARGEUR_FENETRE, HAUTEUR_FENETRE)
    screen.tracer(0)
    return screen

def dessiner_panneau_interface(pen):
    pen.penup()
    # On décale le panneau horizontal à droite (X > 150)
    # On le descend de 60px pour éviter qu'il ne soit coupé en haut
    # X de 150 à 550, Y de 160 à 320
    pen.goto(150, 160)
    pen.setheading(0)
    pen.color("#2c3e50")
    pen.begin_fill()
    for _ in range(2):
        pen.forward(400)
        pen.left(90)
        pen.forward(160)
        pen.left(90)
    pen.end_fill()
    
    # Titres des sections décalés
    pen.color("white")
    x_text = 160
    pen.goto(x_text, 290)
    pen.write("SCÉNARIOS", font=("Arial", 9, "bold"))
    pen.goto(x_text, 240)
    pen.write("CONTRÔLES", font=("Arial", 9, "bold"))
    pen.goto(x_text, 185)
    pen.write("MANUEL", font=("Arial", 9, "bold"))

def dessiner_bouton(pen, x, y, texte, couleur_fond, active=False, width=80):
    pen.penup()
    pen.goto(x, y)
    pen.setheading(0)
    # ... (reste inchangé)
    pen.color("white" if active else "black", couleur_fond)
    pen.pensize(2 if active else 1)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(width)
        pen.left(90)
        pen.forward(25)
        pen.left(90)
    pen.end_fill()
    
    # Centrage du texte
    offset_x = width / 2
    pen.goto(x + offset_x, y + 6)
    pen.color("white" if active else "black")
    pen.write(texte, align="center", font=("Arial", 7, "bold"))

def dessiner_toute_l_interface(pen, mode_actuel, is_paused=False, manual_active=False):
    pen.clear()
    dessiner_panneau_interface(pen)
    
    # Boutons alignés à droite du texte (Starting at X=240)
    x_start = 240
    
    # LIGNE 1 : SCÉNARIOS (Y=285)
    y_scen = 285
    dessiner_bouton(pen, x_start, y_scen, "NORMAL", "#2ecc71", mode_actuel == "NORMAL", width=70)
    dessiner_bouton(pen, x_start+75, y_scen, "PANIQUE", "#e74c3c", mode_actuel == "PANIQUE", width=70)
    dessiner_bouton(pen, x_start+150, y_scen, "NUIT", "#34495e", mode_actuel == "NUIT", width=70)
    dessiner_bouton(pen, x_start+225, y_scen, "MANUEL", "#f39c12", mode_actuel == "PANNE", width=70)

    # LIGNE 2 : PLAYBACK (Y=235)
    y_play = 235
    dessiner_bouton(pen, x_start, y_play, "PLAY", "#27ae60", not is_paused, width=70)
    dessiner_bouton(pen, x_start+75, y_play, "PAUSE", "#e67e22", is_paused, width=70)
    dessiner_bouton(pen, x_start+150, y_play, "RESET", "#3498db", False, width=70)

    # LIGNE 3 : CONTRÔLES MANUELS (Y=180)
    if manual_active:
        y_man = 180
        dessiner_bouton(pen, x_start, y_man, "SWITCH VERT.", "#8e44ad", False, width=110)
        dessiner_bouton(pen, x_start+120, y_man, "SWITCH HORIZ.", "#8e44ad", False, width=110)
    else:
        pen.goto(x_start, 185)
        pen.color("#95a5a6")
        pen.write("(Activez le mode MANUEL)", font=("Arial", 8, "italic"))

def dessiner_decor_pro(theme=THEME_JOUR, pen=None):
    if pen is None:
        pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.clear()

    # 1. HERBE - On élargit la zone de génération pour la fenêtre de 1100
    pen.width(1)
    for _ in range(500):
        x = random.randint(-550, 550)
        y = random.randint(-400, 400)
        if abs(x) < LARGEUR_TOTALE/2 or abs(y) < LARGEUR_TOTALE/2: continue
        pen.penup(); pen.goto(x, y); pen.color(random.choice([theme["herbe"], theme["texture"]]))
        pen.pendown(); pen.setheading(90); pen.forward(random.randint(3, 8))

    # 2. TROTTOIRS
    def rect(x1, y1, x2, y2, c):
        pen.penup(); pen.goto(x1, y1); pen.color(c); pen.begin_fill()
        for p in [(x2, y1), (x2, y2), (x1, y2)]: pen.goto(p)
        pen.end_fill()

    # Trottoirs pleins
    rect(-LARGEUR_TOTALE/2, 400, LARGEUR_TOTALE/2, -400, theme["trottoir"])
    rect(-550, LARGEUR_TOTALE/2, 550, -LARGEUR_TOTALE/2, theme["trottoir"])

    # 3. ASPHALTE
    rect(-LARGEUR_ROUTE/2, 400, LARGEUR_ROUTE/2, -400, theme["asphalte"])
    rect(-550, LARGEUR_ROUTE/2, 550, -LARGEUR_ROUTE/2, theme["asphalte"])

    # 4. MARQUAGES
    pen.color(theme["marquage"])
    pen.width(2)
    # Lignes de voies (pointillés)
    for coord in [-LARGEUR_ROUTE/4, LARGEUR_ROUTE/4]:
        # Vertical
        for y in range(-400, 400, 40):
            if abs(y) > LARGEUR_ROUTE/2 + 10:
                pen.penup(); pen.goto(coord, y); pen.pendown(); pen.goto(coord, y+20)
        # Horizontal
        for x in range(-550, 550, 40):
            if abs(x) > LARGEUR_ROUTE/2 + 10:
                pen.penup(); pen.goto(x, coord); pen.pendown(); pen.goto(x+20, coord)
    
    # Lignes de STOP
    pen.width(6)
    lim = LARGEUR_ROUTE/2
    pen.penup(); pen.goto(-lim, lim+5); pen.pendown(); pen.goto(0, lim+5) # N
    pen.penup(); pen.goto(0, -lim-5); pen.pendown(); pen.goto(lim, -lim-5) # S
    pen.penup(); pen.goto(lim+5, 0); pen.pendown(); pen.goto(lim+5, lim) # E
    pen.penup(); pen.goto(-lim-5, -lim); pen.pendown(); pen.goto(-lim-5, 0) # W

    # Ligne Jaune Centrale
    pen.color(theme["ligne_centrale"])
    pen.width(3)
    for offset in [-2, 2]:
        pen.penup(); pen.goto(offset, 400); pen.pendown(); pen.goto(offset, -400)
        pen.penup(); pen.goto(-550, offset); pen.pendown(); pen.goto(550, offset)

    # Passages piétons (simplifiés)
    pen.color(theme["marquage"])
    pen.width(10)
    for i in range(-3, 4):
        # N & S
        for y in [lim+25, -lim-25]:
            pen.penup(); pen.goto(i*20, y-15); pen.setheading(90); pen.pendown(); pen.forward(30)
        # E & W
        for x in [lim+25, -lim-25]:
            pen.penup(); pen.goto(x-15, i*20); pen.setheading(0); pen.pendown(); pen.forward(30)