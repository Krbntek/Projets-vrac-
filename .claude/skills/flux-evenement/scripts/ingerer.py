#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingerer.py — le registre d'objets d'un événement (evenement/registre.json).

  ajouter   --json '{…}'  |  --fichier objets.json   (un objet ou une liste)
  chercher  <mots>                 recherche dans nom/type/notes, pour relier avant de créer
  lister    [--categorie X]        tableau court
  valider                          champs manquants, doublons, unités
  inventaire                       régénère evenement/INVENTAIRE.md (totaux, manques)
  vers-implantation                pousse les objets spatiaux dans unreal/implantation.json

Lancé depuis n'importe où : il cherche la racine du dépôt (dossier qui contient
evenement/ ou .git). Pas de dépendance hors bibliothèque standard.
"""
import argparse, json, os, re, sys, datetime

def racine():
    d = os.getcwd()
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".git")) or os.path.isdir(os.path.join(d, "evenement")): return d
        d = os.path.dirname(d)
    return os.getcwd()

R = racine()
REG = os.path.join(R, "evenement", "registre.json")
INV = os.path.join(R, "evenement", "INVENTAIRE.md")
IMPL = os.path.join(R, "unreal", "implantation.json")

CATEGORIES = ["materiel", "structure", "espace", "stand", "personne", "contenu", "donnee", "contrainte", "document"]
STATUTS = ["a_confirmer", "confirme", "reserve", "livre", "abandonne"]
ATTENDUS = {  # champs qui, s'ils manquent, rendent l'objet inutilisable plus tard
    "materiel": ["quantite", "dimensions_m", "poids_kg", "puissance_w"],
    "structure": ["quantite", "dimensions_m", "poids_kg"],
    "espace": ["position_m"],
    "stand": ["quantite", "type"],
    "personne": ["equipe", "quantite"],
    "contenu": ["format", "droits"],
    "donnee": ["url", "licence", "recupere_le"],
    "contrainte": ["valeur", "emetteur"],
    "document": ["date", "emetteur"],
}
TYPES_STAND = ["prevention", "secours", "accueil", "buvette", "asso"]

def charger():
    if not os.path.exists(REG):
        return {"version": 1, "evenement": "", "objets": []}
    return json.load(open(REG, encoding="utf-8"))

def ecrire(reg):
    os.makedirs(os.path.dirname(REG), exist_ok=True)
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

# ------------------------------------------------------------------ ajouter
def cmd_ajouter(a):
    reg = charger()
    data = json.loads(a.json) if a.json else json.load(open(a.fichier, encoding="utf-8"))
    objets = data if isinstance(data, list) else [data]
    ids = {o["id"] for o in reg["objets"]}
    crees, maj = [], []
    for o in objets:
        if "id" not in o or "categorie" not in o or "nom" not in o:
            sys.exit(f"objet incomplet (id, categorie, nom obligatoires) : {o}")
        if o["categorie"] not in CATEGORIES: sys.exit(f"catégorie inconnue : {o['categorie']} (attendu : {', '.join(CATEGORIES)})")
        o.setdefault("statut", "a_confirmer"); o.setdefault("type", "?")
        if "source" not in o: print(f"  /!\\ {o['id']} : pas de source — un objet sans source ne se défend pas", file=sys.stderr)
        if o["id"] in ids:
            if not a.remplacer: sys.exit(f"{o['id']} existe déjà : --remplacer pour écraser, ou relie-le (chercher) au lieu de le recréer")
            reg["objets"] = [x for x in reg["objets"] if x["id"] != o["id"]]; maj.append(o["id"])
        else: crees.append(o["id"])
        o["modifie_le"] = datetime.date.today().isoformat()
        reg["objets"].append(o); ids.add(o["id"])
    ecrire(reg)
    print(f"créés : {crees or '—'} | mis à jour : {maj or '—'} | total {len(reg['objets'])}")

# ----------------------------------------------------------------- chercher
def cmd_chercher(a):
    reg = charger(); mots = [m.lower() for m in a.mots]
    for o in reg["objets"]:
        texte = " ".join(str(o.get(k, "")) for k in ("id", "nom", "type", "categorie", "notes", "fournisseur")).lower()
        if all(m in texte for m in mots):
            print(f"  {o['id']:14s} {o['categorie']:10s} {o.get('type','?'):18s} {o['nom']}  [{o.get('statut','?')}]")

def cmd_lister(a):
    reg = charger()
    for o in sorted(reg["objets"], key=lambda o: (o["categorie"], o["id"])):
        if a.categorie and o["categorie"] != a.categorie: continue
        q = o.get("quantite", ""); src = o.get("source", {}).get("entree", "—")
        print(f"  {o['id']:14s} {o['categorie']:10s} {str(q):>3s}  {o['nom'][:42]:42s} {o.get('statut','?'):12s} {src}")

# ------------------------------------------------------------------ valider
def problemes(reg):
    out, vus = [], {}
    for o in reg["objets"]:
        pid = o["id"]
        for ch in ATTENDUS.get(o["categorie"], []):
            if o.get(ch) in (None, "", [], {}): out.append(("manque", pid, f"{ch} absent"))
        if o.get("statut") not in STATUTS: out.append(("erreur", pid, f"statut inconnu : {o.get('statut')}"))
        if o["categorie"] == "stand" and o.get("type") not in TYPES_STAND: out.append(("erreur", pid, f"type de stand inconnu : {o.get('type')} (attendu {', '.join(TYPES_STAND)})"))
        d = o.get("dimensions_m")
        if isinstance(d, dict):
            for k in ("l", "h", "p"):
                v = d.get(k)
                if v is not None and (not isinstance(v, (int, float)) or v <= 0 or v > 200): out.append(("erreur", pid, f"dimensions_m.{k} = {v} suspect (mètres attendus)"))
        for k in ("poids_kg", "puissance_w"):
            v = o.get(k)
            if v is not None and (not isinstance(v, (int, float)) or v < 0): out.append(("erreur", pid, f"{k} = {v} invalide"))
            if k == "poids_kg" and isinstance(v, (int, float)) and 0 < v < 0.5: out.append(("doute", pid, f"poids {v} kg : tonnes ou grammes ?"))
        if "source" not in o: out.append(("manque", pid, "source absente"))
        cle = (o["categorie"], slug(o["nom"]))
        if cle in vus: out.append(("doublon", pid, f"même nom que {vus[cle]} — à relier ?"))
        vus[cle] = pid
    return out

def cmd_valider(a):
    reg = charger(); pb = problemes(reg)
    if not pb: print("registre valide :", len(reg["objets"]), "objets"); return
    for niv, pid, msg in pb: print(f"  {niv:8s} {pid:14s} {msg}")
    print(f"{len(pb)} point(s) — {sum(1 for p in pb if p[0]=='manque')} manque(s), {sum(1 for p in pb if p[0]=='doublon')} doublon(s)")

# --------------------------------------------------------------- inventaire
def cmd_inventaire(a):
    reg = charger(); objs = reg["objets"]; pb = problemes(reg)
    L = [f"# Inventaire — {reg.get('evenement') or 'événement'}", "",
         f"_Généré le {datetime.date.today().isoformat()} depuis `evenement/registre.json` ({len(objs)} objets). Ne pas éditer à la main._", ""]
    def num(o, k): v = o.get(k); return v if isinstance(v, (int, float)) else 0
    mat = [o for o in objs if o["categorie"] in ("materiel", "structure") and o.get("statut") != "abandonne"]
    kw = sum(num(o, "puissance_w") * (o.get("quantite") or 1) for o in mat) / 1000
    kg = sum(num(o, "poids_kg") * (o.get("quantite") or 1) for o in mat)
    L += ["## Totaux", "", "| | |", "|---|---|",
          f"| Matériel et structures (lignes) | {len(mat)} |",
          f"| Puissance électrique cumulée | **{kw:.1f} kW** ({'inconnue pour ' + str(sum(1 for o in mat if o.get('puissance_w') is None)) + ' ligne(s)' if any(o.get('puissance_w') is None for o in mat) else 'complète'}) |",
          f"| Masse cumulée | **{kg:,.0f} kg** |".replace(",", " "),
          f"| Stands | {sum(1 for o in objs if o['categorie']=='stand')} |",
          f"| Personnes (rôles) | {sum((o.get('quantite') or 1) for o in objs if o['categorie']=='personne')} |",
          f"| Contraintes actives | {sum(1 for o in objs if o['categorie']=='contrainte' and o.get('statut')!='abandonne')} |",
          f"| Points à régler (valider) | {len(pb)} |", ""]
    if kw: L += [f"Ordre de grandeur alimentation : **{kw:.0f} kW → {'63 A tri' if kw < 36 else '125 A tri' if kw < 72 else 'plusieurs départs / groupe'}** (sans marge). Vérifier avec le registre à jour.", ""]
    for cat in CATEGORIES:
        lst = [o for o in objs if o["categorie"] == cat]
        if not lst: continue
        L += [f"## {cat.capitalize()} ({len(lst)})", "", "| id | type | nom | qté | dims (m) | kg | W | statut | source |", "|---|---|---|---|---|---|---|---|---|"]
        for o in sorted(lst, key=lambda o: o["id"]):
            d = o.get("dimensions_m") or {}
            dims = "×".join(str(d.get(k, "?")) for k in ("l", "h", "p")) if d else ""
            L.append(f"| `{o['id']}` | {o.get('type','')} | {o['nom']} | {o.get('quantite','')} | {dims} | {o.get('poids_kg','') if o.get('poids_kg') is not None else '?'} | {o.get('puissance_w','') if o.get('puissance_w') is not None else '?'} | {o.get('statut','')} | {o.get('source',{}).get('entree','—')} |")
        L.append("")
    if pb:
        L += ["## À régler", ""] + [f"- **{pid}** — {msg} _({niv})_" for niv, pid, msg in pb] + [""]
    os.makedirs(os.path.dirname(INV), exist_ok=True)
    open(INV, "w", encoding="utf-8").write("\n".join(L))
    print(f"{INV} — {len(objs)} objets, {kw:.1f} kW, {kg:.0f} kg, {len(pb)} point(s) à régler")

# ------------------------------------------------------- vers-implantation
def cmd_vers_implantation(a):
    reg = charger()
    if not os.path.exists(IMPL): sys.exit(f"{IMPL} introuvable")
    impl = json.load(open(IMPL, encoding="utf-8")); chang = []
    spat = [o for o in reg["objets"] if o.get("implantation") and o.get("statut") != "abandonne"]
    # village : les stands groupés, dans l'ordre
    stands = sorted([o for o in spat if o["implantation"].get("groupe") == "village"], key=lambda o: o["implantation"].get("ordre", 999))
    if stands:
        nouveaux = [{"nom": o["nom"], "type": o.get("type", "asso")} for o in stands]
        if nouveaux != impl["village"]["stands"]: impl["village"]["stands"] = nouveaux; chang.append(f"village : {len(nouveaux)} stands")
    # projecteurs : lumens / TR depuis le registre si renseignés
    vps = [o for o in spat if o["implantation"].get("groupe") == "projecteurs"]
    if vps:
        o = vps[0]; sp = o.get("specifique", {})
        for p in impl["projecteurs"]:
            if sp.get("lumens") and p["lumens"] != sp["lumens"]: p["lumens"] = sp["lumens"]; chang.append(f"{p['nom']} : {sp['lumens']} lm")
    # positionnés : totems, wash, obstacles (espaces) → voisins
    totems = [o for o in spat if o["implantation"].get("element") == "SM_Totem"]
    if totems:
        impl["lumieres"]["totems"] = [{"x": o["implantation"]["x"], "z": o["implantation"]["z"], "h": o.get("dimensions_m", {}).get("h", 5.5)} for o in totems]; chang.append(f"totems : {len(totems)}")
    obst = [o for o in reg["objets"] if o["categorie"] == "espace" and o.get("position_m") and o.get("hauteur_m")]
    if obst:
        vois = [v for v in impl["projet"]["voisins"] if not v.get("depuis_registre")]
        for o in obst:
            p = o["position_m"]; r = o.get("rayon_m", 0.5)
            vois.append({"nom": o["nom"], "x0": p["x"] - r, "x1": p["x"] + r, "z0": p["z"] - r, "z1": p["z"] + r, "h": o["hauteur_m"], "depuis_registre": o["id"]})
        impl["projet"]["voisins"] = vois; chang.append(f"obstacles depuis le registre : {len(obst)}")
    if chang:
        json.dump(impl, open(IMPL, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("implantation.json mis à jour :", "; ".join(chang)); print("→ relancer unreal/generer_projet_unreal.py, puis assembler_scene.py dans Unreal")
    else: print("implantation.json déjà à jour")

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ajouter"); g = s.add_mutually_exclusive_group(required=True); g.add_argument("--json"); g.add_argument("--fichier")
    s.add_argument("--remplacer", action="store_true"); s.set_defaults(f=cmd_ajouter)
    s = sub.add_parser("chercher"); s.add_argument("mots", nargs="+"); s.set_defaults(f=cmd_chercher)
    s = sub.add_parser("lister"); s.add_argument("--categorie"); s.set_defaults(f=cmd_lister)
    s = sub.add_parser("valider"); s.set_defaults(f=cmd_valider)
    s = sub.add_parser("inventaire"); s.set_defaults(f=cmd_inventaire)
    s = sub.add_parser("vers-implantation"); s.set_defaults(f=cmd_vers_implantation)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
