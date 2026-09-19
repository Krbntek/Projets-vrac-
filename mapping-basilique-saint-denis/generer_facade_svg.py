#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur de l'elevation vectorielle de la facade occidentale
de la basilique-cathedrale de Saint-Denis, pour mapping video et laser.

Systeme de coordonnees du MODELE :
    X en metres, 0 = axe de symetrie de la facade (axe du portail central)
    Y en metres, 0 = niveau du parvis, vers le HAUT
Systeme de coordonnees du SVG :
    1 unite SVG = 1 cm.  viewBox = 0 0 3250 6100  (32,50 m x 61,00 m)
    => echelle 1:100 si on ouvre le SVG en mm, 1 px SVG = 1 cm reel.

CALAGE (voir CALCULS-MAPPING.md, section 1) :
    photo de reference 1280 x 2007 px
    sol      y = 1935 px
    axe      x =  645 px
    echelle  30,70 px/m   (recoupee sur 2 cotes publiees : massif 29 m, tour sud 58 m)

Pour recaler apres releve sur site : modifier les constantes du bloc MODELE
ci-dessous, puis relancer le script. Tout le reste suit.
"""

import math, os

# ----------------------------------------------------------------------------
# MODELE  (metres)
# ----------------------------------------------------------------------------
W_TOT   = 32.50          # largeur hors-tout du massif occidental
HALF    = W_TOT / 2.0
H_DOC   = 61.00          # hauteur du document

# lignes horizontales (hauteur au-dessus du parvis)
Y_SOCLE      =  1.40     # larmier du soubassement
Y_IMP_LAT    =  4.90     # imposte des portails lateraux
Y_IMP_CEN    =  5.40     # imposte du portail central
Y_CORN1      = 10.60     # grande corniche au-dessus des portails
Y_APPUI      = 12.20     # appui des baies hautes
Y_BANDEAU    = 18.80     # bandeau a mi-hauteur des baies
Y_LINT       = 23.00     # sommet des baies hautes
Y_ARC_BAS    = 23.10     # naissance de l'arcature a statues
Y_ARC_HAUT   = 25.90     # sommet de l'arcature
Y_CORN2      = 28.40     # corniche sous le parapet
Y_PARAPET    = 29.20     # arase du parapet crenele  (cote publiee : 29 m)
Y_PIGNON     = 37.30     # sommet du pignon central
Y_STATUE     = 38.40     # sommet de la statue du pignon

# travees : axes des contreforts intermediaires
X_CF         =  5.65     # axe des 2 contreforts separant les travees
CF_L         =  1.95     # largeur des contreforts
X_PORT_LAT   =  9.60     # axe des portails lateraux

# rosace-horloge
ROSE_X, ROSE_Y = 0.00, 22.50
ROSE_R_EXT   =  3.00     # rayon du cadre mouluré  (diam. 6,00 m)
ROSE_R_CAD   =  2.35     # rayon du cadran de l'horloge
ROSE_R_VIT   =  2.15     # rayon du vitrail
ROSE_R_INT   =  0.95     # rayon de l'oculus central

# tour sud (sur la travee droite)
X_T0, X_T1   =  5.20, 15.80
Y_T_BAIE1_B  = 30.10     # abat-sons bas
Y_T_BAIE1_H  = 36.30
Y_T_CORN     = 36.60
Y_T_BAIE2_B  = 37.00     # abat-sons hauts
Y_T_BAIE2_H  = 49.00
Y_T_ARASE    = 50.60     # corniche sommitale de la tour carree
Y_T_TOIT     = 54.60     # base du lanternon
Y_T_LANT     = 57.60     # sommet des colonnettes du lanternon
Y_T_FLECHE   = 58.00     # pointe                       (cote publiee : 58 m)
Y_T_CROIX    = 60.10     # croix + girouette
X_TOURELLE_0, X_TOURELLE_1 = 4.05, 5.25   # tourelle d'escalier

# ----------------------------------------------------------------------------
# helpers SVG  (metres -> unites SVG)
# ----------------------------------------------------------------------------
def sx(x): return round((x + HALF) * 100.0, 1)
def sy(y): return round((H_DOC - y) * 100.0, 1)

def rect(x0, x1, y0, y1, **kw):
    return elem("rect", x=sx(x0), y=sy(y1), width=round((x1-x0)*100,1),
                height=round((y1-y0)*100,1), **kw)

def line(x0, y0, x1, y1, **kw):
    return elem("line", x1=sx(x0), y1=sy(y0), x2=sx(x1), y2=sy(y1), **kw)

def circle(cx, cy, r, **kw):
    return elem("circle", cx=sx(cx), cy=sy(cy), r=round(r*100,1), **kw)

def path(d, **kw):
    return elem("path", d=d, **kw)

def elem(tag, **kw):
    a = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items() if v is not None)
    return f"<{tag} {a}/>"

def P(x, y):
    return f"{sx(x)},{sy(y)}"

def arc_plein_cintre(x0, x1, y_naissance):
    """Baie/arc en plein cintre : montants + demi-cercle. Renvoie un path ferme."""
    r = (x1 - x0) / 2.0
    return (f"M {P(x0, 0)} L {P(x0, y_naissance)} "
            f"A {r*100:.1f},{r*100:.1f} 0 0 1 {P(x1, y_naissance)} L {P(x1, 0)}")

def baie_cintree(x0, x1, y_base, y_naissance):
    r = (x1 - x0) / 2.0
    return (f"M {P(x0, y_base)} L {P(x0, y_naissance)} "
            f"A {r*100:.1f},{r*100:.1f} 0 0 1 {P(x1, y_naissance)} "
            f"L {P(x1, y_base)} Z")

def baie_ogivale(x0, x1, y_base, y_naissance, y_sommet):
    """Arc brise approche par 2 arcs de cercle passant par le sommet."""
    cx = (x0 + x1) / 2.0
    demi = (x1 - x0) / 2.0
    h = y_sommet - y_naissance
    r = (demi*demi + h*h) / (2*h) if h > 0 else demi
    R = round(r*100, 1)
    return (f"M {P(x0, y_base)} L {P(x0, y_naissance)} "
            f"A {R},{R} 0 0 1 {P(cx, y_sommet)} "
            f"A {R},{R} 0 0 1 {P(x1, y_naissance)} "
            f"L {P(x1, y_base)} Z")

# ----------------------------------------------------------------------------
# elements composes
# ----------------------------------------------------------------------------
def portail(xc, demi_ouv, y_linteau, demi_arch, y_imposte, n_voussures=4):
    """Portail : ebrasement + voussures concentriques + vantail."""
    out = []
    # vantail
    out.append(rect(xc-demi_ouv, xc+demi_ouv, 0, y_linteau))
    # voussures concentriques
    for i in range(n_voussures + 1):
        t = i / n_voussures
        d = demi_ouv + (demi_arch - demi_ouv) * t
        out.append(path(baie_cintree(xc-d, xc+d, y_imposte - 0.9*t, y_imposte)))
    # ligne d'imposte
    out.append(line(xc-demi_arch, y_imposte, xc+demi_arch, y_imposte))
    return out

def crenelage(x0, x1, y_bas, y_haut, pas=1.30, plein=0.75):
    """Parapet crenele -> une polyligne unique (ideal masque + laser)."""
    n = max(1, int((x1 - x0) / pas))
    pas = (x1 - x0) / n
    d = [f"M {P(x0, y_bas)}", f"L {P(x0, y_haut)}"]
    x = x0
    for i in range(n):
        a, b = x + pas*(1-plein)/2, x + pas*(1+plein)/2
        d += [f"L {P(a, y_haut)}", f"L {P(a, y_haut+0.85)}",
              f"L {P(b, y_haut+0.85)}", f"L {P(b, y_haut)}"]
        x += pas
    d += [f"L {P(x1, y_haut)}", f"L {P(x1, y_bas)}"]
    return path(" ".join(d))

def arcature(x0, x1, y_bas, y_haut, n=4):
    """Arcature aveugle a colonnettes (bandeau de statues)."""
    out, pas = [], (x1 - x0) / n
    for i in range(n):
        a = x0 + i*pas + 0.10
        b = a + pas - 0.20
        out.append(path(baie_cintree(a, b, y_bas, y_haut - (b-a)/2)))
    return out

def rosace(nb_lobes=12):
    out = [circle(ROSE_X, ROSE_Y, ROSE_R_EXT),
           circle(ROSE_X, ROSE_Y, ROSE_R_CAD),
           circle(ROSE_X, ROSE_Y, ROSE_R_VIT),
           circle(ROSE_X, ROSE_Y, ROSE_R_INT)]
    for i in range(nb_lobes):
        a = 2*math.pi*i/nb_lobes - math.pi/2
        # rayon
        out.append(line(ROSE_X + ROSE_R_INT*math.cos(a), ROSE_Y + ROSE_R_INT*math.sin(a),
                        ROSE_X + ROSE_R_VIT*math.cos(a), ROSE_Y + ROSE_R_VIT*math.sin(a)))
        # oculus du lobe (chiffres de l'horloge)
        a2 = a + math.pi/nb_lobes
        rr = (ROSE_R_INT + ROSE_R_VIT) / 2 + 0.35
        out.append(circle(ROSE_X + rr*math.cos(a2), ROSE_Y + rr*math.sin(a2), 0.26))
    return out

# ----------------------------------------------------------------------------
# couches
# ----------------------------------------------------------------------------
def couche_contour():
    """Silhouette generale : LE masque de base pour MadMapper / Resolume."""
    d = [f"M {P(-HALF,0)}",
         f"L {P(-HALF, Y_CORN2)}", f"L {P(-HALF, Y_PARAPET)}",
         f"L {P(-X_CF-1.4, Y_PARAPET)}",
         # pignon central
         f"L {P(-X_CF-1.4, Y_PARAPET)}", f"L {P(-5.90, Y_PARAPET)}",
         f"L {P(0, Y_PIGNON)}", f"L {P(5.90, Y_PARAPET)}",
         f"L {P(X_T0, Y_PARAPET)}",
         # tour
         f"L {P(X_T0, Y_T_ARASE)}", f"L {P(X_T0+0.9, Y_T_ARASE)}",
         f"L {P(X_T0+1.6, Y_T_TOIT)}",
         f"L {P((X_T0+X_T1)/2, Y_T_CROIX)}",
         f"L {P(X_T1-1.6, Y_T_TOIT)}", f"L {P(X_T1-0.9, Y_T_ARASE)}",
         f"L {P(X_T1, Y_T_ARASE)}", f"L {P(X_T1, Y_PARAPET)}",
         f"L {P(HALF, Y_PARAPET)}", f"L {P(HALF, 0)}", "Z"]
    return [path(" ".join(d), id="silhouette")]

def couche_masses():
    return [rect(-HALF, HALF, 0, Y_PARAPET, id="massif"),
            rect(X_T0, X_T1, Y_PARAPET, Y_T_ARASE, id="tour-fut"),
            line(-X_CF, 0, -X_CF, Y_PARAPET),
            line( X_CF, 0,  X_CF, Y_PARAPET)]

def couche_contreforts():
    out = []
    for xc in (-HALF + CF_L/2, -X_CF, X_CF, HALF - CF_L/2):
        out.append(rect(xc-CF_L/2, xc+CF_L/2, 0, Y_PARAPET))
        # ressauts
        for y in (Y_CORN1, Y_APPUI, Y_ARC_BAS):
            out.append(line(xc-CF_L/2-0.12, y, xc+CF_L/2+0.12, y))
    out.append(rect(X_TOURELLE_0, X_TOURELLE_1, Y_PARAPET, Y_T_BAIE2_H))  # tourelle escalier
    return out

def couche_corniches():
    ys = [Y_SOCLE, Y_CORN1, Y_APPUI, Y_BANDEAU, Y_ARC_BAS, Y_ARC_HAUT, Y_CORN2]
    return [line(-HALF, y, HALF, y) for y in ys]

def couche_portails():
    out  = portail(0.0,  2.60, 5.50, 5.35, Y_IMP_CEN, 5)
    out += portail(-X_PORT_LAT, 1.35, 3.30, 3.75, Y_IMP_LAT, 4)
    out += portail( X_PORT_LAT, 1.35, 3.30, 3.75, Y_IMP_LAT, 4)
    return out

def couche_baies():
    out = []
    # grande baie au-dessus du portail central
    out.append(path(baie_cintree(-2.95, 2.95, Y_CORN1 + 0.35, 13.60)))
    # plaques d'inscription de part et d'autre
    out.append(rect(-5.15, -3.35, 11.60, 14.70))
    out.append(rect( 3.35,  5.15, 11.60, 14.70))
    # baies hautes : 2 lancettes par travee laterale
    for xc in (-X_PORT_LAT, X_PORT_LAT):
        out.append(path(baie_cintree(xc-3.05, xc+3.05, Y_APPUI-0.3, Y_LINT-3.05)))  # arc d'encadrement
        for dx in (-1.55, 1.55):
            a = xc + dx - 1.15
            out.append(path(baie_cintree(a, a+2.30, Y_APPUI, Y_LINT-1.30)))
    # baie du pignon
    out.append(path(baie_ogivale(-1.30, 1.30, Y_PARAPET+0.4, Y_PARAPET+2.2, Y_PARAPET+3.9)))
    return out

def couche_arcature():
    out = []
    out += arcature(-HALF+CF_L, -X_CF-CF_L/2, Y_ARC_BAS, Y_ARC_HAUT, 4)
    out += arcature( X_CF+CF_L/2, HALF-CF_L, Y_ARC_BAS, Y_ARC_HAUT, 4)
    # medaillons autour de la rosace
    for dx in (-4.35, 4.35):
        for dy in (2.55, -2.55):
            out.append(circle(dx, ROSE_Y+dy, 0.52))
    return out

def couche_tour():
    out = []
    # abat-sons : 2 baies jumelees par niveau
    xm_t = (X_T0 + X_T1) / 2
    for (yb, yh) in ((Y_T_BAIE1_B, Y_T_BAIE1_H), (Y_T_BAIE2_B, Y_T_BAIE2_H)):
        larg, ecart = 2.60, 0.90
        for i in (-1, 1):
            a = xm_t + i*ecart/2 + (0 if i > 0 else -larg)
            out.append(path(baie_cintree(a, a+larg, yb, yh - larg/2)))
            # arcade aveugle d'encadrement
            out.append(path(baie_cintree(a-0.35, a+larg+0.35, yb-0.4, yh - larg/2 + 0.35)))
    out.append(line(X_T0, Y_T_CORN, X_T1, Y_T_CORN))
    # tourelles d'angle
    for x in (X_T0, X_T1-1.0):
        out.append(rect(x, x+1.0, Y_T_BAIE2_B-1.0, Y_T_ARASE+1.4))
    # couronnement : toit, lanternon, croix
    xm = (X_T0 + X_T1)/2
    out.append(path(f"M {P(X_T0+1.6, Y_T_ARASE)} L {P(xm-1.55, Y_T_TOIT)} "
                    f"L {P(xm+1.55, Y_T_TOIT)} L {P(X_T1-1.6, Y_T_ARASE)} Z"))
    out.append(rect(xm-1.55, xm+1.55, Y_T_TOIT, Y_T_LANT))
    out.append(path(baie_cintree(xm-1.05, xm+1.05, Y_T_TOIT+0.3, Y_T_LANT-1.05)))
    out.append(path(f"M {P(xm-1.55, Y_T_LANT)} L {P(xm, Y_T_FLECHE+0.9)} "
                    f"L {P(xm+1.55, Y_T_LANT)} Z"))
    out.append(line(xm, Y_T_FLECHE+0.9, xm, Y_T_CROIX))
    out.append(line(xm-0.45, Y_T_CROIX-0.65, xm+0.45, Y_T_CROIX-0.65))
    return out

def couche_pignon():
    return [path(f"M {P(-5.90, Y_PARAPET)} L {P(0, Y_PIGNON)} L {P(5.90, Y_PARAPET)} Z"),
            path(f"M {P(-5.20, Y_PARAPET)} L {P(0, Y_PIGNON-1.05)} L {P(5.20, Y_PARAPET)} Z"),
            line(0, Y_PIGNON, 0, Y_STATUE),
            circle(0, Y_STATUE-0.55, 0.55)]

def couche_crenelage():
    return [crenelage(-HALF, -5.90, Y_CORN2, Y_PARAPET),
            crenelage(5.90, X_T0, Y_CORN2, Y_PARAPET),
            crenelage(X_T1, HALF, Y_CORN2, Y_PARAPET),
            crenelage(X_T0, X_T1, Y_T_ARASE-0.8, Y_T_ARASE)]

def couche_calage():
    out = [line(0, 0, 0, Y_STATUE, stroke="#ff00ff", stroke_width="4",
                stroke_dasharray="60,40"),
           line(-HALF-1, 0, HALF+1, 0, stroke="#ff00ff", stroke_width="6")]
    # mire d'echelle : 5 m
    out.append(rect(-HALF, -HALF+5.0, -0.0, 0.0))
    for i in range(6):
        out.append(line(-HALF+i, 0, -HALF+i, 0.45, stroke="#ff00ff", stroke_width="4"))
    out.append(f'<text x="{sx(-HALF)}" y="{sy(0)-60}" font-size="45" fill="#ff00ff">'
               f'0 ---- 5 m (1 unite SVG = 1 cm)</text>')
    # croix de calage aux 4 angles
    for x in (-HALF, HALF):
        for y in (0, Y_PARAPET):
            out.append(line(x-0.5, y, x+0.5, y, stroke="#ff00ff", stroke_width="4"))
            out.append(line(x, y-0.5, x, y+0.5, stroke="#ff00ff", stroke_width="4"))
    return out

# ----------------------------------------------------------------------------
# assemblage
# ----------------------------------------------------------------------------
STYLE_TRAIT = 'fill="none" stroke="#000000" stroke-width="3" stroke-linejoin="round"'

def layer(nom, contenu, style=STYLE_TRAIT, visible=True):
    return (f'\n<g inkscape:groupmode="layer" id="{nom}" inkscape:label="{nom}" '
            f'{style} {"" if visible else "display:none"}>\n  '
            + "\n  ".join(contenu) + f"\n</g>")

def document(layers, titre):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="3250" height="6100" viewBox="0 0 3250 6100" version="1.1">
  <title>{titre}</title>
  <desc>Basilique-cathedrale de Saint-Denis - facade occidentale - elevation
  1 unite SVG = 1 cm reel. Largeur 32,50 m. Hauteur document 61,00 m.
  Sol = bord inferieur du viewBox. Axe de symetrie = x 1625.
  Releve photogrammetrique approche - A RECALER PAR RELEVE SUR SITE.</desc>
{''.join(layers)}
</svg>
'''

def main():
    ici = os.path.dirname(os.path.abspath(__file__))

    # ---- fichier 1 : elevation complete, multi-couches (MadMapper / AE) ----
    L = [layer("00-CALAGE",       couche_calage(), 'fill="none"'),
         layer("10-CONTOUR",      couche_contour()),
         layer("20-MASSES",       couche_masses()),
         layer("30-CONTREFORTS",  couche_contreforts()),
         layer("40-CORNICHES",    couche_corniches()),
         layer("50-PORTAILS",     couche_portails()),
         layer("60-ROSACE",       rosace()),
         layer("70-BAIES",        couche_baies()),
         layer("80-ARCATURES",    couche_arcature()),
         layer("85-PIGNON",       couche_pignon()),
         layer("90-TOUR",         couche_tour()),
         layer("95-CRENELAGE",    couche_crenelage())]
    open(os.path.join(ici, "facade-saint-denis_ELEVATION.svg"), "w").write(
        document(L, "Saint-Denis - facade occidentale - elevation complete"))

    # ---- fichier 2 : version laser, trait simple, peu de points ----
    laser = [layer("LASER-CONTOUR", couche_contour(),
                   'fill="none" stroke="#00ff00" stroke-width="6"'),
             layer("LASER-STRUCTURE",
                   [line(-HALF, Y_CORN1, HALF, Y_CORN1),
                    line(-HALF, Y_APPUI, HALF, Y_APPUI),
                    line(-HALF, Y_CORN2, HALF, Y_CORN2),
                    line(-X_CF, 0, -X_CF, Y_PARAPET),
                    line( X_CF, 0,  X_CF, Y_PARAPET),
                    line(-HALF+CF_L, 0, -HALF+CF_L, Y_PARAPET),
                    line( HALF-CF_L, 0,  HALF-CF_L, Y_PARAPET)],
                   'fill="none" stroke="#00ff00" stroke-width="6"'),
             layer("LASER-ROSACE",
                   [circle(ROSE_X, ROSE_Y, ROSE_R_EXT),
                    circle(ROSE_X, ROSE_Y, ROSE_R_VIT),
                    circle(ROSE_X, ROSE_Y, ROSE_R_INT)]
                   + [line(ROSE_X + ROSE_R_INT*math.cos(2*math.pi*i/12 - math.pi/2),
                           ROSE_Y + ROSE_R_INT*math.sin(2*math.pi*i/12 - math.pi/2),
                           ROSE_X + ROSE_R_VIT*math.cos(2*math.pi*i/12 - math.pi/2),
                           ROSE_Y + ROSE_R_VIT*math.sin(2*math.pi*i/12 - math.pi/2))
                      for i in range(12)],
                   'fill="none" stroke="#00ff00" stroke-width="6"'),
             layer("LASER-PORTAILS",
                   [path(baie_cintree(-2.60, 2.60, 0, Y_IMP_CEN)),
                    path(baie_cintree(-X_PORT_LAT-1.35, -X_PORT_LAT+1.35, 0, Y_IMP_LAT)),
                    path(baie_cintree( X_PORT_LAT-1.35,  X_PORT_LAT+1.35, 0, Y_IMP_LAT))],
                   'fill="none" stroke="#00ff00" stroke-width="6"'),
             layer("LASER-PIGNON-TOUR",
                   [path(f"M {P(-5.90, Y_PARAPET)} L {P(0, Y_PIGNON)} L {P(5.90, Y_PARAPET)} Z"),
                    rect(X_T0, X_T1, Y_PARAPET, Y_T_ARASE),
                    path(f"M {P(X_T0+1.6, Y_T_ARASE)} L {P((X_T0+X_T1)/2, Y_T_CROIX)} "
                         f"L {P(X_T1-1.6, Y_T_ARASE)} Z")],
                   'fill="none" stroke="#00ff00" stroke-width="6"')]
    open(os.path.join(ici, "facade-saint-denis_LASER.svg"), "w").write(
        document(laser, "Saint-Denis - facade occidentale - trace laser simplifie"))

    # ---- fichier 3 : masque plein (alpha) pour Resolume / AE ----
    masque = [layer("MASQUE", couche_contour(), 'fill="#ffffff" stroke="none"')]
    open(os.path.join(ici, "facade-saint-denis_MASQUE.svg"), "w").write(
        document(masque, "Saint-Denis - masque de silhouette"))

    print("3 SVG generes dans", ici)
    print(f"  largeur modele {W_TOT} m  |  hauteur doc {H_DOC} m")

if __name__ == "__main__":
    main()
