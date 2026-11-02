# -*- coding: utf-8 -*-
"""
demo_sequence.py — à lancer DANS l'éditeur Unreal, APRÈS assembler_scene.py.

Transforme le niveau d'implantation en démo animée : matériaux, ciel et
soleil animés, éclairage public, village, ambiance, mapping, lasers et
caméra, pilotés par une Level Sequence qui parcourt la soirée de 16 h à 2 h.

    Tools > Execute Python Script…  →  ce fichier
Résultat : /Game/Maps/Implantation enrichi + /Game/Implantation/Seq_Soiree

Paramètres : Content/Import/demo_params.json (mêmes valeurs que la démo HTML
outils/demo-evenement.html). Tout ce qui est chiffré est là, pas ici.

Ce script n'a pas été exécuté dans Unreal (pas de licence sur la machine
qui l'a écrit). Il suit l'API Python de l'éditeur UE 5.3/5.4 ; si une ligne
casse, l'Output Log donne la fonction : le découpage en étapes permet de
relancer une étape seule (voir `ETAPES` en bas).
"""
import json, math, os, unreal

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
PARAMS = json.load(open(os.path.join(RACINE, "Content", "Import", "demo_params.json"), encoding="utf-8"))
IMPL = json.load(open(os.path.join(RACINE, "..", "implantation.json"), encoding="utf-8"))
D_MAT = "/Game/Implantation/Materials"
D_SEQ = "/Game/Implantation"
NOM_SEQ = "Seq_Soiree"
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
MEL = unreal.MaterialEditingLibrary
ATH = unreal.AssetToolsHelpers.get_asset_tools()

H0, H1 = PARAMS["scenario"]["heure_debut"], PARAMS["scenario"]["heure_fin"]
SPH = PARAMS["scenario"]["secondes_par_heure"]
FPS = 30
def frame(t): return unreal.FrameNumber(int(round((t - H0) * SPH * FPS)))
def m2cm(v): return [v[2]*100, v[0]*100, v[1]*100]     # modèle (x, y haut, z recul) -> UE (X avant, Y droite, Z haut)
def lc(rgb): return unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0)

def acteurs(prefixe):
    return [a for a in EAS.get_all_level_actors() if a.get_actor_label().startswith(prefixe)]

# ------------------------------------------------------------ 1. matériaux
def creer_materiau(nom, p):
    """Matériau PBR simple à paramètres (couleur, rugosité, métal, émission),
    + un bruit procédural en normale pour la pierre et le pavé."""
    chemin = f"{D_MAT}/{nom}"
    if unreal.EditorAssetLibrary.does_asset_exist(chemin):
        return unreal.load_asset(chemin)
    mat = ATH.create_asset(nom, D_MAT, unreal.Material, unreal.MaterialFactoryNew())
    base = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -600, 0)
    base.set_editor_property("parameter_name", "Base"); base.set_editor_property("default_value", lc(p.get("base", [0.5, 0.5, 0.5])))
    MEL.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rug = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -600, 200)
    rug.set_editor_property("parameter_name", "Rugosite"); rug.set_editor_property("default_value", float(p.get("rugosite", 0.8)))
    MEL.connect_material_property(rug, "", unreal.MaterialProperty.MP_ROUGHNESS)
    met = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -600, 300)
    met.set_editor_property("parameter_name", "Metal"); met.set_editor_property("default_value", float(p.get("metal", 0.0)))
    MEL.connect_material_property(met, "", unreal.MaterialProperty.MP_METALLIC)
    # émission pilotable (fenêtres, vitre régie, vitraux, image mapping) : couleur × intensité
    ec = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -800, 450)
    ec.set_editor_property("parameter_name", "EmissionCouleur"); ec.set_editor_property("default_value", lc(p.get("couleur_emission", [1, 0.9, 0.7])))
    ei = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -800, 600)
    ei.set_editor_property("parameter_name", "EmissionIntensite"); ei.set_editor_property("default_value", 0.0)
    mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -500, 500)
    MEL.connect_material_expressions(ec, "", mul, "A"); MEL.connect_material_expressions(ei, "", mul, "B")
    MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if p.get("normale_force"):
        # relief procédural : bruit → normale (suffit pour que la lumière rasante "accroche" la pierre)
        bruit = MEL.create_material_expression(mat, unreal.MaterialExpressionNoise, -900, 800)
        bruit.set_editor_property("scale", 0.02); bruit.set_editor_property("levels", 4)
        force = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -900, 950)
        force.set_editor_property("parameter_name", "NormaleForce"); force.set_editor_property("default_value", float(p["normale_force"]))
        m2 = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -650, 850)
        MEL.connect_material_expressions(bruit, "", m2, "A"); MEL.connect_material_expressions(force, "", m2, "B")
        # on pousse le bruit dans la normale via un Append (x,y) et un z constant à 1
        app = MEL.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -450, 850)
        MEL.connect_material_expressions(m2, "", app, "A"); MEL.connect_material_expressions(m2, "", app, "B")
        un = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -450, 980); un.set_editor_property("r", 1.0)
        app2 = MEL.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -300, 900)
        MEL.connect_material_expressions(app, "", app2, "A"); MEL.connect_material_expressions(un, "", app2, "B")
        MEL.connect_material_property(app2, "", unreal.MaterialProperty.MP_NORMAL)
    if p.get("type") in ("volumetrique",) or p.get("additif"):
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
        mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("two_sided", True)
    MEL.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(chemin)
    return mat

