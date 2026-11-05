#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg_facade.py — bibliotheque de primitives pour dessiner une elevation
d'architecture exploitable en mapping video et laser.

Fait partie de la skill `mapping-facade`. A COPIER dans le dossier du projet
(les dossiers de projet partent chez des prestataires : ils doivent etre
autonomes, sans dependance a un chemin de skill).

CONVENTION, la meme pour tous les projets
-----------------------------------------
    Modele  : X en metres, 0 = axe de symetrie de la facade
              Y en metres, 0 = niveau du sol, vers le HAUT
    SVG     : 1 unite = 1 cm reel, Y vers le bas
              le SOL est sur le bord INFERIEUR du viewBox
              l'axe de symetrie est au MILIEU du viewBox

Cette convention n'est pas decorative : elle fait que n'importe quel contenu
fabrique a N px/m se cale par un simple facteur d'echelle, et que le masque
s'aligne tout seul. Garde-la meme si la facade n'est pas symetrique (dans ce
cas l'axe est juste une reference de calage).

USAGE TYPE (dans generer_facade_svg.py, cote projet)

    from svg_facade import Facade

    F = Facade(largeur_m=32.5, hauteur_doc_m=61.0)

    corps = [F.rect(-16.25, 16.25, 0, 29.2), F.ligne(-16.25, 10.6, 16.25, 10.6)]
    F.calque("20-MASSES", corps)
    ...
    F.ecrire("facade_ELEVATION.svg", titre="...", desc="...")
"""

import math


class Facade:
    """Un document d'elevation. Accumule des calques, puis ecrit le SVG."""

    TRAIT = ('fill="none" stroke="#000000" stroke-width="3" '
             'stroke-linejoin="round"')
    LASER = 'fill="none" stroke="#00ff00" stroke-width="6"'
    PLEIN = 'fill="#ffffff" stroke="none"'
    REPERE = '#ff00ff'

    def __init__(self, largeur_m, hauteur_doc_m):
        self.L = float(largeur_m)
        self.H = float(hauteur_doc_m)
        self.demi = self.L / 2.0
        self._calques = []

    # ---------------------------------------------------------------- repere
    def sx(self, x):
        """X modele (m, 0 = axe) -> x SVG (cm, 0 = bord gauche)."""
        return round((x + self.demi) * 100.0, 1)

    def sy(self, y):
        """Y modele (m, 0 = sol, vers le haut) -> y SVG (cm, vers le bas)."""
        return round((self.H - y) * 100.0, 1)

    def P(self, x, y):
        return f"{self.sx(x)},{self.sy(y)}"

    # ------------------------------------------------------------ primitives
    def _el(self, tag, **kw):
        a = " ".join(f'{k.replace("_", "-")}="{v}"'
                     for k, v in kw.items() if v is not None)
        return f"<{tag} {a}/>"

    def rect(self, x0, x1, y0, y1, **kw):
        return self._el("rect", x=self.sx(x0), y=self.sy(y1),
                        width=round((x1 - x0) * 100, 1),
                        height=round((y1 - y0) * 100, 1), **kw)

    def ligne(self, x0, y0, x1, y1, **kw):
        return self._el("line", x1=self.sx(x0), y1=self.sy(y0),
                        x2=self.sx(x1), y2=self.sy(y1), **kw)

    def cercle(self, cx, cy, r, **kw):
        return self._el("circle", cx=self.sx(cx), cy=self.sy(cy),
                        r=round(r * 100, 1), **kw)

    def chemin(self, d, **kw):
        return self._el("path", d=d, **kw)

    def polygone(self, points, ferme=True, **kw):
        d = "M " + " L ".join(self.P(x, y) for x, y in points)
        return self.chemin(d + (" Z" if ferme else ""), **kw)

    # ------------------------------------------------------------ baies
    def baie_cintree(self, x0, x1, y_base, y_naissance, **kw):
        """Plein cintre : montants droits + demi-cercle. Chemin ferme."""
        r = (x1 - x0) / 2.0
        d = (f"M {self.P(x0, y_base)} L {self.P(x0, y_naissance)} "
             f"A {r*100:.1f},{r*100:.1f} 0 0 1 {self.P(x1, y_naissance)} "
             f"L {self.P(x1, y_base)} Z")
        return self.chemin(d, **kw)

    def baie_ogivale(self, x0, x1, y_base, y_naissance, y_sommet, **kw):
        """Arc brise : deux arcs de cercle se rejoignant au sommet."""
        cx = (x0 + x1) / 2.0
        demi = (x1 - x0) / 2.0
        h = y_sommet - y_naissance
        r = (demi * demi + h * h) / (2 * h) if h > 0 else demi
        R = round(r * 100, 1)
        d = (f"M {self.P(x0, y_base)} L {self.P(x0, y_naissance)} "
             f"A {R},{R} 0 0 1 {self.P(cx, y_sommet)} "
             f"A {R},{R} 0 0 1 {self.P(x1, y_naissance)} "
             f"L {self.P(x1, y_base)} Z")
        return self.chemin(d, **kw)

    # ------------------------------------------------------------ composes
    def portail(self, xc, demi_ouverture, y_linteau, demi_archivolte,
                y_imposte, n_voussures=4, retrait=0.9):
        """Portail ebrase : vantail + voussures concentriques + imposte.

        Les voussures sont emboitees et reculent de `retrait` au total : c'est
        ce qui donne la lecture de profondeur une fois la lumiere dessus."""
        out = [self.rect(xc - demi_ouverture, xc + demi_ouverture, 0, y_linteau)]
        for i in range(n_voussures + 1):
            t = i / n_voussures
            d = demi_ouverture + (demi_archivolte - demi_ouverture) * t
            out.append(self.baie_cintree(xc - d, xc + d,
                                         y_imposte - retrait * t, y_imposte))
        out.append(self.ligne(xc - demi_archivolte, y_imposte,
                              xc + demi_archivolte, y_imposte))
        return out

    def rosace(self, cx, cy, rayons, n_lobes=12, r_oculus=0.26, decal=0.35,
               r_rayons=None):
        """Rosace / rose : anneaux concentriques, rayons droits, oculus de lobe.

        `rayons` : les anneaux a tracer, dans l'ordre que tu veux.
        `r_rayons` : (interieur, exterieur) ou s'arretent les rayons droits.
        Par defaut du plus petit anneau au deuxieme plus grand — mais sur une
        rose a cadre mouluré large, precise-le, sinon les rayons debordent
        dans la moulure. Attention au cout en points si la figure sert aussi
        en laser (voir references/laser-ilda.md : un cercle propre coute 60 a
        100 points, et le budget total est de l'ordre de 1000)."""
        out = [self.cercle(cx, cy, r) for r in rayons]
        r_int, r_vit = r_rayons if r_rayons else (min(rayons),
                                                  sorted(rayons)[-2])
        for i in range(n_lobes):
            a = 2 * math.pi * i / n_lobes - math.pi / 2
            out.append(self.ligne(cx + r_int * math.cos(a),
                                  cy + r_int * math.sin(a),
                                  cx + r_vit * math.cos(a),
                                  cy + r_vit * math.sin(a)))
            if r_oculus > 0:            # r_oculus=0 -> pas d'oculus du tout,
                a2 = a + math.pi / n_lobes   # et surtout pas un cercle vide,
                rr = (r_int + r_vit) / 2 + decal   # qui encombrerait le laser
                out.append(self.cercle(cx + rr * math.cos(a2),
                                       cy + rr * math.sin(a2), r_oculus))
        return out

    def crenelage(self, x0, x1, y_bas, y_haut, pas=1.30, plein=0.75,
                  merlon=0.85):
        """Parapet crenele en UNE polyligne : un seul chemin ferme, donc un
        masque propre et un trace laser economique."""
        n = max(1, int((x1 - x0) / pas))
        pas = (x1 - x0) / n
        d = [f"M {self.P(x0, y_bas)}", f"L {self.P(x0, y_haut)}"]
        x = x0
        for _ in range(n):
            a = x + pas * (1 - plein) / 2
            b = x + pas * (1 + plein) / 2
            d += [f"L {self.P(a, y_haut)}", f"L {self.P(a, y_haut + merlon)}",
                  f"L {self.P(b, y_haut + merlon)}", f"L {self.P(b, y_haut)}"]
            x += pas
        d += [f"L {self.P(x1, y_haut)}", f"L {self.P(x1, y_bas)}"]
        return self.chemin(" ".join(d))

    def arcature(self, x0, x1, y_bas, y_haut, n=4, jeu=0.10):
        """Arcature aveugle a colonnettes (bandeaux de statues, galeries)."""
        out, pas = [], (x1 - x0) / n
        for i in range(n):
            a = x0 + i * pas + jeu
            b = a + pas - 2 * jeu
            out.append(self.baie_cintree(a, b, y_bas, y_haut - (b - a) / 2))
        return out

    def contrefort(self, xc, largeur, y0, y1, ressauts=(), debord=0.12):
        out = [self.rect(xc - largeur / 2, xc + largeur / 2, y0, y1)]
        for y in ressauts:
            out.append(self.ligne(xc - largeur / 2 - debord, y,
                                  xc + largeur / 2 + debord, y))
        return out

    def pignon(self, x0, x1, y_base, y_sommet, retrait=0.0):
        out = [self.polygone([(x0, y_base), ((x0 + x1) / 2, y_sommet),
                              (x1, y_base)])]
        if retrait:
            out.append(self.polygone([(x0 + retrait, y_base),
                                      ((x0 + x1) / 2, y_sommet - retrait * 1.5),
                                      (x1 - retrait, y_base)]))
        return out

    # ------------------------------------------------------------ calage
    def calque_calage(self, y_haut, mire=5.0, y_croix=None):
        """Axe, ligne de sol, mire metrique, croix aux angles.

        `y_haut` : jusqu'ou monte l'axe. `y_croix` : hauteur des croix d'angle
        si elle differe (typiquement l'arase du corps de batiment, alors que
        l'axe monte jusqu'au sommet).

        Ce calque n'est pas decoratif : c'est lui qui permet de verifier en
        trois secondes, dans n'importe quel logiciel, que le fichier n'a pas
        ete remis a l'echelle en route."""
        c = self.REPERE
        out = [self.ligne(0, 0, 0, y_haut, stroke=c, stroke_width="4",
                          stroke_dasharray="60,40"),
               self.ligne(-self.demi - 1, 0, self.demi + 1, 0,
                          stroke=c, stroke_width="6")]
        for i in range(int(mire) + 1):
            out.append(self.ligne(-self.demi + i, 0, -self.demi + i, 0.45,
                                  stroke=c, stroke_width="4"))
        out.append(f'<text x="{self.sx(-self.demi)}" y="{self.sy(0)-60}" '
                   f'font-size="45" fill="{c}">0 ---- {mire:.0f} m '
                   f'(1 unite SVG = 1 cm)</text>')
        for x in (-self.demi, self.demi):
            for y in (0, y_croix if y_croix is not None else y_haut):
                out.append(self.ligne(x - 0.5, y, x + 0.5, y, stroke=c,
                                      stroke_width="4"))
                out.append(self.ligne(x, y - 0.5, x, y + 0.5, stroke=c,
                                      stroke_width="4"))
        return out

    # ------------------------------------------------------------ document
    def calque(self, nom, contenu, style=None):
        """Ajoute un calque nomme. Les noms numerotes (10-, 20-, ...) gardent
        l'ordre d'empilement lisible dans Illustrator et MadMapper."""
        self._calques.append((nom, contenu, style or self.TRAIT))
        return self

    def vider(self):
        self._calques = []
        return self

    def rendu(self, titre="", desc=""):
        corps = ""
        for nom, contenu, style in self._calques:
            corps += (f'\n<g inkscape:groupmode="layer" id="{nom}" '
                      f'inkscape:label="{nom}" {style}>\n  '
                      + "\n  ".join(contenu) + "\n</g>")
        w, h = round(self.L * 100), round(self.H * 100)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="{w}" height="{h}" viewBox="0 0 {w} {h}" version="1.1">
  <title>{titre}</title>
  <desc>{desc}
  1 unite SVG = 1 cm reel. Largeur {self.L:.2f} m. Hauteur document {self.H:.2f} m.
  Sol = bord inferieur du viewBox. Axe de symetrie = x {w/2:.0f}.</desc>
{corps}
</svg>
'''

    def ecrire(self, chemin, titre="", desc=""):
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(self.rendu(titre, desc))
        return chemin


def apercu_png(svg, png, largeur=1200, fond="white"):
    """Rendu de controle. Regarde-le : une elevation fausse se voit a l'oeil
    bien plus vite qu'elle ne se lit dans des coordonnees."""
    try:
        import cairosvg
    except ImportError:
        print("cairosvg absent (pip install cairosvg) - apercu saute")
        return None
    cairosvg.svg2png(url=svg, write_to=png, output_width=largeur,
                     background_color=fond)
    return png
