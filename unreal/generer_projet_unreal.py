#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_projet_unreal.py — fabrique les fichiers 3D du plan d'implantation
pour Unreal Engine, à partir de implantation.json (la même source que le
visualiseur outils/implantation-3d.html).

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

Dépendances : trimesh, shapely, numpy   (pip install trimesh shapely numpy)
"""

import json, math, os, sys
import numpy as np
import trimesh
from trimesh.creation import box, cylinder, cone, extrude_polygon
from trimesh.visual.material import PBRMaterial
from shapely.geometry import Polygon

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "implantation.json")
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
    "echafaud": mat("M_Echafaud", (0.79, 0.54, 0.24), rough=0.6, metal=0.3),
    "deck":     mat("M_Deck",     (0.54, 0.35, 0.15)),
    "bache":    mat("M_Bache",    (0.95, 0.95, 0.95), alpha=0.55),
    "projo":    mat("M_Projo",    (0.13, 0.15, 0.19), rough=0.4, metal=0.5),
    "noir":     mat("M_Noir",     (0.07, 0.08, 0.10), rough=0.5, metal=0.4),
    "inox":     mat("M_Inox",     (0.55, 0.57, 0.59), rough=0.4, metal=0.6),
    "comptoir": mat("M_Comptoir", (0.42, 0.35, 0.27)),
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
    g = cone(radius=rayon, height=L, sections=seg)     # base en z=0, pointe en z=L
    g.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))  # pointe en z=0, base en z=-L
    g.apply_transform(trimesh.geometry.align_vectors([0, 0, -1], d / L))
    g.apply_translation(s)
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def PYRAMIDE_CONE(sommet, base_centre, rayon, m):
    """pyramide à 4 pans (toit de tonnelle) : cône à 4 sections tourné de 45°."""
    g = CONE(sommet, base_centre, rayon, m, seg=4); return g

def FRUSTUM_VP(P, coins, m):
    """pyramide tronquée VP : pointe P, 4 coins de l'image sur la façade."""
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

def EXTRUDE_XY(points, epaisseur, m):
    """profil dans le plan XY (Y haut) extrudé selon Z, de z=-epaisseur à 0."""
    g = extrude_polygon(Polygon(points), epaisseur)     # extrusion selon +z local
    g.apply_translation([0, 0, -epaisseur])
    g.visual = trimesh.visual.TextureVisuals(material=m); return g

def assembler(parts, nom):
    s = trimesh.Scene()
    for i, p in enumerate(parts): s.add_geometry(p, node_name=f"{nom}_{i}", geom_name=f"{nom}_{i}")
    return s

# ------------------------------------------------------------- positions
# même logique que le visualiseur (posPlateforme, regieAABB, posStands…)
def positions(E):
    b, r, v, s = E["bloc"], E["regie"], E["village"], E["sono"]
    pl = dict(x0=b["x"] - b["largeurPlateforme"] / 2, x1=b["x"] + b["largeurPlateforme"] / 2,
              z0=b["z"] - b["profondeurPlateforme"] / 2, z1=b["z"] + b["profondeurPlateforme"] / 2, h=b["hauteurVP"])
    zc = pl["z1"] + r["ecart"] + r["largeur"] / 2
    rg = dict(x=b["x"], z=zc, L=r["longueur"], l=r["largeur"], h=r["hauteur"], z1=zc + r["largeur"] / 2)
    stands = []
    z0 = rg["z1"] + v["ecartRegie"] + v["cote"] / 2
    for i, st in enumerate(v["stands"]):
        rang, cote = i // 2, (1 if i % 2 else -1)
        stands.append(dict(nom=st["nom"], type=st["type"], x=b["x"] + cote * (v["allee"] / 2 + v["cote"] / 2), z=z0 + rang * v["pas"]))
    pa = [dict(nom="PA_jardin", x=-s["x"], z=s["z"], cote=-1), dict(nom="PA_cour", x=s["x"], z=s["z"], cote=1)]
    delais = [dict(nom=f"Delai_{i+1}", x=(1 if i % 2 else -1) * s["delaiX"], z=s["delaiZ"], cote=(1 if i % 2 else -1)) for i in range(s["delais"])]
    vps = [dict(p, x=b["x"] + p["dx"], y=b["hauteurVP"], z=b["z"]) for p in E["projecteurs"]]
    lasers = [dict(l, x=b["x"] + l["dx"], y=b["hauteurVP"] + l["dy"], z=b["z"]) for l in E["lasers"]]
    return dict(pl=pl, rg=rg, stands=stands, pa=pa, delais=delais, vps=vps, lasers=lasers)