def instance(nom, parent, overrides):
    chemin = f"{D_MAT}/{nom}"
    if unreal.EditorAssetLibrary.does_asset_exist(chemin):
        return unreal.load_asset(chemin)
    mi = ATH.create_asset(nom, D_MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in overrides.items():
        if isinstance(v, (list, tuple)): MEL.set_material_instance_vector_parameter_value(mi, k, lc(v))
        else: MEL.set_material_instance_scalar_parameter_value(mi, k, float(v))
    unreal.EditorAssetLibrary.save_asset(chemin)
    return mi

def etape_materiaux():
    M = PARAMS["materiaux"]
    mats = {k: creer_materiau(k, v) for k, v in M.items() if not k.startswith("_") and "base" in v or v.get("type")}
    # tonnelles : une instance par type de stand
    for typ, rgb in M["M_Tente"]["base_par_type"].items():
        mats[f"MI_Tente_{typ}"] = instance(f"MI_Tente_{typ}", mats["M_Tente"], {"Base": rgb})
    # affectation par préfixe d'acteur
    affect = {"Facade": "M_Pierre", "Nef": "M_Pierre", "Sol": "M_Pave", "Voisin": "M_Voisin", "Regie": "M_Regie",
              "PlateformeVP": "M_Echafaud", "PA_": "M_Sono", "Delai": "M_Sono", "Totem": "M_Sono", "VP_": "M_Sono", "Laser_": "M_Sono",
              "TourLayher": "M_Echafaud", "Podium": "M_Deck", "ProjScene": "M_Sono", "Camion": "M_Regie", "Subs_": "M_Sono", "FrontFill": "M_Sono",
              "Repos": "M_Tente", "Stockage": "M_Tente", "Bache": "M_Sono", "Armoire": "M_Regie", "GE_": "M_Sono", "Cables": "M_Sono", "FaisceauScene": "M_Faisceau",
              "Cone": "M_ConeVP", "FaisceauTotem": "M_Faisceau", "FaisceauWash": "M_Faisceau", "FaisceauLaser": "M_Laser"}
    n = 0
    for a in EAS.get_all_level_actors():
        if not isinstance(a, unreal.StaticMeshActor): continue
        lab = a.get_actor_label(); mat = None
        if lab.startswith("Stand_"):
            typ = next((s["type"] for s in IMPL["village"]["stands"] if lab == "Stand_" + s["nom"].replace(" ", "_").replace("·", "-")), "asso")
            mat = mats.get(f"MI_Tente_{typ}")
        else:
            for k, v in affect.items():
                if lab.startswith(k): mat = mats.get(v); break
        if mat:
            c = a.static_mesh_component
            for i in range(c.get_num_materials()): c.set_material(i, mat)
            n += 1
    unreal.log(f"[demo] matériaux : {len(mats)} créés, {n} acteurs habillés")
    return mats

# ------------------------------------------------------- 2. ciel et soleil
def etape_ciel():
    S = PARAMS["soleil"]
    for a in acteurs("Demo_"): a.destroy_actor()
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000)); sun.set_actor_label("Demo_Soleil"); sun.tags = ["implantation", "demo"]
    c = sun.light_component
    c.set_intensity_units(unreal.LightUnits.LUX) if hasattr(c, "set_intensity_units") else None
    c.set_intensity(float(S["intensite_lux_midi"]))
    c.set_editor_property("use_temperature", True); c.set_temperature(float(S["temperature_K_midi"]))
    c.set_editor_property("atmosphere_sun_light", True)
    c.set_editor_property("light_shaft_bloom", True)
    atmo = EAS.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)); atmo.set_actor_label("Demo_Atmosphere"); atmo.tags = ["implantation", "demo"]
    nuages = EAS.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0)); nuages.set_actor_label("Demo_Nuages"); nuages.tags = ["implantation", "demo"]
    fog = EAS.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0)); fog.set_actor_label("Demo_Brouillard"); fog.tags = ["implantation", "demo"]
    fc = fog.component; fc.set_editor_property("fog_density", float(S["brouillard"]["densite"])); fc.set_editor_property("fog_height_falloff", 0.2)
    fc.set_editor_property("volumetric_fog", True)          # c'est lui qui rend les cônes VP et faisceaux visibles "dans l'air"
    fc.set_editor_property("volumetric_fog_scattering_distribution", 0.2)
    sky = next((a for a in EAS.get_all_level_actors() if isinstance(a, unreal.SkyLight)), None) or EAS.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 500))
    sky.set_actor_label("Demo_SkyLight"); sky.tags = ["implantation", "demo"]
    sky.light_component.set_editor_property("real_time_capture", True)
    pp = EAS.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0)); pp.set_actor_label("Demo_PostProcess"); pp.tags = ["implantation", "demo"]
    pp.set_editor_property("unbound", True)
    st = pp.settings
    st.set_editor_property("override_auto_exposure_method", True); st.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM)
    st.set_editor_property("override_auto_exposure_min_brightness", True); st.set_editor_property("auto_exposure_min_brightness", -3.0)
    st.set_editor_property("override_auto_exposure_max_brightness", True); st.set_editor_property("auto_exposure_max_brightness", 12.0)
    st.set_editor_property("override_bloom_intensity", True); st.set_editor_property("bloom_intensity", 0.5)
    unreal.log("[demo] ciel : soleil, atmosphère, nuages, brouillard volumétrique, post-process")
    return sun

