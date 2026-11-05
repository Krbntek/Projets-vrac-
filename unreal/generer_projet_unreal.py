#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_projet_unreal.py — fabrique les fichiers 3D du plan d'implantation
pour Unreal Engine, à partir de implantation.json (version 2 : la même source
que la démo outils/demo-evenement.html et le visualiseur outils/implantation-3d.html).

Produit :
  MappingSaintDenis/Content/Import/Scene/Implantation.glb
        la scène complète : hiérarchie d'acteurs, instances placées,
        lumières (KHR_lights_punctual) — à importer "dans le niveau"
  MappingSaintDenis/Content/Import/Elements/SM_<nom>.glb  +  .obj/.mtl
        un fichier par élément, posé à l'origine, sol à z=0 — pour
        retravailler chaque objet indépendamment
  MappingSaintDenis/Content/Import/placement.json
        les transformations de chaque instance, en cm, repère Unreal

Conventions
  - implantation.json : mètres, X = axe façade, Y = haut, Z = recul.
  - GLB : mètres, Y vers le haut (norme glTF). L'importeur Unreal convertit
    en cm Z-up tout seul (échelle uniforme 100, à laisser par défaut).
  - Les éléments ont leur origine au sol, au centre de leur emprise.

Dépendances : trimesh, shapely, numpy, mapbox_earcut   (pip install trimesh shapely numpy mapbox_earcut)
"""

import json, math, os, re, sys
import numpy as np
import trimesh
from trimesh.creation import box, cylinder, cone, extrude_polygon
from trimesh.visual.material import PBRMaterial
from shapely.geometry import Polygon

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".json") else os.path.join(ICI, "implantation.json")   # python3 generer_projet_unreal.py autre.json
PROJ = os.path.join(ICI, "MappingSaintDenis")
D_SCENE = os.path.join(PROJ, "Content", "Import", "Scene")
D_ELEM = os.path.join(PROJ, "Content", "Import", "Elements")

# ----------------------------------------------------------------- couleurs
def mat(nom, rgb, alpha=1.0, metal=0.0, rough=0.85, emissive=None):
    m = PBRMaterial(name=nom, baseColorFactor=[*rgb, alpha], metallicFactor=metal, roughnessFactor=rough)
    if alpha < 1.0: m.alphaMode = "BLEND"
    if emissive: m.emissiveFactor = emissive
    return m

M = {
    "pierre":   mat("M_Pierre",   (0.85, 0.82, 0.75)),
    "sombre":   mat("M_Sombre",   (0.16, 0.15, 0.13)),
    "vitrail":  mat("M_Vitrail",  (0.11, 0.16, 0.24), rough=0.3, metal=0.1),
    "or":       mat("M_Or",       (0.78, 0.64, 0.29), rough=0.4, metal=0.6),
    "pave":     mat("M_Pave",     (0.54, 0.52, 0.47), rough=1.0),
    "voisin":   mat("M_Voisin",   (0.73, 0.70, 0.63)),
    "nef":      mat("M_Nef",      (0.81, 0.78, 0.71)),
    "toiture":  mat("M_Toiture",  (0.35, 0.33, 0.28)),
    "regie":    mat("M_Regie",    (0.84, 0.87, 0.89), rough=0.5, metal=0.3),
    "galva":    mat("M_Galva",    (0.71, 0.73, 0.76), rough=0.35, metal=0.75),
    "echafaud": mat("M_Echafaud", (0.79, 0.54, 0.24), rough=0.6, metal=0.3),
    "deck":     mat("M_Deck",     (0.56, 0.58, 0.60), rough=0.55, metal=0.5),
    "bois":     mat("M_Bois",     (0.42, 0.33, 0.25), rough=0.9),
    "jupe":     mat("M_Jupe",     (0.05, 0.06, 0.07), rough=0.9),
    "bache":    mat("M_Bache",    (0.95, 0.95, 0.95), alpha=0.55),
    "bacheOp":  mat("M_BacheOpaque", (0.17, 0.18, 0.21), rough=0.9),
    "projo":    mat("M_Projo",    (0.13, 0.15, 0.19), rough=0.4, metal=0.5),
    "noir":     mat("M_Noir",     (0.07, 0.08, 0.10), rough=0.5, metal=0.4),
    "inox":     mat("M_Inox",     (0.55, 0.57, 0.59), rough=0.4, metal=0.6),
    "blanc":    mat("M_Blanc",    (0.93, 0.94, 0.95), rough=0.5, metal=0.2),
    "comptoir": mat("M_Comptoir", (0.42, 0.35, 0.27)),
    "beton":    mat("M_Beton",    (0.60, 0.60, 0.58), rough=0.95),
    "jaune":    mat("M_Jaune",    (1.0, 0.82, 0.25), rough=0.7),
    "cable":    mat("M_Cable",    (0.08, 0.09, 0.11), rough=0.8),
    "ecran":    mat("M_Ecran",    (0.05, 0.05, 0.08), rough=0.3, emissive=(0.6, 0.4, 0.9)),
    "led":      mat("M_LedScene", (1.0, 0.9, 0.7), emissive=(1.0, 0.7, 0.3)),
    "armoire":  mat("M_Armoire",  (0.60, 0.64, 0.68), rough=0.5, metal=0.4),
    "cone":     mat("M_ConeVP",   (1.0, 0.71, 0.33), alpha=0.12, emissive=(0.5, 0.3, 0.1)),
    "laser":    mat("M_Laser",    (0.25, 0.73, 0.31), emissive=(0.2, 0.9, 0.3)),
    "zone":     mat("M_ZonePublic", (0.62, 0.83, 1.0), alpha=0.25),
    "sono":     mat("M_SonoSecteur", (0.94, 0.53, 0.24), alpha=0.12),
    "lum":      mat("M_FaisceauLum", (0.70, 0.42, 1.0), alpha=0.14, emissive=(0.35, 0.2, 0.5)),
}
TENTE = {"prevention": (0.31, 0.64, 1.0), "secours": (0.97, 0.32, 0.29), "accueil": (1.0, 0.71, 0.33),
         "buvette": (0.89, 0.75, 0.35), "asso": (0.91, 0.88, 0.78)}

# ------------------------------------------------------------- primitives
def B(x0, x1, y0, y1, z0, z1, m):
    """boîte par ses bornes, repère modèle (Y haut)."""
    g = box(extents=[x1 - x0, y1 - y0, z1 - z0])
    g.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def CYL(a, b, r, m, seg=12):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a; L = np.linalg.norm(d)
    g = cylinder(radius=r, height=L, sections=seg)
    g.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d / L))
    g.apply_translation((a + b) / 2)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def CONE(sommet, base_centre, rayon, m, seg=24):
    """cône dont la POINTE est au sommet et la base (rayon) au point base_centre."""
    s, b = np.array(sommet, float), np.array(base_centre, float)
    d = b - s; L = np.linalg.norm(d)
    g = cone(radius=rayon, height=L, sections=seg)       # base en z=0, pointe en z=L
    g.apply_translation([0, 0, -L])                         # pointe à l'origine, base en z=-L
    g.apply_transform(trimesh.geometry.align_vectors([0, 0, -1], d / L))   # la base part vers la cible
    g.apply_translation(s)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def PYRAMIDE_CONE(sommet, base_centre, rayon, m):
    return CONE(sommet, base_centre, rayon, m, seg=4)

def FRUSTUM_VP(P, coins, m):
    v = np.array([P] + coins, float)
    f = [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1], [1, 2, 3], [1, 3, 4]]
    g = trimesh.Trimesh(vertices=v, faces=f, process=False)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def PLAN_XZ(x0, x1, z0, z1, y, m):
    v = np.array([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]], float)
    g = trimesh.Trimesh(vertices=v, faces=[[0, 2, 1], [0, 3, 2]], process=False)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def PLAN_XY(x0, x1, y0, y1, z, m):
    v = np.array([[x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z]], float)
    g = trimesh.Trimesh(vertices=v, faces=[[0, 1, 2], [0, 2, 3]], process=False)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def PLAN_YZ(x, y0, y1, z0, z1, m):
    v = np.array([[x, y0, z0], [x, y0, z1], [x, y1, z1], [x, y1, z0]], float)
    g = trimesh.Trimesh(vertices=v, faces=[[0, 1, 2], [0, 2, 3]], process=False)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def EXTRUDE_XY(points, epaisseur, m):
    g = extrude_polygon(Polygon(points), epaisseur)
    g.apply_translation([0, 0, -epaisseur])
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def assembler(parts, nom):
    s = trimesh.Scene()
    for i, p in enumerate(parts): s.add_geometry(p, node_name=f"{nom}_{i}", geom_name=f"{nom}_{i}")
    return s

# ------------------------------------------------------------- positions
# même logique que la démo (posPlateforme, regieBox, podiumBox, camionBox, posStands, tracesCables…)
def positions(E):
    b, r, v, s, pd, c, el = E["bloc"], E["regie"], E["village"], E["sono"], E["podium"], E["camion"], E["electricite"]
    Z = E["projet"]["zonePublic"]
    pl = dict(x0=b["x"] - b["largeurPlateforme"] / 2, x1=b["x"] + b["largeurPlateforme"] / 2,
              z0=b["z"] - b["profondeurPlateforme"] / 2, z1=b["z"] + b["profondeurPlateforme"] / 2,
              h=b.get("plancher", b["hauteurVP"] - .5), hVP=b["hauteurVP"])
    devant = r.get("position", "devant") == "devant"
    zc = pl["z0"] - r["ecart"] - r["largeur"] / 2 if devant else pl["z1"] + r["ecart"] + r["largeur"] / 2
    y0 = r.get("surelevation", 0.0)
    rg = dict(x=b["x"], z=zc, L=r["longueur"], l=r["largeur"], h=r["hauteur"], y0=y0, y1=y0 + r["hauteur"],
              x0=b["x"] - r["longueur"] / 2, x1=b["x"] + r["longueur"] / 2, z0=zc - r["largeur"] / 2, z1=zc + r["largeur"] / 2)
    H = min(1.5, pd["hauteur"]); tz1 = rg["z0"] - pd["ecartRegie"]; tz0 = tz1 - pd["tete"]["profondeur"]
    pb = dict(H=H, x=b["x"], tete=dict(x0=b["x"] - pd["tete"]["largeur"] / 2, x1=b["x"] + pd["tete"]["largeur"] / 2, z0=tz0, z1=tz1),
              cat=dict(x0=b["x"] - pd["catwalk"]["largeur"] / 2, x1=b["x"] + pd["catwalk"]["largeur"] / 2, z0=tz0 - pd["catwalk"]["longueur"], z1=tz0))
    x0c = c["x"] - c["longueur"] / 2
    cam = dict(x0=x0c, x1=c["x"] + c["longueur"] / 2, xc0=x0c + c["cabine"], xh0=c["x"] + c["longueur"] / 2, xh1=c["x"] + c["longueur"] / 2 + c["hayon"],
               z0=c["z"] - c["largeur"] / 2, z1=c["z"] + c["largeur"] / 2, yp=c["plancher"], yt=c["plancher"] + c["hauteurCaisse"])
    stands = []
    n = len(v["stands"]); par_cote = math.ceil(n / 2)
    for i, st in enumerate(v["stands"]):
        if v.get("forme", "flancs") == "flancs":
            side = -1 if i < par_cote else 1; k = i if side < 0 else i - par_cote
            x = b["x"] + side * ((pl["x1"] - b["x"]) + v["ecartTour"] + v["cote"] / 2 + k * (v["cote"] + v["ecart"]))
            # un stand déplacé à la souris dans le visualiseur garde sa position propre (x, z, rot)
            stands.append(dict(nom=st["nom"], type=st["type"], x=st.get("x", x), z=st.get("z", v["z"]), rot=float(st.get("rot", 0.0))))
        else:
            rang, cote = i // 2, (1 if i % 2 else -1)
            z0 = max(rg["z1"], pl["z1"]) + v.get("ecartRegie", 1.5) + v["cote"] / 2
            stands.append(dict(nom=st["nom"], type=st["type"], x=b["x"] + cote * (v.get("allee", 4) / 2 + v["cote"] / 2), z=z0 + rang * v.get("pas", 3.6), rot=0.0))
    xmax = max(abs(x) for x in s["stacks"])
    stacks = [dict(nom=f"Subs_{'jardin' if x < 0 else 'cour'}_{'ext' if abs(x) == xmax else 'int'}", x=x, z=s["z"], ext=abs(x) == xmax) for x in s["stacks"]]
    delais = []
    for i in range(s["delais"]):
        o = (s.get("delaisPos") or [None] * s["delais"])[i] or {}
        delais.append(dict(nom=f"Delai_{'jardin' if i % 2 == 0 else 'cour'}", x=o.get("x", (1 if i % 2 else -1) * s["delaiX"]), z=o.get("z", s["delaiZ"]), cote=-1 if i % 2 == 0 else 1))
    vps = [dict(p, x=b["x"] + p["dx"], y=b["hauteurVP"], z=b["z"]) for p in E["projecteurs"]]
    lasers = [dict(l, x=b["x"] + l["dx"], y=b["hauteurVP"] + l["dy"], z=b["z"]) for l in E["lasers"]]
    scene_l = [dict(x=b["x"] + l["dx"], z=pb["tete"]["z0"] + l["dz"], h=l["h"]) for l in E["lumieres"].get("scene", [])]
    # passages de câbles : troncs jardin / cour, délais, régie → podium, TGBT → régie / tour, GE → TGBT
    zl, xs, zf = Z["z1"] + 2.2, Z["x1"] + 1.5, 1.6
    tg = el["armoires"][0]; cables = []
    for cc in (-1, 1):
        cables.append(dict(nom=f"Tronc_{'jardin' if cc < 0 else 'cour'}", type="tronc",
                           pts=[[rg["x"] + cc * rg["L"] / 2, zl], [cc * xs, zl], [cc * xs, zf], [cam["x0"] - 1.2 if cc < 0 else cam["xh1"] + .8, zf]]))
    for d in delais:
        cables.append(dict(nom="Cable_" + d["nom"], type="public", pts=[[d["cote"] * xs, d["z"]], [d["x"], d["z"]]]))
    cables.append(dict(nom="Cable_regie_podium", type="coulisses", pts=[[rg["x"], rg["z0"]], [rg["x"], pb["tete"]["z1"]]]))
    cables.append(dict(nom="Cable_TGBT_regie", type="tronc", pts=[[tg["x"], tg["z"]], [tg["x"], zl], [rg["x"] - rg["L"] / 2, zl]]))
    cables.append(dict(nom="Cable_TGBT_tour", type="tronc", pts=[[tg["x"], tg["z"]], [tg["x"], pl["z1"] + .3], [pl["x0"] + 3.07 + .06, pl["z1"] + .3]]))
    if el.get("groupe"):
        g = el["groupe"]; cables.append(dict(nom="Cable_GE_TGBT", type="tronc", pts=[[g["x"], g["z"]], [tg["x"], g["z"]], [tg["x"], tg["z"]]]))
    return dict(pl=pl, rg=rg, pb=pb, cam=cam, stands=stands, stacks=stacks, delais=delais, vps=vps, lasers=lasers, scene_l=scene_l, cables=cables)

def cadre_image(p):
    W = p["z"] / p["tr"]; H = W / p["ratio"]
    return dict(W=W, H=H, x0=p["cx"] - W / 2, x1=p["cx"] + W / 2, y0=p["cy"] - H / 2, y1=p["cy"] + H / 2)

# ------------------------------------------------------------- éléments (à l'origine, sol y = 0)
def elem_facade(F):
    parts = [EXTRUDE_XY(F["contour"], F["profondeur"], M["pierre"])]
    for i, (x0, x1, y0, y1) in enumerate(F["ouvertures"]):
        parts.append(B(x0, x1, y0, y1, -0.30, 0.02, M["sombre"] if i < 3 else M["vitrail"]))
    r = F["rosace"]
    disc = trimesh.creation.annulus(r_min=r["r"] * 0.72, r_max=r["r"], height=0.08, sections=48)
    disc.apply_translation([r["x"], r["y"], 0.03]); disc.visual = trimesh.visual.TextureVisuals(material=M["or"]); parts.append(disc)
    vit = cylinder(radius=r["r"] * 0.72, height=0.04, sections=48); vit.apply_translation([r["x"], r["y"], 0.03])
    vit.visual = trimesh.visual.TextureVisuals(material=M["vitrail"]); parts.append(vit)
    return parts

def elem_nef(n):
    L = n["z1"] - n["z0"]
    return [B(n["x0"], n["x1"], 0, n["h"], -L, 0, M["nef"]), B(n["x0"] - .5, n["x1"] + .5, n["h"], n["h"] + 1.5, -L, 0, M["toiture"])]

def elem_boite_sol(w, h, d, m):
    return [B(-w / 2, w / 2, 0, h, -d / 2, d / 2, m)]

def elem_tour_layher(b, pl):
    """Layher Allround : montants 2 m sur embases + vérins, moises à chaque niveau, diagonales alternées,
    planchers acier 0,32 (+ 0,19) au niveau haut, plancher à trappe + échelle par niveau, garde-corps,
    plinthes, toit bâché, lests béton. Origine au centre de l'emprise, sol à 0."""
    nx, n, hN, base, L = b["travees"], b["niveaux"], b["hauteurNiveau"], b["base"], b["profondeurPlateforme"]
    w, d = nx * L, L
    xs = [-w / 2 + i * L for i in range(nx + 1)]; zs = [-d / 2, d / 2]; ys = [base + k * hN for k in range(n + 1)]
    mg, md, mp, parts = M["galva"], M["deck"], M["echafaud"], []
    for x in xs:
        for z in zs:
            parts += [B(x - .08, x + .08, 0, .012, z - .08, z + .08, mg), CYL([x, 0, z], [x, base, z], .02, mg, 8), CYL([x, base - .05, z], [x, base + .1, z], .04, mg, 8)]
            for k in range(n): parts.append(CYL([x, ys[k], z], [x, ys[k + 1], z], .024, mg, 8))
            parts.append(CYL([x, ys[n], z], [x, ys[n] + 1.0, z], .024, mg, 8))
            y = base
            while y <= ys[n] + 1.0 + 1e-6:   # rosettes tous les 0,5 m
                ro = cylinder(radius=.055, height=.009, sections=8); ro.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])); ro.apply_translation([x, y, z])
                ro.visual = trimesh.visual.TextureVisuals(material=mg); parts.append(ro); y += .5
    for k, y in enumerate(ys):
        for z in zs:
            for i in range(nx): parts.append(CYL([xs[i], y, z], [xs[i + 1], y, z], .028 if k == n else .024, mg, 8))
        for x in xs: parts.append(CYL([x, y, zs[0]], [x, y, zs[1]], .024, mg, 8))
    for dy in (.5, 1.0):   # garde-corps
        y = ys[n] + dy
        for z in zs:
            for i in range(nx): parts.append(CYL([xs[i], y, z], [xs[i + 1], y, z], .024, mg, 8))
        for x in (xs[0], xs[nx]): parts.append(CYL([x, y, zs[0]], [x, y, zs[1]], .024, mg, 8))
    for z in zs: parts.append(B(-w / 2, w / 2, ys[n] + .06, ys[n] + .21, z - .02, z + .02, mp))   # plinthes
    for x in (-w / 2, w / 2): parts.append(B(x - .02, x + .02, ys[n] + .06, ys[n] + .21, -d / 2, d / 2, mp))
    for k in range(n):   # diagonales
        for zi, z in enumerate(zs):
            for i in range(nx):
                dd = 1 if (i + k + zi) % 2 else 0
                parts.append(CYL([xs[i + dd], ys[k], z], [xs[i + 1 - dd], ys[k + 1], z], .02, mg, 8))
        for xi, x in enumerate((xs[0], xs[nx])):
            dd = 1 if (k + xi) % 2 else 0
            parts.append(CYL([x, ys[k], zs[dd]], [x, ys[k + 1], zs[1 - dd]], .02, mg, 8))
    for i in range(nx):   # planchers acier 9 × 0,32 + 1 × 0,19
        x = xs[i] + .03
        for j in range(10):
            wd = .32 if j < 9 else .19
            parts.append(B(x, x + wd - .012, ys[n], ys[n] + .06, -d / 2 + .05, d / 2 - .05, md)); x += wd
    for k in range(1, n + 1):   # plancher à trappe + échelle, travée jardin
        y = ys[k]; x0 = xs[0] + .03
        if k < n: parts.append(B(x0, x0 + .61, y, y + .06, -d / 2 + .05, d / 2 - .05, md))
        lx, lz = x0 + .3, -d / 2 + .6
        parts += [CYL([lx - .2, y - hN + .1, lz], [lx - .2, y + .3, lz], .015, mg, 6), CYL([lx + .2, y - hN + .1, lz], [lx + .2, y + .3, lz], .015, mg, 6)]
        yy = y - hN + .3
        while yy < y + .2: parts.append(CYL([lx - .2, yy, lz], [lx + .2, yy, lz], .012, mg, 6)); yy += .3
    for x in (xs[0], xs[nx]):
        for z in zs: parts.append(CYL([x, ys[n] + 1.0, z], [x, ys[n] + 2.6, z], .024, mg, 8))
    parts.append(B(-w / 2 - .25, w / 2 + .25, ys[n] + 2.5, ys[n] + 2.6, -d / 2 - .25, d / 2 + .25, M["bache"]))
    for x in xs:
        for z in (-d / 2 - .95, d / 2 + .95): parts.append(B(x - .6, x + .6, 0, .6, z - .3, z + .3, M["beton"]))   # lests
    parts.append(CYL([xs[1] + .06, 0, d / 2 + .06], [xs[1] + .06, ys[n], d / 2 + .06], .045, M["cable"], 8))   # tronc vidéo / puissance
    return parts

