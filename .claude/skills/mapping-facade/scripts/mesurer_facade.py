#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mesurer_facade.py — extraire des mesures exploitables d'une photo de facade.

Fait partie de la skill `mapping-facade`.
Dependances : pillow, numpy  (pip install pillow numpy)

Ce que ca fait, et pourquoi
---------------------------
Sur une elevation photographique, trois choses se mesurent de facon fiable et
reproductible, sans jugement a l'oeil :

  1. la SILHOUETTE contre le ciel (segmentation couleur) — c'est la mesure la
     plus sure de toutes, et c'est exactement ce dont le masque a besoin ;
  2. les LIGNES HORIZONTALES structurantes (corniches, bandeaux, appuis), par
     energie de gradient vertical cumulee sur une bande ;
  3. les LIGNES VERTICALES (contreforts, refends, travees), symetriquement.

Le reste — ouvertures, moulures — se lit a l'oeil sur un recadrage agrandi :
l'automatiser donne des resultats moins fiables que l'operateur, parce que les
ombres portees ont le meme contraste que la pierre.

SOUS-COMMANDES

  silhouette  profil du toit contre le ciel + bords du bati
  lignes      corniches et contreforts dans une zone donnee
  calibrer    echelle px/m par recoupement de cotes publiees  <- le plus important
  recadrer    extrait un detail agrandi, pour le lire a l'oeil

EXEMPLES

  python3 mesurer_facade.py silhouette facade.jpg
  python3 mesurer_facade.py lignes facade.jpg --zone 140,800,1000,1990
  python3 mesurer_facade.py calibrer --sol 1935 --controle 1040=29 --controle 153=58
  python3 mesurer_facade.py recadrer facade.jpg --boite 820,1700,1120,2007 --zoom 3
"""

import argparse
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("Il manque pillow et/ou numpy :  pip install pillow numpy")


# ---------------------------------------------------------------- silhouette
def profil_ciel(chemin, marge_bleu=40, mini_bleu=90, confirmation=15):
    """Pour chaque colonne, l'ordonnee du premier pixel de bati sous le ciel.

    `confirmation` : on n'accepte un pixel que si les N suivants sont aussi du
    bati. Sans ca, une trainee d'avion ou un oiseau cree un faux sommet."""
    im = Image.open(chemin).convert("RGB")
    a = np.asarray(im).astype(int)
    H, W, _ = a.shape
    R, B = a[:, :, 0], a[:, :, 2]
    ciel = (B - R > marge_bleu) & (B > mini_bleu)
    # sentinelle = H : colonne entierement ciel, PAS de bati.
    # Sans ca une colonne de ciel pur se lit comme un sommet a y=0 et fausse
    # la detection des bords du bati.
    prof = np.full(W, H, dtype=int)
    for x in range(W):
        for y in np.where(~ciel[:, x])[0]:
            if y + confirmation < H and (~ciel[y:y + confirmation, x]).all():
                prof[x] = y
                break
    return prof, (W, H), ciel


def bords_bati(prof, H, marge=40):
    """Bords gauche/droit du volume principal : la ou le profil decroche.

    Les colonnes sans bati (sentinelle H) sont ecartees avant de prendre la
    mediane, sinon elles tirent la reference vers le bas."""
    bati = prof[prof < H]
    if len(bati) == 0:
        return None, None
    med = np.median(bati)
    hauts = np.where((prof < med - marge) & (prof < H))[0]
    if len(hauts) == 0:
        return None, None
    return int(hauts[0]), int(hauts[-1])


def cmd_silhouette(args):
    prof, (W, H), ciel = profil_ciel(args.photo, args.marge_bleu)
    g, d = bords_bati(prof, H)
    vides = int((prof >= H).sum())
    print(f"photo            {W} x {H} px")
    print(f"ciel detecte     {100*ciel.mean():.0f} % de l'image")
    if vides:
        print(f"colonnes sans bati  {vides} (ciel jusqu'au sol)")
    print(f"point le plus haut   x={int(prof.argmin())}  y={int(prof.min())}")
    if g is not None:
        print(f"volume saillant  x = {g} .. {d}   (largeur {d-g} px)"
              f"   [partie qui depasse la ligne de toiture mediane]")
    print("\nprofil (x, y) tous les", args.pas, "px   (-- = pas de bati) :")
    for x in range(0, W, args.pas):
        v = int(prof[x])
        print(f"  {x:5d} {'   --' if v >= H else f'{v:5d}'}")
    if args.polyligne:
        pts = [(x, int(prof[x])) for x in range(0, W, args.pas)
               if prof[x] < H]
        print("\npolyligne SVG (coordonnees photo) :")
        print("M " + " L ".join(f"{x},{y}" for x, y in pts))


# ------------------------------------------------------------------- lignes
def _pics(serie, seuil, voisinage):
    s = (serie - serie.min()) / (serie.max() - serie.min() + 1e-9)
    return [(i, round(float(s[i]), 2)) for i in range(len(s))
            if s[i] > seuil and s[i] == s[max(0, i - voisinage):
                                          i + voisinage + 1].max()]