# ------------------------------------------------- 3. lumières de la démo
def etape_lumieres():
    L = PARAMS["lumieres"]
    Z = IMPL["projet"]["zonePublic"]
    for a in acteurs("DemoL_"): a.destroy_actor()
    # candélabres : 8 autour de la zone public
    pos = [[-34, 2], [34, 2], [-34, 30], [34, 30], [-34, 58], [34, 58], [-14, 66], [14, 66]]
    for i, (x, z) in enumerate(pos):
        p = EAS.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*m2cm([x, L["candelabres"]["hauteur_m"], z])))
        p.set_actor_label(f"DemoL_Candelabre_{i+1}"); p.set_folder_path("08_Demo"); p.tags = ["implantation", "demo"]
        c = p.point_light_component; c.set_intensity_units(unreal.LightUnits.LUMENS); c.set_intensity(float(L["candelabres"]["lumens"]))
        c.set_editor_property("use_temperature", True); c.set_temperature(float(L["candelabres"]["temperature_K"])); c.set_attenuation_radius(L["candelabres"]["rayon_m"] * 100)
    # stands : une lumière chaude par tonnelle
    for a in acteurs("Stand_"):
        loc = a.get_actor_location(); loc.z = L["stands"]["hauteur_m"] * 100
        p = EAS.spawn_actor_from_class(unreal.PointLight, loc); p.set_actor_label("DemoL_" + a.get_actor_label()); p.set_folder_path("08_Demo"); p.tags = ["implantation", "demo"]
        c = p.point_light_component; c.set_intensity_units(unreal.LightUnits.LUMENS); c.set_intensity(float(L["stands"]["lumens"]))
        c.set_editor_property("use_temperature", True); c.set_temperature(float(L["stands"]["temperature_K"])); c.set_attenuation_radius(L["stands"]["rayon_m"] * 100)
    unreal.log("[demo] lumières : candélabres et stands posés")