def elem_regie(rg):
    L, l, h, y0 = rg["L"], rg["l"], rg["h"], rg["y0"]
    parts = []
    if y0 > 0:
        parts.append(B(-L / 2, L / 2, .08, y0, -l / 2, l / 2, M["jupe"]))
        x = -L / 2 + .3
        while x <= L / 2:
            for z in (-l / 2 + .3, l / 2 - .3): parts.append(CYL([x, 0, z], [x, y0, z], .035, M["inox"], 8))
            x += 1.0
        n, g, p, xe = 5, y0 / 5, 1.2 / 5, -L / 2 + .9
        for i in range(n):
            y1 = g * (n - i); z0 = l / 2 + i * p
            parts.append(B(xe - .6, xe + .6, y1 - .05, y1, z0, z0 + p, M["noir"]))
    parts += [B(-L / 2, L / 2, y0, y0 + h, -l / 2, l / 2, M["regie"]),
              PLAN_XY(-L / 2 + .4, -L / 2 + 1.4, y0, y0 + 2.2, l / 2 + .01, M["inox"]),       # porte côté tour
              PLAN_XY(-1.2, 2.0, y0 + 1.15, y0 + 2.05, -l / 2 - .01, M["vitrail"]),          # vitre côté façade
              B(L / 2 - 1.2, L / 2 - .2, y0 + h, y0 + h + .6, -.5, .5, M["inox"])]
    for x in (-L / 2, L / 2): parts.append(B(x - .15, x + .15, y0 - .1, y0 + .3, -.3, .3, M["noir"]))   # sorties de câbles
    return parts