def cadre_image(p):
    W = p["z"] / p["tr"]; H = W / p["ratio"]
    return dict(W=W, H=H, x0=p["cx"] - W / 2, x1=p["cx"] + W / 2, y0=p["cy"] - H / 2, y1=p["cy"] + H / 2)

# ------------------------------------------------------------- éléments
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

def elem_nef(n):  # à l'origine : x centré, z de -(L) à 0
    L = n["z1"] - n["z0"]
    return [B(n["x0"], n["x1"], 0, n["h"], -L, 0, M["nef"]), B(n["x0"] - .5, n["x1"] + .5, n["h"], n["h"] + 1.5, -L, 0, M["toiture"])]

def elem_boite_sol(w, h, d, m):  # centré en x/z, sol à 0
    return [B(-w / 2, w / 2, 0, h, -d / 2, d / 2, m)]

def elem_plateforme(pl):
    w, d, h = pl["x1"] - pl["x0"], pl["z1"] - pl["z0"], pl["h"]
    m, parts = M["echafaud"], []
    xs = np.linspace(-w / 2, w / 2, max(2, round(w / 2.25) + 1)); zs = [-d / 2, d / 2]
    for x in xs:
        for z in zs: parts.append(CYL([x, 0, z], [x, h - .25, z], .05, m))
    y = 2.0
    while y < h - .3:
        for z in zs: parts.append(CYL([-w / 2, y, z], [w / 2, y, z], .03, m))
        for x in (-w / 2, w / 2): parts.append(CYL([x, y, -d / 2], [x, y, d / 2], .03, m))
        y += 2.0
    parts.append(B(-w / 2 - .15, w / 2 + .15, h - .45, h - .2, -d / 2 - .15, d / 2 + .15, M["deck"]))
    for (a, b2, c, e) in [(-w/2,-d/2,w/2,-d/2),(-w/2,d/2,w/2,d/2),(-w/2,-d/2,-w/2,d/2),(w/2,-d/2,w/2,d/2)]:
        parts.append(CYL([a, h + .9, b2], [c, h + .9, e], .025, m))
    parts.append(B(-w / 2 - .2, w / 2 + .2, h + 2.3, h + 2.4, -d / 2 - .2, d / 2 + .2, M["bache"]))
    return parts

def elem_regie(rg):
    L, l, h = rg["L"], rg["l"], rg["h"]
    parts = [B(-L / 2, L / 2, 0, h, -l / 2, l / 2, M["regie"]),
             PLAN_XY(-L / 2 + .4, -L / 2 + 1.4, 0, 2.2, l / 2 + .01, M["inox"]),            # porte côté village
             PLAN_XY(-0.6, 1.8, 1.15, 2.05, -l / 2 - .01, M["vitrail"]),                   # vitre côté façade
             B(L / 2 - 1.2, L / 2 - .2, h, h + .6, -.5, .5, M["inox"])]                     # clim
    return parts

def elem_tonnelle(c, couleur):
    h0, h1 = 2.2, 3.0
    mt = mat("M_Tente", couleur, rough=0.9)
    parts = [CYL([x, 0, z], [x, h0, z], .035, M["inox"]) for x in (-c / 2, c / 2) for z in (-c / 2, c / 2)]
    parts.append(PYRAMIDE_CONE([0, h1, 0], [0, h0, 0], c * math.sqrt(.5) * 1.02, mt))
    parts[-1].apply_transform(trimesh.transformations.rotation_matrix(math.pi / 4, [0, 1, 0]))
    parts.append(B(-c / 2 + .2, c / 2 - .2, 0, .95, -c / 2 + .1, -c / 2 + .7, M["comptoir"]))
    return parts