# ------------------------------------------------------------ 4. séquence
def etape_sequence(sun):
    """Une Level Sequence qui parcourt la soirée : chaque heure = secondes_par_heure.
    On anime : rotation du soleil, intensité des groupes de lumières, émission
    des matériaux, caméra."""
    chemin = f"{D_SEQ}/{NOM_SEQ}"
    if unreal.EditorAssetLibrary.does_asset_exist(chemin): unreal.EditorAssetLibrary.delete_asset(chemin)
    seq = ATH.create_asset(NOM_SEQ, D_SEQ, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    seq.set_playback_start(0); seq.set_playback_end(int((H1 - H0) * SPH * FPS))
    phases = PARAMS["scenario"]["phases"]; S = PARAMS["soleil"]

    def piste_float(acteur, chemin_prop, cles):
        """ajoute une piste de propriété float sur un acteur possédé par la séquence."""
        b = seq.add_possessable(acteur)
        tr = b.add_track(unreal.MovieSceneFloatTrack); tr.set_property_name_and_path(chemin_prop.split(".")[-1], chemin_prop)
        sec = tr.add_section(); sec.set_range(0, seq.get_playback_end())
        ch = sec.get_channels()[0]
        for t, v in cles: ch.add_key(frame(t), float(v))
        return b

    # soleil : rotation (pitch = -élévation) et intensité
    def elev(t): return math.sin((t - S["lever"]) / (S["coucher"] - S["lever"]) * math.pi) * S["elevation_max_deg"]
    bs = seq.add_possessable(sun)
    tr = bs.add_track(unreal.MovieScene3DTransformTrack); sec = tr.add_section(); sec.set_range(0, seq.get_playback_end())
    chans = sec.get_channels()      # [loc x,y,z, rot x(roll), y(pitch), z(yaw), scale x,y,z]
    t = H0
    while t <= H1 + 1e-6:
        e = elev(t); az = (t - 13.5) / 12 * 180 + 180      # yaw : sud à 13h30
        chans[4].add_key(frame(t), -max(e, -12.0)); chans[5].add_key(frame(t), az)
        t += 0.25
    piste_float(sun, "LightComponent0.Intensity", [(t_, S["intensite_lux_midi"] * max(0.0, min(1.0, elev(t_) / 25.0)) + 0.5) for t_ in [H0 + i * 0.25 for i in range(int((H1 - H0) * 4) + 1)]])
    piste_float(sun, "LightComponent0.Temperature", [(t_, S["temperature_K_coucher"] + (S["temperature_K_midi"] - S["temperature_K_coucher"]) * max(0.0, min(1.0, elev(t_) / 15.0))) for t_ in [H0 + i * 0.5 for i in range(int((H1 - H0) * 2) + 1)]])

    # groupes de lumières : on/off par phase, avec fondu
    def cles_groupe(cle, pleine):
        out = []
        for i, ph in enumerate(phases):
            v = pleine if ph[cle] else 0.0
            out.append((ph["t"], v))
            if i + 1 < len(phases): out.append((phases[i + 1]["t"] - 0.08, v))
        return out
    nuit = lambda t_: 1.0 if elev(t_) < -6 else 0.0
    for a in acteurs("DemoL_Candelabre"):
        piste_float(a, "PointLightComponent0.Intensity", [(t_, v * nuit(t_)) for t_, v in cles_groupe("eclairage_public", PARAMS["lumieres"]["candelabres"]["lumens"])])
    for a in acteurs("DemoL_Stand_"):
        piste_float(a, "PointLightComponent0.Intensity", cles_groupe("village", PARAMS["lumieres"]["stands"]["lumens"]))
    for a in acteurs("Light_Totem"):
        piste_float(a, "SpotLightComponent0.Intensity", cles_groupe("ambiance", PARAMS["lumieres"]["totems"]["lumens"]))
    for a in acteurs("Light_Wash"):
        piste_float(a, "SpotLightComponent0.Intensity", cles_groupe("ambiance", PARAMS["lumieres"]["wash_facade"]["lumens"]))
    for a in acteurs("Light_VP"):
        piste_float(a, "SpotLightComponent0.Intensity", cles_groupe("mapping", IMPL["projecteurs"][0]["lumens"]))
    # visibilité des volumes d'étude : cônes VP avec le mapping, faisceaux laser avec les lasers, faisceaux lumière avec l'ambiance
    def piste_visibilite(acteur, cle):
        b = seq.add_possessable(acteur); tr = b.add_track(unreal.MovieSceneVisibilityTrack); sec = tr.add_section(); sec.set_range(0, seq.get_playback_end())
        ch = sec.get_channels()[0]
        for ph in phases: ch.add_key(frame(ph["t"]), bool(ph[cle]))
    for a in acteurs("ConeVP"): piste_visibilite(a, "mapping")
    for a in acteurs("FaisceauLaser"): piste_visibilite(a, "lasers")
    for a in acteurs("FaisceauTotem"): piste_visibilite(a, "ambiance")
    for a in acteurs("FaisceauWash"): piste_visibilite(a, "ambiance")
    for a in acteurs("ZonePublic"): piste_visibilite(a, "public") if False else None

    # caméra : CineCameraActor sur le plan-séquence
    C = PARAMS["cameras"]
    cam = EAS.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(*m2cm(C["plan_sequence"][0]["pos_m"])))
    cam.set_actor_label("Demo_Camera"); cam.set_folder_path("08_Demo"); cam.tags = ["implantation", "demo"]
    cam.cine_camera_component.set_editor_property("current_focal_length", float(C["focale_mm"]))
    bc = seq.add_possessable(cam)
    trc = bc.add_track(unreal.MovieScene3DTransformTrack); sc = trc.add_section(); sc.set_range(0, seq.get_playback_end()); cc = sc.get_channels()
    for k in C["plan_sequence"]:
        p = m2cm(k["pos_m"]); c = m2cm(k["cible_m"])
        rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*p), unreal.Vector(*c))
        for i, v in enumerate(p): cc[i].add_key(frame(k["t"]), float(v))
        cc[3].add_key(frame(k["t"]), rot.roll); cc[4].add_key(frame(k["t"]), rot.pitch); cc[5].add_key(frame(k["t"]), rot.yaw)
    cut = seq.add_track(unreal.MovieSceneCameraCutTrack); cs = cut.add_section(); cs.set_range(0, seq.get_playback_end())
    cs.set_camera_binding_id(bc.get_binding_id())
    unreal.EditorAssetLibrary.save_asset(chemin)
    unreal.log(f"[demo] séquence {chemin} : {int((H1 - H0) * SPH)} s, {FPS} i/s — ouvre-la dans Sequencer, puis Render (Movie Render Queue) pour la vidéo")
    return seq

ETAPES = {"materiaux": etape_materiaux, "ciel": etape_ciel, "lumieres": etape_lumieres}

def main():
    with unreal.ScopedSlowTask(4, "Démo animée") as st:
        st.make_dialog(True)
        st.enter_progress_frame(1, "Matériaux"); etape_materiaux()
        st.enter_progress_frame(1, "Ciel");       sun = etape_ciel()
        st.enter_progress_frame(1, "Lumières");   etape_lumieres()
        st.enter_progress_frame(1, "Séquence");   etape_sequence(sun)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.log("[demo] terminé")

main()