def elem_podium(pb, pd):
    """tête + catwalk, origine au centre de la tête ; le catwalk part vers -z (la façade)."""
    H, Tw, Td, Cw, Cl = pb["H"], pd["tete"]["largeur"], pd["tete"]["profondeur"], pd["catwalk"]["largeur"], pd["catwalk"]["longueur"]
    T = dict(x0=-Tw / 2, x1=Tw / 2, z0=-Td / 2, z1=Td / 2); C = dict(x0=-Cw / 2, x1=Cw / 2, z0=-Td / 2 - Cl, z1=-Td / 2)
    mi, parts = M["inox"], []
    for bx in (T, C):
        parts += [B(bx["x0"], bx["x1"], H - .12, H, bx["z0"], bx["z1"], M["bois"]), B(bx["x0"] + .08, bx["x1"] - .08, 0, H - .12, bx["z0"] + .08, bx["z1"] - .08, M["jupe"])]
    x = T["x0"] + .3
    while x <= T["x1"] - .29:
        for z in (T["z0"] + .3, T["z1"] - .3): parts.append(CYL([x, 0, z], [x, H - .12, z], .035, mi, 8))
        x += 1.0
    z = C["z0"] + .3
    while z <= C["z1"]:
        for x in (C["x0"] + .25, C["x1"] - .25): parts.append(CYL([x, 0, z], [x, H - .12, z], .035, mi, 8))
        z += 1.0
    for (x0, z0, x1, z1) in [(T["x0"] + 1.4, T["z1"], T["x1"] - 1.4, T["z1"]), (T["x0"], T["z0"], T["x0"], T["z1"] - 1.5), (T["x1"], T["z0"], T["x1"], T["z1"] - 1.5)]:
        for hh in (H + .5, H + 1.1): parts.append(CYL([x0, hh, z0], [x1, hh, z1], .025, mi, 8))
        nn = max(1, round(math.hypot(x1 - x0, z1 - z0) / 1.5))
        for i in range(nn + 1):
            x, z = x0 + (x1 - x0) * i / nn, z0 + (z1 - z0) * i / nn; parts.append(CYL([x, H, z], [x, H + 1.1, z], .025, mi, 8))
    for (x0, x1, z0, z1) in [(C["x0"] - .02, C["x0"] + .03, C["z0"], C["z1"]), (C["x1"] - .03, C["x1"] + .02, C["z0"], C["z1"]), (C["x0"], C["x1"], C["z0"] - .02, C["z0"] + .03),
                             (T["x0"], C["x0"], T["z0"] - .02, T["z0"] + .03), (C["x1"], T["x1"], T["z0"] - .02, T["z0"] + .03)]:
        parts.append(B(x0, x1, H, H + .1, z0, z1, M["led"]))
    nM, gm, pm, zs0, zs1 = 8, H / 8, .28, T["z1"] - 1.4, T["z1"] - .2   # escaliers latéraux
    for side in (-1, 1):
        xe = T["x0"] if side < 0 else T["x1"]
        for i in range(nM):
            y1 = gm * (nM - i); xa, xb = xe + side * i * pm, xe + side * (i + 1) * pm
            parts += [B(min(xa, xb), max(xa, xb), y1 - .05, y1, zs0, zs1, M["noir"]), B(min(xa, xb), min(xa, xb) + .05, y1 - .005, y1 + .012, zs0, zs1, M["jaune"])]
        xb = xe + side * nM * pm
        for z in (zs0, zs1):
            parts += [CYL([xe, H, z], [xb, gm, z], .025, mi, 8), CYL([xe, H + .95, z], [xb, gm + .95, z], .028, mi, 8), CYL([xb, 0, z], [xb, gm + .95, z], .028, mi, 8), CYL([xe, H, z], [xe, H + 1.1, z], .028, mi, 8)]
    parts += [B(-2.4, -.8, H, H + .9, T["z1"] - 1.5, T["z1"] - .9, M["noir"]), B(.4, 1.9, H + .75, H + .85, T["z1"] - 1.3, T["z1"] - .95, M["noir"])]   # backline
    for dx in (-1.6, 1.6): parts.append(B(dx - .3, dx + .3, H, H + .35, T["z0"] + .1, T["z0"] + .5, M["noir"]))   # retours
    parts += [CYL([0, H, T["z0"] + 1.2], [0, H + 1.5, T["z0"] + 1.2], .015, M["noir"], 6)]
    for side in (-1, 1):   # jupes imprimées (texte dans Unreal : M_Jupe à remplacer par une texture)
        parts.append(PLAN_YZ(C["x0"] - .01 if side < 0 else C["x1"] + .01, .1, H - .15, C["z0"] + .2, C["z1"] - .2, M["jaune"]))
    return parts

