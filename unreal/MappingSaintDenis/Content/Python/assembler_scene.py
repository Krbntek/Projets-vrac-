# -*- coding: utf-8 -*-
"""
assembler_scene.py — à lancer DANS l'éditeur Unreal (Python Editor Script Plugin).

    Menu  Tools > Execute Python Script…  → choisir ce fichier
    ou, dans l'Output Log, en mode Python :
        exec(open(r"<chemin>/Content/Python/assembler_scene.py", encoding="utf-8").read())

Ce qu'il fait, dans l'ordre :
  1. importe chaque élément Content/Import/Elements/SM_*.glb en Static Mesh
     dans /Game/Implantation/Meshes (un asset par élément, retravaillable)
  2. crée (ou vide) le niveau /Game/Maps/Implantation
  3. place un StaticMeshActor par ligne de Content/Import/placement.json,
     rangé dans des dossiers de l'Outliner (Facade, Bloc, Village, Sono, Lumieres…)
  4. ajoute un SpotLight par vidéoprojecteur / totem / wash, intensité en lumens
  5. pose une caméra "Public" à 1,70 m dans la zone public, et un ciel

Alternative sans script : File > Import Into Level… → Scene/Implantation.glb,
qui recrée la hiérarchie et les lumières d'un coup, mais en un seul import
moins commode à retravailler élément par élément.

Repère : implantation.json est en mètres, X = axe façade, Y = haut, Z = recul.
Unreal est en cm, X avant, Y droite, Z haut. placement.json est DÉJÀ converti.
"""
import json, os, unreal

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
D_ELEM = os.path.join(RACINE, "Content", "Import", "Elements")
PLACEMENT = os.path.join(RACINE, "Content", "Import", "placement.json")
DEST_MESH = "/Game/Implantation/Meshes"
NIVEAU = "/Game/Maps/Implantation"

DOSSIERS = {  # préfixe d'acteur -> dossier Outliner
    "Facade": "01_Facade", "Nef": "01_Facade", "Sol": "00_Site", "Voisin": "00_Site", "ZonePublic": "00_Site",
    "TourLayher": "02_Bloc_central", "PlateformeVP": "02_Bloc_central", "Regie": "02_Bloc_central", "VP_": "02_Bloc_central", "Laser": "02_Bloc_central",
    "Podium": "08_Scene_catwalk", "ProjScene": "08_Scene_catwalk", "FaisceauScene": "06_Faisceaux",
    "Camion": "09_Camion_DJ",
    "Stand": "03_Village", "Repos": "11_Repos_stockage", "Stockage": "11_Repos_stockage", "Bache": "11_Repos_stockage",
    "Subs_": "04_Sono", "PA_": "04_Sono", "FrontFill": "04_Sono", "Delai": "04_Sono", "Sono": "04_Sono",
    "Totem": "05_Lumieres", "Wash": "05_Lumieres", "Cone": "06_Faisceaux", "Faisceau": "06_Faisceaux", "Light": "05_Lumieres",
    "Armoire": "10_Electricite_cables", "GE_": "10_Electricite_cables", "Cables": "10_Electricite_cables",
}
def dossier(nom):
    for k, v in DOSSIERS.items():
        if nom.startswith(k): return v
    return "99_Divers"

# --------------------------------------------------------------- 1. import
def importer_elements():
    """Interchange (UE 5.1+) importe le glTF en mètres → cm automatiquement."""
    taches = []
    for f in sorted(os.listdir(D_ELEM)):
        if not f.endswith(".glb"): continue
        t = unreal.AssetImportTask()
        t.filename = os.path.join(D_ELEM, f)
        t.destination_path = DEST_MESH
        t.destination_name = f[:-4]
        t.replace_existing = True
        t.automated = True
        t.save = True
        taches.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(taches)
    importes = {}
    for t in taches:
        # Interchange peut produire plusieurs assets (maillages + matériaux) : on garde le StaticMesh
        for chemin in list(t.imported_object_paths or []):
            a = unreal.load_asset(chemin)
            if isinstance(a, unreal.StaticMesh):
                importes[t.destination_name] = a; break
        if t.destination_name not in importes:
            # repli : un StaticMesh du même nom dans le dossier
            cand = unreal.load_asset(f"{DEST_MESH}/{t.destination_name}")
            if cand: importes[t.destination_name] = cand
    unreal.log(f"[implantation] {len(importes)} éléments importés dans {DEST_MESH}")
    return importes

