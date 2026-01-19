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
LARGEUR_FENETRE = 800
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

    def update_color(self, etat, flash=False):
        if etat == self.dernier_etat and flash == self.dernier_flash:
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
    pen.goto(-400, 350)
    pen.color("#2c3e50")
    pen.begin_fill()
    for _ in range(2):
        pen.forward(800)
        pen.left(90)
        pen.forward(50)
        pen.left(90)
    pen.end_fill()
    pen.goto(-380, 365)
    pen.color("white")
    pen.write("MODES SIMULATION :", font=("Arial", 12, "bold"))

def dessiner_bouton(pen, x, y, texte, couleur_fond, active=False):
    pen.penup()
    pen.goto(x, y)
    pen.color("white" if active else "black", couleur_fond)
    pen.pensize(3 if active else 1)
    pen.begin_fill()
    for _ in range(2):
        pen.forward(110)
        pen.left(90)
        pen.forward(30)
        pen.left(90)
    pen.end_fill()
    pen.goto(x + 55, y + 8)
    pen.color("white" if active else "black")
    pen.write(texte, align="center", font=("Arial", 10, "bold"))

def dessiner_toute_l_interface(pen, mode_actuel):
    pen.clear()
    dessiner_panneau_interface(pen)
    dessiner_bouton(pen, -210, 360, "NORMAL", "#2ecc71", mode_actuel == "NORMAL")
    dessiner_bouton(pen, -90, 360, "PANIQUE", "#e74c3c", mode_actuel == "PANIQUE")
    dessiner_bouton(pen, 30, 360, "NUIT", "#34495e", mode_actuel == "NUIT")
    dessiner_bouton(pen, 150, 360, "PANNE", "#f39c12", mode_actuel == "PANNE")

def dessiner_decor_pro(theme=THEME_JOUR, pen=None):
    if pen is None:
        pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.clear()

    # 1. HERBE
    pen.width(1)
    for _ in range(400):
        x = random.randint(-400, 400)
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
    rect(-400, LARGEUR_TOTALE/2, 400, -LARGEUR_TOTALE/2, theme["trottoir"])

    # 3. ASPHALTE
    rect(-LARGEUR_ROUTE/2, 400, LARGEUR_ROUTE/2, -400, theme["asphalte"])
    rect(-400, LARGEUR_ROUTE/2, 400, -LARGEUR_ROUTE/2, theme["asphalte"])

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
        for x in range(-400, 400, 40):
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
        pen.penup(); pen.goto(-400, offset); pen.pendown(); pen.goto(400, offset)

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