def elem_camion(cam, c):
    """cam n'est plus utilisé (tout vient de c)."""
    """origine au centre du véhicule (x = c.x, z = c.z) ; cabine côté -x, hayon déployé côté +x."""
    L = c["longueur"]; x0, x1 = -L / 2, L / 2; xc0 = x0 + c["cabine"]; xh1 = x1 + c["hayon"]; z0, z1 = -c["largeur"] / 2, c["largeur"] / 2; yp, yt = c["plancher"], c["plancher"] + c["hauteurCaisse"]
    mb, mn, mi, parts = M["blanc"], M["noir"], M["inox"], []
    parts += [B(x0 + .1, xc0 - .05, .4, 2.6, z0 + .05, z1 - .05, mb), PLAN_YZ(x0 + .09, 1.4, 2.4, -.95, .95, M["vitrail"]),
              B(x0, x1, .5, yp, z0 + .1, z1 - .1, mn), B(xc0, x1, yp, yt, z0, z1, mb)]
    for x in (x0 + 1.0, x1 - 1.2):
        for z in (z0 + .15, z1 - .15):
            r = cylinder(radius=.5, height=.3, sections=16); r.apply_translation([x, .5, z]); r.visual = trimesh.visual.TextureVisuals(material=mn); parts.append(r)
    parts.append(B(x1, xh1, yp - .08, yp, z0, z1, M["deck"]))   # hayon
    for z in (z0 + .2, z1 - .2): parts.append(CYL([xh1 - .1, 0, z], [xh1 - .1, yp - .08, z], .03, mi, 8))
    for (ax, az, bx, bz) in [(x1, z0, xh1, z0), (xh1, z0, xh1, z1)]:
        for hh in (.5, 1.0): parts.append(CYL([ax, yp + hh, az], [bx, yp + hh, bz], .02, mi, 8))
        parts += [CYL([bx, yp, bz], [bx, yp + 1.0, bz], .022, mi, 8), CYL([ax, yp, az], [ax, yp + 1.0, az], .022, mi, 8)]
    xd = (x1 + xh1) / 2
    parts += [B(xd - .65, xd + .65, yp, yp + .9, z1 - .65, z1 - .15, mn), B(xd - .5, xd + .5, yp + .9, yp + .98, z1 - .6, z1 - .2, M["projo"])]
    for x in (x1 - .6, xh1 + .6):
        parts += [CYL([x, 0, z1 + .4], [x, 1.1, z1 + .4], .03, mi, 8), B(x - .2, x + .2, 1.1, 1.45, z1 + .2, z1 + .6, mn)]   # retours DJ
    if c.get("ecran", True):
        parts += [B(xc0 + .05, x1 - .05, yp + .05, yt - .05, z1, z1 + .015, mn), PLAN_XY(xc0 + .1, x1 - .1, yp + .1, yt - .1, z1 + .02, M["ecran"])]
    return parts

