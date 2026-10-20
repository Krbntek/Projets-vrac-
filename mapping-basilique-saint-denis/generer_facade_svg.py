#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elevation vectorielle de la facade occidentale de la basilique-cathedrale
de Saint-Denis, pour mapping video (Resolume) et laser (MadMapper).

Produit 3 SVG :
    facade-saint-denis_ELEVATION.svg   12 calques, fichier de travail
    facade-saint-denis_MASQUE.svg      silhouette pleine, masque alpha
    facade-saint-denis_LASER.svg       trace simplifie, trait seul

Methode, conventions et primitives : skill `mapping-facade`.
La bibliotheque svg_facade.py est copiee ici volontairement, pour que ce
dossier reste autonome s'il part chez un prestataire.

CALAGE (detail dans CALCULS-MAPPING.md, section 1)
    photo de reference 1280 x 2007 px
    sol y = 1935 px | axe x = 645 px | echelle 30,70 px/m
    recoupee sur deux cotes publiees : corps de facade 29 m, tour sud 58 m,
    convergentes a 0,5 % -> largeur de massif deduite 32,50 m.

RECALAGE APRES RELEVE SUR SITE : modifier les constantes ci-dessous et
relancer. Les 3 SVG se refont coherents.
"""

import os
from svg_facade import Facade, apercu_png

# ---------------------------------------------------------------- MODELE (m)
W_TOT = 32.50          # largeur hors-tout du massif occidental
HALF = W_TOT / 2.0
H_DOC = 61.00          # hauteur du document

Y_SOCLE      =  1.40   # larmier du soubassement
Y_IMP_LAT    =  4.90   # imposte des portails lateraux
Y_IMP_CEN    =  5.40   # imposte du portail central
Y_CORN1      = 10.60   # grande corniche au-dessus des portails
Y_APPUI      = 12.20   # appui des baies hautes
Y_BANDEAU    = 18.80   # bandeau a mi-hauteur des baies
Y_LINT       = 23.00   # sommet des baies hautes
Y_ARC_BAS    = 23.10   # naissance de l'arcature a statues
Y_ARC_HAUT   = 25.90   # sommet de l'arcature
Y_CORN2      = 28.40   # corniche sous le parapet
Y_PARAPET    = 29.20   # arase du parapet crenele   (cote publiee 29 m)
Y_PIGNON     = 37.30   # sommet du pignon central
Y_STATUE     = 38.40   # sommet de la statue du pignon

X_CF         =  5.65   # axe des 2 contreforts separant les travees
CF_L         =  1.95   # largeur des contreforts
X_PORT_LAT   =  9.60   # axe des portails lateraux

ROSE_X, ROSE_Y = 0.00, 22.50          # rosace-horloge
ROSE_R = (3.00, 2.35, 2.15, 0.95)     # cadre / cadran / vitrail / oculus

X_T0, X_T1   =  5.20, 15.80           # emprise de la tour sud
Y_T_BAIE1_B, Y_T_BAIE1_H = 30.10, 36.30   # abat-sons bas
Y_T_CORN     = 36.60
Y_T_BAIE2_B, Y_T_BAIE2_H = 37.00, 49.00   # abat-sons hauts
Y_T_ARASE    = 50.60   # corniche sommitale de la tour carree
Y_T_TOIT     = 54.60   # base du lanternon
Y_T_LANT     = 57.60   # sommet des colonnettes
Y_T_FLECHE   = 58.00   # pointe                     (cote publiee 58 m)
Y_T_CROIX    = 60.10   # croix + girouette
X_TOURELLE   = (4.05, 5.25)           # tourelle d'escalier

F = Facade(largeur_m=W_TOT, hauteur_doc_m=H_DOC)
XM_T = (X_T0 + X_T1) / 2


# ------------------------------------------------------------------ calques
def contour():
    """Silhouette generale : le masque de base pour MadMapper / Resolume."""
    return [F.polygone([
        (-HALF, 0), (-HALF, Y_CORN2), (-HALF, Y_PARAPET),
        (-5.90, Y_PARAPET), (0, Y_PIGNON), (5.90, Y_PARAPET),
        (X_T0, Y_PARAPET), (X_T0, Y_T_ARASE), (X_T0 + 0.9, Y_T_ARASE),
        (X_T0 + 1.6, Y_T_TOIT), (XM_T, Y_T_CROIX),
        (X_T1 - 1.6, Y_T_TOIT), (X_T1 - 0.9, Y_T_ARASE),
        (X_T1, Y_T_ARASE), (X_T1, Y_PARAPET),
        (HALF, Y_PARAPET), (HALF, 0)], id="silhouette")]


def masses():
    return [F.rect(-HALF, HALF, 0, Y_PARAPET, id="massif"),
            F.rect(X_T0, X_T1, Y_PARAPET, Y_T_ARASE, id="tour-fut"),
            F.ligne(-X_CF, 0, -X_CF, Y_PARAPET),
            F.ligne(X_CF, 0, X_CF, Y_PARAPET)]


def contreforts():
    out = []
    for xc in (-HALF + CF_L / 2, -X_CF, X_CF, HALF - CF_L / 2):
        out += F.contrefort(xc, CF_L, 0, Y_PARAPET,
                            ressauts=(Y_CORN1, Y_APPUI, Y_ARC_BAS))
    out.append(F.rect(X_TOURELLE[0], X_TOURELLE[1], Y_PARAPET, Y_T_BAIE2_H))
    return out


def corniches():
    return [F.ligne(-HALF, y, HALF, y) for y in
            (Y_SOCLE, Y_CORN1, Y_APPUI, Y_BANDEAU, Y_ARC_BAS, Y_ARC_HAUT,
             Y_CORN2)]


def portails():
    return (F.portail(0.0, 2.60, 5.50, 5.35, Y_IMP_CEN, 5)
            + F.portail(-X_PORT_LAT, 1.35, 3.30, 3.75, Y_IMP_LAT, 4)
            + F.portail(X_PORT_LAT, 1.35, 3.30, 3.75, Y_IMP_LAT, 4))


def baies():
    out = [F.baie_cintree(-2.95, 2.95, Y_CORN1 + 0.35, 13.60),   # baie centrale
           F.rect(-5.15, -3.35, 11.60, 14.70),                   # plaques
           F.rect(3.35, 5.15, 11.60, 14.70)]
    for xc in (-X_PORT_LAT, X_PORT_LAT):                         # lancettes
        out.append(F.baie_cintree(xc - 3.05, xc + 3.05, Y_APPUI - 0.3,
                                  Y_LINT - 3.05))
        for dx in (-1.55, 1.55):
            a = xc + dx - 1.15
            out.append(F.baie_cintree(a, a + 2.30, Y_APPUI, Y_LINT - 1.30))
    out.append(F.baie_ogivale(-1.30, 1.30, Y_PARAPET + 0.4,
                              Y_PARAPET + 2.2, Y_PARAPET + 3.9))
    return out


def arcatures():
    out = (F.arcature(-HALF + CF_L, -X_CF - CF_L / 2, Y_ARC_BAS, Y_ARC_HAUT, 4)
           + F.arcature(X_CF + CF_L / 2, HALF - CF_L, Y_ARC_BAS, Y_ARC_HAUT, 4))
    for dx in (-4.35, 4.35):                                     # medaillons
        for dy in (2.55, -2.55):
            out.append(F.cercle(dx, ROSE_Y + dy, 0.52))
    return out


def tour():
    out = []
    for yb, yh in ((Y_T_BAIE1_B, Y_T_BAIE1_H), (Y_T_BAIE2_B, Y_T_BAIE2_H)):
        larg, ecart = 2.60, 0.90
        for i in (-1, 1):
            a = XM_T + i * ecart / 2 + (0 if i > 0 else -larg)
            out.append(F.baie_cintree(a, a + larg, yb, yh - larg / 2))
            out.append(F.baie_cintree(a - 0.35, a + larg + 0.35, yb - 0.4,
                                      yh - larg / 2 + 0.35))
    out.append(F.ligne(X_T0, Y_T_CORN, X_T1, Y_T_CORN))
    for x in (X_T0, X_T1 - 1.0):                                 # tourelles
        out.append(F.rect(x, x + 1.0, Y_T_BAIE2_B - 1.0, Y_T_ARASE + 1.4))
    out.append(F.polygone([(X_T0 + 1.6, Y_T_ARASE), (XM_T - 1.55, Y_T_TOIT),
                           (XM_T + 1.55, Y_T_TOIT), (X_T1 - 1.6, Y_T_ARASE)]))
    out.append(F.rect(XM_T - 1.55, XM_T + 1.55, Y_T_TOIT, Y_T_LANT))
    out.append(F.baie_cintree(XM_T - 1.05, XM_T + 1.05, Y_T_TOIT + 0.3,
                              Y_T_LANT - 1.05))
    out.append(F.polygone([(XM_T - 1.55, Y_T_LANT), (XM_T, Y_T_FLECHE + 0.9),
                           (XM_T + 1.55, Y_T_LANT)]))
    out.append(F.ligne(XM_T, Y_T_FLECHE + 0.9, XM_T, Y_T_CROIX))
    out.append(F.ligne(XM_T - 0.45, Y_T_CROIX - 0.65,
                       XM_T + 0.45, Y_T_CROIX - 0.65))
    return out


def pignon():
    return F.pignon(-5.90, 5.90, Y_PARAPET, Y_PIGNON, retrait=0.70) + [
        F.ligne(0, Y_PIGNON, 0, Y_STATUE),
        F.cercle(0, Y_STATUE - 0.55, 0.55)]


def crenelage():
    return [F.crenelage(-HALF, -5.90, Y_CORN2, Y_PARAPET),
            F.crenelage(5.90, X_T0, Y_CORN2, Y_PARAPET),
            F.crenelage(X_T1, HALF, Y_CORN2, Y_PARAPET),
            F.crenelage(X_T0, X_T1, Y_T_ARASE - 0.8, Y_T_ARASE)]


# --------------------------------------------------------------- assemblage
DESC = ("Basilique-cathedrale de Saint-Denis - facade occidentale - elevation.\n"
        "  Releve photogrammetrique approche (+/- 3 a 5 %) - A RECALER SUR SITE.")


def main():
    ici = os.path.dirname(os.path.abspath(__file__))
    chemin = lambda n: os.path.join(ici, n)

    # 1 — elevation complete, multi-calques
    (F.vider()
     .calque("00-CALAGE", F.calque_calage(Y_STATUE, y_croix=Y_PARAPET), 'fill="none"')
     .calque("10-CONTOUR", contour())
     .calque("20-MASSES", masses())
     .calque("30-CONTREFORTS", contreforts())
     .calque("40-CORNICHES", corniches())
     .calque("50-PORTAILS", portails())
     .calque("60-ROSACE", F.rosace(ROSE_X, ROSE_Y, ROSE_R,
                                   r_rayons=(ROSE_R[3], ROSE_R[2])))
     .calque("70-BAIES", baies())
     .calque("80-ARCATURES", arcatures())
     .calque("85-PIGNON", pignon())
     .calque("90-TOUR", tour())
     .calque("95-CRENELAGE", crenelage())
     .ecrire(chemin("facade-saint-denis_ELEVATION.svg"),
             "Saint-Denis - facade occidentale - elevation complete", DESC))

    # 2 — masque alpha
    (F.vider()
     .calque("MASQUE", contour(), F.PLEIN)
     .ecrire(chemin("facade-saint-denis_MASQUE.svg"),
             "Saint-Denis - masque de silhouette", DESC))

    # 3 — trace laser : trait seul, peu de points (budget ~1000 pts/image)
    (F.vider()
     .calque("LASER-CONTOUR", contour(), F.LASER)
     .calque("LASER-STRUCTURE", [
         F.ligne(-HALF, Y_CORN1, HALF, Y_CORN1),
         F.ligne(-HALF, Y_APPUI, HALF, Y_APPUI),
         F.ligne(-HALF, Y_CORN2, HALF, Y_CORN2),
         F.ligne(-X_CF, 0, -X_CF, Y_PARAPET),
         F.ligne(X_CF, 0, X_CF, Y_PARAPET),
         F.ligne(-HALF + CF_L, 0, -HALF + CF_L, Y_PARAPET),
         F.ligne(HALF - CF_L, 0, HALF - CF_L, Y_PARAPET)], F.LASER)
     .calque("LASER-ROSACE", F.rosace(ROSE_X, ROSE_Y,
                                      (ROSE_R[0], ROSE_R[2], ROSE_R[3]),
                                      r_oculus=0, decal=0,
                                      r_rayons=(ROSE_R[3], ROSE_R[2])), F.LASER)
     .calque("LASER-PORTAILS", [
         F.baie_cintree(-2.60, 2.60, 0, Y_IMP_CEN),
         F.baie_cintree(-X_PORT_LAT - 1.35, -X_PORT_LAT + 1.35, 0, Y_IMP_LAT),
         F.baie_cintree(X_PORT_LAT - 1.35, X_PORT_LAT + 1.35, 0, Y_IMP_LAT)],
         F.LASER)
     .calque("LASER-PIGNON-TOUR", [
         F.polygone([(-5.90, Y_PARAPET), (0, Y_PIGNON), (5.90, Y_PARAPET)]),
         F.rect(X_T0, X_T1, Y_PARAPET, Y_T_ARASE),
         F.polygone([(X_T0 + 1.6, Y_T_ARASE), (XM_T, Y_T_CROIX),
                     (X_T1 - 1.6, Y_T_ARASE)])], F.LASER)
     .ecrire(chemin("facade-saint-denis_LASER.svg"),
             "Saint-Denis - facade occidentale - trace laser simplifie", DESC))

    apercu_png(chemin("facade-saint-denis_ELEVATION.svg"),
               chemin("apercu-elevation.png"), 1300)
    apercu_png(chemin("facade-saint-denis_LASER.svg"),
               chemin("apercu-laser.png"), 900, fond="black")

    print("3 SVG + 2 apercus generes dans", ici)
    print(f"  massif {W_TOT} m de large | document {H_DOC} m de haut")


if __name__ == "__main__":
    main()