def cmd_lignes(args):
    a = np.asarray(Image.open(args.photo).convert("L")).astype(float)
    x0, y0, x1, y1 = args.zone
    gy = np.abs(np.diff(a, axis=0))
    gx = np.abs(np.diff(a, axis=1))

    h = gy[y0:y1, x0:x1].sum(axis=1)
    v = gx[y0:y1, x0:x1].sum(axis=0)

    print(f"zone analysee : x {x0}..{x1}, y {y0}..{y1}\n")
    print("LIGNES HORIZONTALES (corniches, bandeaux, appuis) — y, force :")
    for i, s in _pics(h, args.seuil, args.voisinage):
        print(f"   y = {y0+i:5d}   {s}")
    print("\nLIGNES VERTICALES (contreforts, refends, travees) — x, force :")
    for i, s in _pics(v, args.seuil, args.voisinage):
        print(f"   x = {x0+i:5d}   {s}")
    print("\nLes pics proches par paires sont les deux aretes d'un meme element.")


# ---------------------------------------------------------------- calibrage
def cmd_calibrer(args):
    """L'etape qui decide de tout.

    On ne calibre JAMAIS sur une seule reference : une erreur de calage ne se
    voit pas, elle se propage silencieusement dans toute l'etude (surfaces,
    lumens, optique). Deux cotes publiees independantes qui convergent a
    quelques pourcents, c'est une preuve ; une seule, c'est une hypothese."""
    sol = args.sol
    vals = []
    print(f"sol a y = {sol} px\n")
    print(f"{'repere (y px)':>16} {'cote (m)':>10} {'px/m':>9}")
    for c in args.controle:
        y, m = c.split("=")
        y, m = int(y), float(m)
        k = (sol - y) / m
        vals.append(k)
        print(f"{y:>16} {m:>10.2f} {k:>9.3f}")

    k = float(np.mean(vals))
    if len(vals) > 1:
        ecart = (max(vals) - min(vals)) / k * 100
        print(f"\nechelle retenue  {k:.2f} px/m   (dispersion {ecart:.1f} %)")
        if ecart > 5:
            print("  /!\\ plus de 5 % d'ecart : une des deux cotes publiees ne")
            print("      designe pas ce que tu crois (hauteur sous voute plutot")
            print("      que hauteur de facade ?), ou la photo a de la")
            print("      perspective residuelle. A trancher avant de continuer.")
        else:
            print("  deux references independantes convergent : calage solide.")
    else:
        print(f"\nechelle  {k:.2f} px/m")
        print("  /!\\ une seule reference = hypothese non verifiee.")
        print("      Ajoute un second --controle avant de batir quoi que ce soit.")

    if args.largeur_px:
        print(f"\nlargeur mesuree {args.largeur_px} px "
              f"-> {args.largeur_px/k:.2f} m")
    if args.convertir:
        print("\nconversions demandees (y px -> m au-dessus du sol) :")
        for y in args.convertir:
            print(f"   y = {y:5d}  ->  {(sol-y)/k:7.2f} m")


# ---------------------------------------------------------------- recadrage
def cmd_recadrer(args):
    im = Image.open(args.photo)
    x0, y0, x1, y1 = args.boite
    out = im.crop((x0, y0, x1, y1))
    out = out.resize((int(out.width * args.zoom), int(out.height * args.zoom)))
    out.save(args.sortie)
    print(f"{args.sortie}  ({out.width} x {out.height}, zoom {args.zoom}x)")
    print(f"pour revenir aux coordonnees photo : x_photo = {x0} + x_crop/{args.zoom}")


# -------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("silhouette", help="profil du bati contre le ciel")
    s.add_argument("photo")
    s.add_argument("--pas", type=int, default=40)
    s.add_argument("--marge-bleu", type=int, default=40)
    s.add_argument("--polyligne", action="store_true")
    s.set_defaults(func=cmd_silhouette)

    s = sub.add_parser("lignes", help="corniches et contreforts")
    s.add_argument("photo")
    s.add_argument("--zone", type=lambda v: [int(i) for i in v.split(",")],
                   required=True, metavar="x0,y0,x1,y1")
    s.add_argument("--seuil", type=float, default=0.30)
    s.add_argument("--voisinage", type=int, default=6)
    s.set_defaults(func=cmd_lignes)

    s = sub.add_parser("calibrer", help="echelle px/m par recoupement")
    s.add_argument("--sol", type=int, required=True)
    s.add_argument("--controle", action="append", required=True,
                   metavar="Ypx=METRES",
                   help="repete une fois par cote publiee ; au moins deux")
    s.add_argument("--largeur-px", type=int)
    s.add_argument("--convertir", type=int, nargs="*", default=[])
    s.set_defaults(func=cmd_calibrer)

    s = sub.add_parser("recadrer", help="detail agrandi a lire a l'oeil")
    s.add_argument("photo")
    s.add_argument("--boite", type=lambda v: [int(i) for i in v.split(",")],
                   required=True, metavar="x0,y0,x1,y1")
    s.add_argument("--zoom", type=float, default=3.0)
    s.add_argument("--sortie", default="detail.png")
    s.set_defaults(func=cmd_recadrer)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # sorties longues souvent passees dans `head` ou `less`
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