def elem_tonnelle(c, couleur):
    h0, h1 = 2.2, 3.0
    mt = mat("M_Tente", couleur, rough=0.9)
    parts = [CYL([x, 0, z], [x, h0, z], .035, M["inox"], 8) for x in (-c / 2, c / 2) for z in (-c / 2, c / 2)]
    parts.append(PYRAMIDE_CONE([0, h1, 0], [0, h0, 0], c * math.sqrt(.5) * 1.02, mt))
    parts[-1].apply_transform(trimesh.transformations.rotation_matrix(math.pi / 4, [0, 1, 0]))
    parts.append(B(-c / 2 + .2, c / 2 - .2, 0, .95, -c / 2 + .1, -c / 2 + .7, M["comptoir"]))   # comptoir côté -z : vers la façade
    for x in (-c / 2, c / 2):
        for z in (-c / 2, c / 2): parts.append(B(x - .2, x + .2, 0, .18, z - .2, z + .2, M["noir"]))   # lests
    return parts

def elem_tonnelle_plate(w, d, couleur):
    mt = mat("M_TenteRepos", couleur, rough=0.9)
    parts = [CYL([x, 0, z], [x, 2.2, z], .035, M["inox"], 8) for x in (-w / 2, w / 2) for z in (-d / 2, d / 2)]
    parts.append(B(-w / 2 - .1, w / 2 + .1, 2.27, 2.33, -d / 2 - .1, d / 2 + .1, mt)); return parts

def elem_repos(r):
    parts = elem_tonnelle_plate(r["tonnelle"]["largeur"], r["tonnelle"]["profondeur"], (0.85, 0.82, 0.77))
    for i in range(4): parts.append(B(-2.4 + i * 1.4, -1.2 + i * 1.4, .42, .48, -.9 + (i % 2) * 1.6, -.6 + (i % 2) * 1.6, M["bois"]))
    parts.append(B(-.6, .6, 0, .75, .3, .9, M["comptoir"])); return parts

def elem_stockage(r):
    parts = elem_tonnelle_plate(r["stockage"]["largeur"], r["stockage"]["profondeur"], (0.73, 0.75, 0.78))
    for i in range(6): parts.append(B(-1.2 + (i % 3) * .8, -.6 + (i % 3) * .8, 0, .9 + (i // 3) * .3, -1 + (i // 3) * 1.1, -.4 + (i // 3) * 1.1, M["noir"]))
    return parts

def elem_bache(r):
    b = r["bache"]; parts = [B(-b["demiLargeur"], b["demiLargeur"], 0, b["hauteur"], -.02, .02, M["bacheOp"])]
    x = -b["demiLargeur"]
    while x <= b["demiLargeur"] + 1e-6: parts.append(CYL([x, 0, 0], [x, b["hauteur"] + .1, 0], .03, M["inox"], 8)); x += 3.5
    return parts

def elem_sub_stack(s):
    sb = s["sub"]; parts = []
    for k in range(s["subsParStack"]): parts.append(B(-sb["l"] / 2, sb["l"] / 2, k * sb["h"], (k + 1) * sb["h"] - .03, -sb["p"] / 2, sb["p"] / 2, M["noir"]))
    return parts

def elem_tetes(n, demi_l, hT, prof):
    parts = []
    for k in range(n):
        g = B(-demi_l, demi_l, k * hT, (k + 1) * hT - .02, -prof / 2 + .1, prof / 2 - .05, M["noir"])
        g.apply_transform(trimesh.transformations.rotation_matrix(-k * .05, [1, 0, 0])); parts.append(g)
    return parts

def elem_delai_tour(h, n_tetes):
    parts = [CYL([dx, 0, dz], [dx * .3, h - 1, dz * .3], .025, M["inox"], 8) for dx in (-.5, .5) for dz in (-.5, .5)]
    parts += [CYL([0, 0, 0], [0, h - .9, 0], .05, M["inox"], 8), B(-.7, .7, 0, .15, -.7, .7, M["noir"])]
    for k in range(n_tetes): parts.append(B(-.5, .5, h - .9 + k * .36, h - .9 + (k + 1) * .36 - .02, -.3, .3, M["noir"]))
    return parts

def elem_totem(h):
    parts = [B(-.5, .5, 0, .25, -.5, .5, M["projo"]), CYL([0, 0, 0], [0, h, 0], .06, M["projo"], 8),
             B(-.5, .5, h - .3, h - .15, -.1, .1, M["noir"]), B(-.5, .5, h - .1, h + .05, -.1, .1, M["noir"])]   # 2 barres Mode B
    for dx in (-.35, .35): parts.append(CYL([dx, h + .1, 0], [dx, h + .35, -.15], .12, M["noir"], 10))          # 2 PAR 64
    return parts

def elem_wash(): return [B(-.45, .45, 0, .5, -.35, .35, M["noir"])]
def elem_proj_scene(h): return [CYL([0, 0, 0], [0, h, 0], .04, M["projo"], 8), B(-.15, .15, h - .2, h + .1, -.15, .15, M["noir"])]
def elem_projecteur(): return [B(-.3, .3, -.21, .21, -.35, .35, M["projo"]), CYL([0, 0, .35], [0, 0, .47], .14, M["noir"])]
def elem_laser(): return [B(-.2, .2, -.12, .12, -.2, .2, M["noir"])]
def elem_armoire(a): return [B(-a["l"] / 2, a["l"] / 2, 0, a["h"], -a["p"] / 2, a["p"] / 2, M["armoire"]), B(-a["l"] / 2 + .1, a["l"] / 2 - .1, a["h"] * .55, a["h"] * .75, -a["p"] / 2 - .01, -a["p"] / 2 + .01, M["jaune"])]
def elem_groupe(g): return [B(-g["l"] / 2, g["l"] / 2, 0, g["h"], -g["p"] / 2, g["p"] / 2, M["armoire"]), CYL([g["l"] / 2 - .3, g["h"], 0], [g["l"] / 2 - .3, g["h"] + .6, 0], .08, M["noir"], 8)]

def elem_cables(cables):
    """passages de câbles en coordonnées monde : segment plat + bandes jaunes."""
    parts, total = [], 0.0
    for c in cables:
        w, h = (.9, .09) if c["type"] == "public" else (.5, .07)
        for i in range(len(c["pts"]) - 1):
            (x0, z0), (x1, z1) = c["pts"][i], c["pts"][i + 1]; L = math.hypot(x1 - x0, z1 - z0); total += L
            if L < .05: continue
            ang = -math.atan2(z1 - z0, x1 - x0)
            seg = B(-L / 2, L / 2, 0, h, -w / 2, w / 2, M["cable"]); seg.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 1, 0])); seg.apply_translation([(x0 + x1) / 2, 0, (z0 + z1) / 2]); parts.append(seg)
            pas = 2.0 if c["type"] == "tronc" else 1.0; dd = pas / 2
            while dd < L:
                u = dd / L; ray = B(-.06, .06, h, h + .012, -w / 2, w / 2, M["jaune"]); ray.apply_transform(trimesh.transformations.rotation_matrix(ang, [0, 1, 0]))
                ray.apply_translation([x0 + (x1 - x0) * u, 0, z0 + (z1 - z0) * u]); parts.append(ray); dd += pas
    return parts, total

# ------------------------------------------------------------- export
def ecrire_element(nom, parts):
    os.makedirs(D_ELEM, exist_ok=True)
    sc = assembler(parts, nom)
    sc.export(os.path.join(D_ELEM, f"{nom}.glb"))
    fus = trimesh.util.concatenate(parts)
    fus.export(os.path.join(D_ELEM, f"{nom}.obj"))
    return sc

def T(x, y, z, rot_y=0.0):
    m = trimesh.transformations.rotation_matrix(rot_y, [0, 1, 0])
    m[:3, 3] = [x, y, z]; return m

def look_at_y(src, dst):
    dx, dz = dst[0] - src[0], dst[2] - src[2]
    return math.atan2(dx, dz)