# --------------------------------------------------------------- 2. niveau
def ouvrir_niveau():
    sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(NIVEAU):
        sub.load_level(NIVEAU)
        # on vide ce qui vient d'un assemblage précédent (tag 'implantation')
        for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
            if "implantation" in [str(t) for t in a.tags]: a.destroy_actor()
    else:
        sub.new_level(NIVEAU)

# --------------------------------------------------------------- 3. acteurs
def placer(importes):
    P = json.load(open(PLACEMENT, encoding="utf-8"))
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n = 0
    for a in P["acteurs"]:
        sm = importes.get(a["element"])
        if not sm:
            unreal.log_warning(f"[implantation] élément absent : {a['element']}"); continue
        loc = unreal.Vector(*a["location_cm"])
        rot = unreal.Rotator(0.0, 0.0, 0.0); rot.yaw = a.get("yaw_deg", 0.0)
        act = eas.spawn_actor_from_class(unreal.StaticMeshActor, loc, rot)
        act.set_actor_label(a["acteur"])
        act.static_mesh_component.set_static_mesh(sm)
        act.set_folder_path(dossier(a["acteur"]))
        act.tags = ["implantation"]
        if a["element"].startswith(("SM_Cone", "SM_Faisceau", "SM_Sono_Couverture", "SM_ZonePublic", "SM_Cables")):
            act.static_mesh_component.set_cast_shadow(False)   # volumes d'étude, pas d'ombre
        n += 1
    unreal.log(f"[implantation] {n} acteurs placés")
    return P

# --------------------------------------------------------------- 4. lumières
def lumieres(P):
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for l in P["lumieres"]:
        loc = unreal.Vector(*l["location_cm"]); cible = unreal.Vector(*l["cible_cm"])
        rot = unreal.MathLibrary.find_look_at_rotation(loc, cible)
        act = eas.spawn_actor_from_class(unreal.SpotLight, loc, rot)
        act.set_actor_label(l["nom"]); act.set_folder_path("05_Lumieres"); act.tags = ["implantation"]
        c = act.spot_light_component
        c.set_intensity_units(unreal.LightUnits.LUMENS)
        c.set_intensity(float(l["lumens"]))
        c.set_outer_cone_angle(float(l["cone_deg"]) / 2.0)
        c.set_inner_cone_angle(float(l["cone_deg"]) * 0.4)
        c.set_attenuation_radius(20000.0)
        if l["nom"].startswith("Light_VP"):
            c.set_light_color(unreal.LinearColor(1.0, 0.94, 0.86, 1.0))
            c.set_source_radius(10.0)
        else:
            c.set_light_color(unreal.LinearColor(0.75, 0.55, 1.0, 1.0))
    unreal.log(f"[implantation] {len(P['lumieres'])} spots (unités : lumens)")

# --------------------------------------------------------------- 5. ambiance
def ambiance():
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # nuit urbaine : ciel sombre, un peu de lumière ambiante
    sky = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500)); sky.set_actor_label("SkyLight_nuit"); sky.tags = ["implantation"]
    sky.light_component.set_intensity(0.08)
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(4200.0, 0.0, 170.0),
                                     unreal.MathLibrary.find_look_at_rotation(unreal.Vector(4200.0, 0.0, 170.0), unreal.Vector(0.0, 0.0, 1600.0)))
    cam.set_actor_label("Camera_Public_1m70"); cam.set_folder_path("07_Cameras"); cam.tags = ["implantation"]
    cam2 = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(9500.0, 1800.0, 1400.0),
                                      unreal.MathLibrary.find_look_at_rotation(unreal.Vector(9500.0, 1800.0, 1400.0), unreal.Vector(7600.0, 0.0, 300.0)))
    cam2.set_actor_label("Camera_Bloc_central"); cam2.set_folder_path("07_Cameras"); cam2.tags = ["implantation"]

def main():
    with unreal.ScopedSlowTask(5, "Assemblage de l'implantation") as t:
        t.make_dialog(True)
        t.enter_progress_frame(1, "Import des éléments"); importes = importer_elements()
        t.enter_progress_frame(1, "Niveau");              ouvrir_niveau()
        t.enter_progress_frame(1, "Placement");           P = placer(importes)
        t.enter_progress_frame(1, "Lumières");            lumieres(P)
        t.enter_progress_frame(1, "Ambiance");            ambiance()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.log("[implantation] terminé — niveau " + NIVEAU)

main()