def elem_pa(s):
    parts = []
    for i in range(s["subs"]): parts.append(B(-.6, .6, i * .7, i * .7 + .65, -.6, .6, M["noir"]))
    parts.append(CYL([0, 0, 0], [0, s["hauteur"], 0], .04, M["inox"]))
    y = s["hauteur"] - .35
    while y > s["subs"] * .7 + .2:
        parts.append(B(-.45, .45, y - .32, y, -.3, .3, M["noir"])); y -= .38
    return parts

def elem_delai(h):
    parts = [CYL([0, 0, 0], [0, h, 0], .04, M["inox"])]
    y = h - .3
    while y > h - 1.6: parts.append(B(-.3, .3, y - .3, y, -.22, .22, M["noir"])); y -= .38
    return parts

def elem_totem(h):
    return [B(-.5, .5, 0, .25, -.5, .5, M["projo"]), CYL([0, 0, 0], [0, h, 0], .06, M["projo"]), B(-.35, .35, h - .35, h, -.2, .2, M["noir"])]

def elem_wash():
    return [B(-.45, .45, 0, .5, -.35, .35, M["noir"])]

def elem_projecteur():
    return [B(-.3, .3, -.21, .21, -.35, .35, M["projo"]), CYL([0, 0, .35], [0, 0, .47], .14, M["noir"])]

def elem_laser():
    return [B(-.2, .2, -.12, .12, -.2, .2, M["noir"])]

# ------------------------------------------------------------- export
def ecrire_element(nom, parts):
    os.makedirs(D_ELEM, exist_ok=True)
    sc = assembler(parts, nom)
    sc.export(os.path.join(D_ELEM, f"{nom}.glb"))
    # copie OBJ (un seul maillage fusionné, couleurs par matériau perdues partiellement)
    fus = trimesh.util.concatenate(parts)
    fus.export(os.path.join(D_ELEM, f"{nom}.obj"))
    return sc

def T(x, y, z, rot_y=0.0):
    """matrice de placement : translation + rotation autour de Y (haut)."""
    m = trimesh.transformations.rotation_matrix(rot_y, [0, 1, 0])
    m[:3, 3] = [x, y, z]; return m

def look_at_y(src, dst):
    """rotation autour de Y pour qu'un objet tourné vers +Z regarde dst (en plan)."""
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
        cd = lm["lumens"] / (2 * math.pi * (1 - math.cos(lm["angle"] / 2)))   # lumens -> candela sur le cône
        lights.append(dict(name=lm["nom"], type="spot", color=lm["couleur"], intensity=round(cd, 1),
                           spot=dict(innerConeAngle=round(lm["angle"] * .4, 4), outerConeAngle=round(lm["angle"] / 2, 4))))
        d_ = np.array(lm["cible"], float) - np.array(lm["pos"], float); d_ /= np.linalg.norm(d_)
        R = trimesh.geometry.align_vectors([0, 0, -1], d_)                   # le spot glTF éclaire vers -Z local
        q = trimesh.transformations.quaternion_from_matrix(R)                 # (w, x, y, z)
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