def injecter_lumieres_glb(chemin, lumieres):
    """Ajoute des spots KHR_lights_punctual au GLB (candela, cône, orientation)."""
    import struct
    d = open(chemin, "rb").read()
    assert d[:4] == b"glTF"
    ln = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + ln].decode("utf-8"))
    off = 20 + ln
    bin_len, bin_type = struct.unpack("<II", d[off:off + 8]); bin_chunk = d[off + 8:off + 8 + bin_len]
    j.setdefault("extensionsUsed", []).append("KHR_lights_punctual")
    lights = []
    for lm in lumieres:
        cd = lm["lumens"] / (2 * math.pi * (1 - math.cos(lm["angle"] / 2)))
        lights.append(dict(name=lm["nom"], type="spot", color=lm["couleur"], intensity=round(cd, 1),
                           spot=dict(innerConeAngle=round(lm["angle"] * .4, 4), outerConeAngle=round(lm["angle"] / 2, 4))))
        d_ = np.array(lm["cible"], float) - np.array(lm["pos"], float); d_ /= np.linalg.norm(d_)
        R = trimesh.geometry.align_vectors([0, 0, -1], d_)
        q = trimesh.transformations.quaternion_from_matrix(R)
        j["nodes"].append(dict(name=lm["nom"], translation=[float(v) for v in lm["pos"]],
                               rotation=[float(q[1]), float(q[2]), float(q[3]), float(q[0])],
                               extensions={"KHR_lights_punctual": {"light": len(lights) - 1}}))
        j["scenes"][0]["nodes"].append(len(j["nodes"]) - 1)
    j.setdefault("extensions", {})["KHR_lights_punctual"] = {"lights": lights}
    js = json.dumps(j, separators=(",", ":")).encode("utf-8"); js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + bin_len
    with open(chemin, "wb") as f:
        f.write(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                + struct.pack("<II", bin_len, bin_type) + bin_chunk)

def main_v3(E):
    """schéma v3 (outils/studio-implantation.html) : une liste d'objets libres, chacun avec x, z, rot et ses paramètres."""
    P = E["projet"]; F = P["facade"]; Z = E["zone"]
    if os.path.isdir(D_ELEM):
        for f in os.listdir(D_ELEM):
            if f.startswith("SM_"): os.remove(os.path.join(D_ELEM, f))
    os.makedirs(D_SCENE, exist_ok=True); os.makedirs(D_ELEM, exist_ok=True)
    scene = trimesh.Scene(); placement = []; lumieres = []
    def poser(nom_elem, parts, inst):
        ecrire_element(nom_elem, parts); fus = trimesh.util.concatenate([p.copy() for p in parts])
        scene.add_geometry(fus, node_name=inst["nom"], geom_name=nom_elem, transform=T(inst["x"], inst.get("y", 0), inst["z"], inst.get("rot", 0.0)))
        placement.append(dict(acteur=inst["nom"], element=nom_elem, location_cm=[inst["z"]*100, inst["x"]*100, inst.get("y", 0)*100], yaw_deg=round(math.degrees(inst.get("rot", 0.0)), 2)))
    poser("SM_Facade", elem_facade(F), dict(nom="Facade", x=0, z=0))
    poser("SM_Nef", elem_nef(P["nef"]), dict(nom="Nef", x=0, z=P["nef"]["z1"]))
    for i, v in enumerate(P["voisins"]): poser(f"SM_Voisin_{i+1}", elem_boite_sol(v["x1"]-v["x0"], v["h"], v["z1"]-v["z0"], M["voisin"]), dict(nom=f"Voisin_{i+1}", x=(v["x0"]+v["x1"])/2, z=(v["z0"]+v["z1"])/2))
    poser("SM_Sol", [PLAN_XZ(-120, 120, -40, 160, 0, M["pave"])], dict(nom="Sol", x=0, z=0))
    poser("SM_ZonePublic", [PLAN_XZ(Z["x0"], Z["x1"], Z["z0"], Z["z1"], 0.03, M["zone"])], dict(nom="ZonePublic", x=0, z=0))
    for o in E["objets"]:
        t, nom = o["type"], "Obj_" + re.sub(r"[^A-Za-z0-9]+", "_", o["nom"]).strip("_") + f"_{o['id']}"
        inst = dict(nom=nom, x=o["x"], z=o["z"], rot=float(o.get("rot", 0)))
        if t == "camion":
            c = dict(longueur=7.3, largeur=2.2, cabine=2.35, plancher=.95, hauteurCaisse=2.2, hayon=o.get("hayon", 1.6), ecran=bool(o.get("ecran", 1)))
            poser(f"SM_Camion_{o['id']}", elem_camion(None, c), inst)
        elif t == "podium":
            l, p, H = o["nx"]*1.0, o["nz"]*2.0, o["hauteur"]; parts = [B(-l/2, l/2, H-.08, H, -p/2, p/2, M["bois"]), B(-l/2+.05, l/2-.05, 0, H-.08, -p/2+.05, p/2-.05, M["jupe"])]
            if o.get("gardecorps"):
                for (x0, z0, x1, z1) in [(-l/2, p/2, l/2, p/2), (-l/2, -p/2, -l/2, p/2), (l/2, -p/2, l/2, p/2)]:
                    for hh in (H+.5, H+1.1): parts.append(CYL([x0, hh, z0], [x1, hh, z1], .02, M["inox"], 8))
            poser(f"SM_Podium_{o['id']}", parts, inst)
        elif t == "pile_subs":
            parts = [B(-.3, .3, k*.7, (k+1)*.7-.03, -.37, .37, M["noir"]) for k in range(o["subs"])] + elem_tetes(o["tetes"], .45, .35, .75)
            for g in parts[o["subs"]:]: g.apply_translation([0, o["subs"]*.7, 0])
            poser(f"SM_PileSubs_{o['id']}", parts, inst)
        elif t == "vp":
            p2 = dict(o, x=o["x"], y=o["altitude"], z=o["z"], ratio=16/9); im = cadre_image(p2)
            poser("SM_Projecteur", elem_projecteur(), dict(nom=nom, x=o["x"], y=o["altitude"], z=o["z"], rot=look_at_y([o["x"], o["altitude"], o["z"]], [o["cx"], o["cy"], 0]) + math.pi))
            coins = [[im["x0"], im["y0"], 0], [im["x1"], im["y0"], 0], [im["x1"], im["y1"], 0], [im["x0"], im["y1"], 0]]
            poser(f"SM_ConeVP_{o['id']}", [FRUSTUM_VP([o["x"], o["altitude"], o["z"]], coins, M["cone"]), PLAN_XY(im["x0"], im["x1"], im["y0"], im["y1"], .06, mat("M_ImageVP", (1, .71, .33), alpha=.25))], dict(nom=f"ConeVP_{o['id']}", x=0, z=0))
            lumieres.append(dict(nom=f"Light_VP_{o['id']}", pos=[o["x"], o["altitude"], o["z"]], cible=[o["cx"], o["cy"], 0], lumens=o.get("lumens", {"x10000":7500,"hdt1000":10000,"pu2220b":20000,"l1500uh":12000,"l1755u":15000}.get(o.get("modele"), 10000)), angle=2*math.atan((im["W"]/2)/o["z"]), couleur=[1, .94, .86]))
        elif t == "laser":
            poser("SM_Laser", elem_laser(), dict(nom=nom, x=o["x"], y=o["altitude"], z=o["z"]))
            poser(f"SM_FaisceauLaser_{o['id']}", [CYL([o["x"], o["altitude"], o["z"]], [o["tx"], o["ty"], 0], .05, M["laser"])], dict(nom=f"FaisceauLaser_{o['id']}", x=0, z=0))
        elif t == "tonnelle": poser(f"SM_Tonnelle_{o.get('usage', 'asso')}", elem_tonnelle(3.0, TENTE.get(o.get("usage"), TENTE["asso"])), inst)
        elif t == "totem":
            poser("SM_Totem", elem_totem(o["h"]), inst)
            lumieres.append(dict(nom=f"Light_Totem_{o['id']}", pos=[o["x"], o["h"], o["z"]], cible=[o["x"] - 14*math.sin(o.get("rot", 0)), 0, o["z"] - 14*math.cos(o.get("rot", 0))], lumens=20000, angle=math.radians(60), couleur=[.75, .55, 1]))
        elif t == "wash":
            poser("SM_WashFacade", elem_wash(), inst)
            lumieres.append(dict(nom=f"Light_Wash_{o['id']}", pos=[o["x"], .5, o["z"]], cible=[o["tx"], o["ty"], 0], lumens=15000, angle=math.radians(30), couleur=[.75, .55, 1]))
        elif t == "regie": poser(f"SM_Regie_{o['id']}", elem_regie(dict(L=6.06, l=2.44, h=2.59, y0=o.get("surel", 0))), inst)
        elif t == "tour":
            b = dict(travees=o["travees"], niveaux=max(1, int(round((o["plancher"]-.3)/2))), hauteurNiveau=2.0, base=.3, profondeurPlateforme=3.07)
            poser(f"SM_TourLayher_{o['id']}", elem_tour_layher(b, dict(hVP=o["plancher"]+.5)), inst)
        elif t == "delai": poser("SM_DelaiTour", elem_delai_tour(o["h"], o["tetes"]), inst)
        elif t == "armoire": poser("SM_Armoire", elem_armoire(dict(l=1.2, h=1.8, p=.6)), inst)
        elif t == "ge": poser("SM_GroupeElectrogene", elem_groupe(dict(l=3.2, h=2.2, p=1.5)), inst)
        elif t == "barnum": poser("SM_Barnum", elem_tonnelle_plate(6, 3, (.85, .82, .77)), inst)
        elif t == "balise": poser("SM_Balise", [B(-.25, .25, 0, 1.8, -.25, .25, M["jaune"])], inst)
    out = os.path.join(D_SCENE, "Implantation.glb"); scene.export(out); injecter_lumieres_glb(out, lumieres)
    json.dump(dict(unites="cm", repere="Unreal : X avant (= recul Z du modèle), Y droite (= X modèle), Z haut (= Y modèle)", version=3, acteurs=placement,
                   lumieres=[dict(nom=l["nom"], location_cm=[l["pos"][2]*100, l["pos"][0]*100, l["pos"][1]*100], cible_cm=[l["cible"][2]*100, l["cible"][0]*100, l["cible"][1]*100], lumens=l["lumens"], cone_deg=round(math.degrees(l["angle"]), 1)) for l in lumieres]),
              open(os.path.join(PROJ, "Content", "Import", "placement.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"scène v3 : {out} ({len(placement)} acteurs, {len(lumieres)} lumières)")

def main():
    E = json.load(open(SRC, encoding="utf-8"))
    if E.get("version", 1) == 3: return main_v3(E)
    if E.get("version", 1) < 2: sys.exit("implantation.json version 1 : exporte à nouveau depuis la démo ou le visualiseur (schéma v2 : podium, camion, repos, electricite)")
    P = E["projet"]; pos = positions(E)
    # on repart d'un dossier d'éléments propre : les SM_ de l'ancien schéma ne doivent pas traîner
    if os.path.isdir(D_ELEM):
        for f in os.listdir(D_ELEM):
            if f.startswith("SM_"): os.remove(os.path.join(D_ELEM, f))
    os.makedirs(D_SCENE, exist_ok=True); os.makedirs(D_ELEM, exist_ok=True)
    scene = trimesh.Scene()
    placement = []

    def poser(nom_elem, parts, instances):
        ecrire_element(nom_elem, parts)
        fus = trimesh.util.concatenate([p.copy() for p in parts])
        for inst in instances:
            n = inst["nom"]
            scene.add_geometry(fus, node_name=n, geom_name=nom_elem, transform=T(inst["x"], inst.get("y", 0), inst["z"], inst.get("rot", 0.0)))
            placement.append(dict(acteur=n, element=nom_elem,
                                  location_cm=[inst["z"] * 100, inst["x"] * 100, inst.get("y", 0) * 100],
                                  yaw_deg=round(math.degrees(inst.get("rot", 0.0)), 2)))

    F = P["facade"]; Z = P["zonePublic"]; b = E["bloc"]
    poser("SM_Facade", elem_facade(F), [dict(nom="Facade", x=0, z=0)])
    poser("SM_Nef", elem_nef(P["nef"]), [dict(nom="Nef", x=0, z=P["nef"]["z1"])])
    for i, v in enumerate(P["voisins"]):
        poser(f"SM_Voisin_{i+1}", elem_boite_sol(v["x1"] - v["x0"], v["h"], v["z1"] - v["z0"], M["voisin"]),
              [dict(nom=f"Voisin_{i+1}_{v['nom']}".replace(" ", "_"), x=(v["x0"] + v["x1"]) / 2, z=(v["z0"] + v["z1"]) / 2)])
    poser("SM_Sol", [PLAN_XZ(-120, 120, -40, 160, 0, M["pave"])], [dict(nom="Sol", x=0, z=0)])
    poser("SM_ZonePublic", [PLAN_XZ(Z["x0"], Z["x1"], Z["z0"], Z["z1"], 0.03, M["zone"])], [dict(nom="ZonePublic", x=0, z=0)])

    pl, rg, pb, cam = pos["pl"], pos["rg"], pos["pb"], pos["cam"]
    poser("SM_TourLayher", elem_tour_layher(b, pl), [dict(nom="TourLayher_VP", x=b["x"], z=b["z"])])
    poser("SM_Regie", elem_regie(rg), [dict(nom="Regie_etanche", x=rg["x"], z=rg["z"])])
    poser("SM_Podium", elem_podium(pb, E["podium"]), [dict(nom="Podium_catwalk", x=pb["x"], z=(pb["tete"]["z0"] + pb["tete"]["z1"]) / 2)])
    poser("SM_Camion", elem_camion(cam, E["camion"]), [dict(nom="Camion_20m3_DJ", x=E["camion"]["x"], z=E["camion"]["z"])])

    par_type = {}
    for st in pos["stands"]: par_type.setdefault(st["type"], []).append(st)
    for typ, lst in par_type.items():
        poser(f"SM_Tonnelle_{typ}", elem_tonnelle(E["village"]["cote"], TENTE[typ]),
              [dict(nom="Stand_" + st["nom"].replace(" ", "_").replace("·", "-"), x=st["x"], z=st["z"], rot=st["rot"]) for st in lst])
    r = E["repos"]
    poser("SM_Repos", elem_repos(r), [dict(nom="Repos_equipe", x=r["x"], z=r["z"])])
    poser("SM_Stockage", elem_stockage(r), [dict(nom="Stockage", x=r["stockage"]["x"], z=r["stockage"]["z"])])
    poser("SM_BacheRepos", elem_bache(r), [dict(nom="Bache_opaque_repos", x=0, z=r["bache"]["z"])])

    s = E["sono"]; sb = s["sub"]; top = s["subsParStack"] * sb["h"]
    poser("SM_SubStack", elem_sub_stack(s), [dict(nom=st["nom"], x=st["x"], z=st["z"]) for st in pos["stacks"]])
    poser("SM_TetesPA", elem_tetes(s["tetes"]["parStackExterieur"], .5, .35, sb["p"]), [dict(nom=st["nom"].replace("Subs", "PA_tetes"), x=st["x"], y=top, z=st["z"]) for st in pos["stacks"] if st["ext"]])
    poser("SM_FrontFill", elem_tetes(s["tetes"]["frontFill"], .3, .4, sb["p"]), [dict(nom=st["nom"].replace("Subs", "FrontFill"), x=st["x"], y=top, z=st["z"]) for st in pos["stacks"] if not st["ext"]])
    if pos["delais"]:
        poser("SM_DelaiTour", elem_delai_tour(s["delaiH"], s["delaiTetes"]), [dict(nom=d["nom"], x=d["x"], z=d["z"]) for d in pos["delais"]])
    secteurs = []
    for st in [q for q in pos["stacks"] if q["ext"]]:
        cote = -1 if st["x"] < 0 else 1
        ang, az = math.radians(s["ouverture"] / 2), math.radians(-cote * s["visee"])
        pts = [[0, 0]] + [[math.sin(a + az) * s["portee"], math.cos(a + az) * s["portee"]] for a in np.linspace(-ang, ang, 25)]
        v = np.array([[st["x"] + q[0], 0.04, st["z"] + q[1]] for q in pts]); f = [[0, i, i + 1] for i in range(1, len(pts) - 1)]
        g = trimesh.Trimesh(vertices=v, faces=f, process=False); g.visual = trimesh.visual.TextureVisuals(material=M["sono"]); secteurs.append(g)
    poser("SM_Sono_Couverture", secteurs, [dict(nom="Sono_Couverture", x=0, z=0)])

    L = E["lumieres"]
    poser("SM_Totem", elem_totem(L["totems"][0]["h"]), [dict(nom=f"Totem_{i+1}", x=t["x"], z=t["z"]) for i, t in enumerate(L["totems"])])
    poser("SM_WashFacade", elem_wash(), [dict(nom=f"Wash_{i+1}", x=w["x"], z=w["z"]) for i, w in enumerate(L["wash"])])
    if pos["scene_l"]:
        poser("SM_ProjScene", elem_proj_scene(pos["scene_l"][0]["h"]), [dict(nom=f"ProjScene_{i+1}", x=l["x"], z=l["z"]) for i, l in enumerate(pos["scene_l"])])

    el = E["electricite"]
    for i, a in enumerate(el["armoires"]):
        poser(f"SM_Armoire_{i+1}", elem_armoire(a), [dict(nom="Armoire_" + a["nom"].split(" ")[0] + f"_{i+1}", x=a["x"], z=a["z"])])
    if el.get("groupe"):
        poser("SM_GroupeElectrogene", elem_groupe(el["groupe"]), [dict(nom="GE_100kVA_option", x=el["groupe"]["x"], z=el["groupe"]["z"])])
    cab, longueur = elem_cables(pos["cables"])
    poser("SM_Cables", cab, [dict(nom="Cables_passages", x=0, z=0)])

    for i, p in enumerate(pos["vps"]):
        poser("SM_Projecteur", elem_projecteur(), [dict(nom="VP_" + str(i + 1), x=p["x"], y=p["y"], z=p["z"], rot=look_at_y([p["x"], p["y"], p["z"]], [p["cx"], p["cy"], 0]) + math.pi)])
        im = cadre_image(p)
        coins = [[im["x0"], im["y0"], 0], [im["x1"], im["y0"], 0], [im["x1"], im["y1"], 0], [im["x0"], im["y1"], 0]]
        poser(f"SM_ConeVP_{i+1}", [FRUSTUM_VP([p["x"], p["y"], p["z"]], coins, M["cone"]),
                                   PLAN_XY(im["x0"], im["x1"], im["y0"], im["y1"], 0.06, mat("M_ImageVP", (1, .71, .33), alpha=.25))],
              [dict(nom=f"ConeVP_{i+1}", x=0, z=0)])
    for i, l in enumerate(pos["lasers"]):
        poser("SM_Laser", elem_laser(), [dict(nom=f"Laser_{i+1}", x=l["x"], y=l["y"], z=l["z"])])
        poser(f"SM_FaisceauLaser_{i+1}", [CYL([l["x"], l["y"], l["z"]], [l["tx"], l["ty"], 0], .05, M["laser"])], [dict(nom=f"FaisceauLaser_{i+1}", x=0, z=0)])
    cx, cz = (Z["x0"] + Z["x1"]) / 2, (Z["z0"] + Z["z1"]) / 2
    for i, t in enumerate(L["totems"]):
        d = np.array([cx - t["x"], -t["h"], cz - t["z"]]); d = d / np.linalg.norm(d) * min(26, np.linalg.norm([cx - t["x"], t["h"], cz - t["z"]]))
        base = [t["x"] + d[0], max(.1, t["h"] + d[1]), t["z"] + d[2]]
        poser(f"SM_FaisceauTotem_{i+1}", [CONE([t["x"], t["h"] - .2, t["z"]], base, 7, M["lum"])], [dict(nom=f"FaisceauTotem_{i+1}", x=0, z=0)])
    for i, w in enumerate(L["wash"]):
        poser(f"SM_FaisceauWash_{i+1}", [CONE([w["x"], .5, w["z"]], [w["tx"], w["ty"], 0], 4.5, M["lum"])], [dict(nom=f"FaisceauWash_{i+1}", x=0, z=0)])
    for i, l in enumerate(pos["scene_l"]):
        poser(f"SM_FaisceauScene_{i+1}", [CONE([l["x"], l["h"] - .1, l["z"]], [pb["x"], pb["H"] + .8, pb["tete"]["z0"] - 2], 2.6, M["lum"])], [dict(nom=f"FaisceauScene_{i+1}", x=0, z=0)])

    # lumières réelles (KHR_lights_punctual)
    lumieres = []
    for i, p in enumerate(pos["vps"]):
        im = cadre_image(p); demi = math.atan((im["W"] / 2) / p["z"])
        lumieres.append(dict(nom=f"Light_VP_{i+1}", pos=[p["x"], p["y"], p["z"]], cible=[p["cx"], p["cy"], 0], lumens=p["lumens"], angle=demi * 2, couleur=[1.0, 0.94, 0.86]))
    for i, t in enumerate(L["totems"]):
        lumieres.append(dict(nom=f"Light_Totem_{i+1}", pos=[t["x"], t["h"], t["z"]], cible=[cx, 0, cz], lumens=20000, angle=math.radians(60), couleur=[0.75, 0.55, 1.0]))
    for i, w in enumerate(L["wash"]):
        lumieres.append(dict(nom=f"Light_Wash_{i+1}", pos=[w["x"], .5, w["z"]], cible=[w["tx"], w["ty"], 0], lumens=15000, angle=math.radians(30), couleur=[0.75, 0.55, 1.0]))
    for i, l in enumerate(pos["scene_l"]):
        lumieres.append(dict(nom=f"Light_Scene_{i+1}", pos=[l["x"], l["h"], l["z"]], cible=[pb["x"], pb["H"] + 1.2, pb["tete"]["z0"] - 2], lumens=8000, angle=math.radians(50), couleur=[0.4, 0.75, 1.0] if i == 0 else [1.0, 0.45, 0.6]))

    out = os.path.join(D_SCENE, "Implantation.glb")
    scene.export(out)
    injecter_lumieres_glb(out, lumieres)
    json.dump(dict(unites="cm", repere="Unreal : X avant (= recul Z du modèle), Y droite (= X modèle), Z haut (= Y modèle)", version=2,
                   cables_m=round(longueur, 1),
                   acteurs=placement, lumieres=[dict(nom=l["nom"], location_cm=[l["pos"][2]*100, l["pos"][0]*100, l["pos"][1]*100],
                                                     cible_cm=[l["cible"][2]*100, l["cible"][0]*100, l["cible"][1]*100], lumens=l["lumens"],
                                                     cone_deg=round(math.degrees(l["angle"]), 1)) for l in lumieres]),
              open(os.path.join(PROJ, "Content", "Import", "placement.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_el = len([f for f in os.listdir(D_ELEM) if f.endswith(".glb")])
    print(f"scène : {out}  ({len(scene.geometry)} géométries, {len(placement)} acteurs, {len(lumieres)} lumières, câbles {longueur:.0f} m)")
    print(f"éléments : {n_el} GLB + OBJ dans {D_ELEM}")

if __name__ == "__main__":
    main()