def main():
    E = json.load(open(SRC, encoding="utf-8")); P = E["projet"]; pos = positions(E)
    os.makedirs(D_SCENE, exist_ok=True); os.makedirs(D_ELEM, exist_ok=True)
    scene = trimesh.Scene()
    placement = []   # pour placement.json (cm, repère Unreal)

    def poser(nom_elem, parts, instances):
        """exporte l'élément à l'origine et place ses instances dans la scène."""
        ecrire_element(nom_elem, parts)
        fus = trimesh.util.concatenate([p.copy() for p in parts])
        for inst in instances:
            n = inst["nom"]
            scene.add_geometry(fus, node_name=n, geom_name=nom_elem, transform=T(inst["x"], inst.get("y", 0), inst["z"], inst.get("rot", 0.0)))
            placement.append(dict(acteur=n, element=nom_elem,
                                  # Unreal : X avant = Z modèle, Y droite = X modèle, Z haut = Y modèle, en cm
                                  location_cm=[inst["z"] * 100, inst["x"] * 100, inst.get("y", 0) * 100],
                                  yaw_deg=round(math.degrees(inst.get("rot", 0.0)), 2)))

    F = P["facade"]
    poser("SM_Facade", elem_facade(F), [dict(nom="Facade", x=0, z=0)])
    poser("SM_Nef", elem_nef(P["nef"]), [dict(nom="Nef", x=0, z=P["nef"]["z1"])])
    for i, v in enumerate(P["voisins"]):
        poser(f"SM_Voisin_{i+1}", elem_boite_sol(v["x1"] - v["x0"], v["h"], v["z1"] - v["z0"], M["voisin"]),
              [dict(nom=f"Voisin_{i+1}_{v['nom']}".replace(" ", "_"), x=(v["x0"] + v["x1"]) / 2, z=(v["z0"] + v["z1"]) / 2)])
    poser("SM_Sol", [PLAN_XZ(-120, 120, -40, 160, 0, M["pave"])], [dict(nom="Sol", x=0, z=0)])
    Z = P["zonePublic"]
    poser("SM_ZonePublic", [PLAN_XZ(Z["x0"], Z["x1"], Z["z0"], Z["z1"], 0.03, M["zone"])], [dict(nom="ZonePublic", x=0, z=0)])

    pl = pos["pl"]
    poser("SM_PlateformeVP", elem_plateforme(pl), [dict(nom="PlateformeVP", x=(pl["x0"] + pl["x1"]) / 2, z=(pl["z0"] + pl["z1"]) / 2)])
    rg = pos["rg"]
    poser("SM_Regie", elem_regie(rg), [dict(nom="Regie_etanche", x=rg["x"], z=rg["z"])])

    par_type = {}
    for st in pos["stands"]: par_type.setdefault(st["type"], []).append(st)
    for typ, lst in par_type.items():
        poser(f"SM_Tonnelle_{typ}", elem_tonnelle(E["village"]["cote"], TENTE[typ]),
              [dict(nom="Stand_" + st["nom"].replace(" ", "_").replace("·", "-"), x=st["x"], z=st["z"]) for st in lst])

    s = E["sono"]
    poser("SM_PA_Stack", elem_pa(s), [dict(nom=p["nom"], x=p["x"], z=p["z"], rot=math.radians(-p["cote"] * s["visee"])) for p in pos["pa"]])
    if pos["delais"]:
        poser("SM_Delai", elem_delai(s["delaiH"]), [dict(nom=d["nom"], x=d["x"], z=d["z"]) for d in pos["delais"]])
    # secteurs de couverture (plans)
    secteurs = []
    for p in pos["pa"]:
        ang, az = math.radians(s["ouverture"] / 2), math.radians(-p["cote"] * s["visee"])
        pts = [[0, 0]] + [[math.sin(a + az) * s["portee"], math.cos(a + az) * s["portee"]] for a in np.linspace(-ang, ang, 25)]
        v = np.array([[p["x"] + q[0], 0.04, p["z"] + q[1]] for q in pts]); f = [[0, i, i + 1] for i in range(1, len(pts) - 1)]
        g = trimesh.Trimesh(vertices=v, faces=f, process=False); g.visual = trimesh.visual.TextureVisuals(material=M["sono"]); secteurs.append(g)
    poser("SM_Sono_Couverture", secteurs, [dict(nom="Sono_Couverture", x=0, z=0)])

    L = E["lumieres"]
    poser("SM_Totem", elem_totem(L["totems"][0]["h"]), [dict(nom=f"Totem_{i+1}", x=t["x"], z=t["z"]) for i, t in enumerate(L["totems"])])
    poser("SM_WashFacade", elem_wash(), [dict(nom=f"Wash_{i+1}", x=w["x"], z=w["z"]) for i, w in enumerate(L["wash"])])

    # VP, lasers, et leurs faisceaux (géométrie dans le repère monde)
    for i, p in enumerate(pos["vps"]):
        poser(f"SM_Projecteur", elem_projecteur(), [dict(nom="VP_" + str(i + 1), x=p["x"], y=p["y"], z=p["z"], rot=look_at_y([p["x"], p["y"], p["z"]], [p["cx"], p["cy"], 0]) + math.pi)])
        im = cadre_image(p)
        coins = [[im["x0"], im["y0"], 0], [im["x1"], im["y0"], 0], [im["x1"], im["y1"], 0], [im["x0"], im["y1"], 0]]
        poser(f"SM_ConeVP_{i+1}", [FRUSTUM_VP([p["x"], p["y"], p["z"]], coins, M["cone"]),
                                   PLAN_XY(im["x0"], im["x1"], im["y0"], im["y1"], 0.06, mat("M_ImageVP", (1, .71, .33), alpha=.25))],
              [dict(nom=f"ConeVP_{i+1}", x=0, z=0)])
    for i, l in enumerate(pos["lasers"]):
        poser("SM_Laser", elem_laser(), [dict(nom=f"Laser_{i+1}", x=l["x"], y=l["y"], z=l["z"])])
        poser(f"SM_FaisceauLaser_{i+1}", [CYL([l["x"], l["y"], l["z"]], [l["tx"], l["ty"], 0], .05, M["laser"])], [dict(nom=f"FaisceauLaser_{i+1}", x=0, z=0)])
    for i, t in enumerate(L["totems"]):
        cx, cz = (Z["x0"] + Z["x1"]) / 2, (Z["z0"] + Z["z1"]) / 2
        d = np.array([cx - t["x"], -t["h"], cz - t["z"]]); d = d / np.linalg.norm(d) * min(26, np.linalg.norm([cx - t["x"], t["h"], cz - t["z"]]))
        base = [t["x"] + d[0], max(.1, t["h"] + d[1]), t["z"] + d[2]]
        poser(f"SM_FaisceauTotem_{i+1}", [CONE([t["x"], t["h"] - .2, t["z"]], base, 7, M["lum"])], [dict(nom=f"FaisceauTotem_{i+1}", x=0, z=0)])
    for i, w in enumerate(L["wash"]):
        poser(f"SM_FaisceauWash_{i+1}", [CONE([w["x"], .5, w["z"]], [w["tx"], w["ty"], 0], 4.5, M["lum"])], [dict(nom=f"FaisceauWash_{i+1}", x=0, z=0)])

    # lumières réelles (KHR_lights_punctual) : un spot par VP, un par totem, un par wash.
    # trimesh n'écrit pas cette extension : on l'injecte dans le GLB après export.
    lumieres = []
    for i, p in enumerate(pos["vps"]):
        im = cadre_image(p); demi = math.atan((im["W"] / 2) / p["z"])
        lumieres.append(dict(nom=f"Light_VP_{i+1}", pos=[p["x"], p["y"], p["z"]], cible=[p["cx"], p["cy"], 0],
                             lumens=p["lumens"], angle=demi * 2, couleur=[1.0, 0.94, 0.86]))
    for i, t in enumerate(L["totems"]):
        lumieres.append(dict(nom=f"Light_Totem_{i+1}", pos=[t["x"], t["h"], t["z"]], cible=[(Z["x0"]+Z["x1"])/2, 0, (Z["z0"]+Z["z1"])/2], lumens=20000, angle=math.radians(60), couleur=[0.75, 0.55, 1.0]))
    for i, w in enumerate(L["wash"]):
        lumieres.append(dict(nom=f"Light_Wash_{i+1}", pos=[w["x"], .5, w["z"]], cible=[w["tx"], w["ty"], 0], lumens=15000, angle=math.radians(30), couleur=[0.75, 0.55, 1.0]))

    out = os.path.join(D_SCENE, "Implantation.glb")
    scene.export(out)
    injecter_lumieres_glb(out, lumieres)
    json.dump(dict(unites="cm", repere="Unreal : X avant (= recul Z du modèle), Y droite (= X modèle), Z haut (= Y modèle)",
                   acteurs=placement, lumieres=[dict(nom=l["nom"], location_cm=[l["pos"][2]*100, l["pos"][0]*100, l["pos"][1]*100],
                                                     cible_cm=[l["cible"][2]*100, l["cible"][0]*100, l["cible"][1]*100], lumens=l["lumens"],
                                                     cone_deg=round(math.degrees(l["angle"]), 1)) for l in lumieres]),
              open(os.path.join(PROJ, "Content", "Import", "placement.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n_el = len([f for f in os.listdir(D_ELEM) if f.endswith(".glb")])
    print(f"scène : {out}  ({len(scene.geometry)} géométries, {len(placement)} acteurs, {len(lumieres)} lumières)")
    print(f"éléments : {n_el} GLB + OBJ dans {D_ELEM}")

if __name__ == "__main__":
    main()
