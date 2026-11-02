#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_exports.py — fabrique les exports « dossier » de l'événement :

  exports/<document>.html   version HTML simple, lisible partout, sans 3D
  exports/<document>.pdf    la même chose en PDF A4 (via Chromium / Playwright : node rendre_pdf.js)

Le contenu et l'ORDRE des documents sont décrits dans exports/dossier/plan.json :
un document = une liste de sections ; une section vient soit d'un fichier Markdown
(exports/dossier/sections/*.md), soit d'une section de evenement/SYNOPTIQUES.md, soit du
registre (inventaire), soit de photos (exports/photos). Pour réorganiser un dossier,
on déplace des lignes dans plan.json ou on édite un .md ; on relance ce script.

  python3 exports/generer_exports.py            # tout
  python3 exports/generer_exports.py --sans-pdf # HTML seulement

Les schémas Mermaid des synoptiques sont convertis en tableaux « De → Vers » pour rester
lisibles à l'impression (le code Mermaid reste visible dans la version HTML, dépliable).
"""
import json, os, re, sys, subprocess, datetime, html

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PLAN = os.path.join(ICI, "dossier", "plan.json")
SECTIONS = os.path.join(ICI, "dossier", "sections")
SYNO = os.path.join(RACINE, "evenement", "SYNOPTIQUES.md")
REG = os.path.join(RACINE, "evenement", "registre.json")
PHOTOS = os.path.join(ICI, "photos")

# ----------------------------------------------------------------- markdown minimal
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"&lt;(https?://[^&\s]+)&gt;", r'<a href="\1">\1</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<i>\1</i>", t)
    return t

def mermaid_table(code):
    """flowchart Mermaid → lignes (de, liaison, vers) avec les libellés des nœuds."""
    noms, aretes = {}, []
    def label(brut):
        brut = brut.strip().strip('"')
        return re.sub(r"<br\s*/?>", " · ", brut)
    for ligne in code.splitlines():
        l = ligne.strip()
        if not l or l.startswith(("flowchart", "graph", "subgraph", "end", "%%")): continue
        for m in re.finditer(r'([A-Za-z0-9_]+)\s*\[\s*"?(.*?)"?\s*\]', l):
            noms[m.group(1)] = label(m.group(2))
        if "--" not in l: continue
        chaine = re.split(r"\s*(-->|-\.->|-\.-|---)\s*", l)
        # chaine : [A, fleche, (|label| B), fleche, ...]
        i = 0
        while i + 2 < len(chaine):
            gauche, fleche, droite = chaine[i], chaine[i + 1], chaine[i + 2]
            lab = ""
            m = re.match(r'\|\s*"?(.*?)"?\s*\|\s*(.*)', droite)
            if m: lab, droite = label(m.group(1)), m.group(2)
            g_ids = [re.match(r"([A-Za-z0-9_]+)", x.strip()).group(1) for x in gauche.split("&") if re.match(r"\s*[A-Za-z0-9_]+", x)]
            d_ids = [re.match(r"([A-Za-z0-9_]+)", x.strip()).group(1) for x in droite.split("&") if re.match(r"\s*[A-Za-z0-9_]+", x)]
            for a in g_ids:
                for b in d_ids: aretes.append((a, lab, b, fleche))
            chaine[i + 2] = droite; i += 2
    if not aretes: return "<pre>" + html.escape(code) + "</pre>"
    out = ['<table class="syno"><tr><th>De</th><th>Liaison</th><th>Vers</th></tr>']
    for a, lab, b, fl in aretes:
        na, nb = noms.get(a, a), noms.get(b, b)
        out.append(f'<tr><td>{html.escape(na)}</td><td class="lien">{html.escape(lab) or ("(option)" if "." in fl else "")}</td><td>{html.escape(nb)}</td></tr>')
    out.append("</table>")
    out.append('<details class="code"><summary>code Mermaid (pour reprendre le schéma)</summary><pre>' + html.escape(code) + "</pre></details>")
    return "\n".join(out)

def md2html(texte, niveau_base=0):
    """Convertit un Markdown simple (titres, paragraphes, listes, tableaux, blocs ``` ) en HTML."""
    lignes = texte.splitlines(); out = []; i = 0; para = []
    def flush():
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
    while i < len(lignes):
        l = lignes[i]
        if l.startswith("```"):
            flush(); lang = l[3:].strip(); bloc = []; i += 1
            while i < len(lignes) and not lignes[i].startswith("```"): bloc.append(lignes[i]); i += 1
            i += 1
            out.append(mermaid_table("\n".join(bloc)) if lang == "mermaid" else "<pre>" + html.escape("\n".join(bloc)) + "</pre>"); continue
        m = re.match(r"^(#{1,5})\s+(.*)", l)
        if m:
            flush(); n = min(5, len(m.group(1)) + niveau_base); out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); i += 1; continue
        if re.match(r"^\s*[-*]\s+", l) or re.match(r"^\s*\d+\.\s+", l):
            flush(); ordonne = bool(re.match(r"^\s*\d+\.", l)); items = []
            while i < len(lignes) and (re.match(r"^\s*[-*]\s+", lignes[i]) or re.match(r"^\s*\d+\.\s+", lignes[i]) or (lignes[i].startswith("  ") and items)):
                if re.match(r"^\s*([-*]|\d+\.)\s+", lignes[i]): items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lignes[i]))
                else: items[-1] += " " + lignes[i].strip()
                i += 1
            tag = "ol" if ordonne else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        if l.startswith("|"):
            flush(); rows = []
            while i < len(lignes) and lignes[i].startswith("|"): rows.append(lignes[i]); i += 1
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            cells = [c for c in cells if not all(re.match(r"^:?-{2,}:?$", x) for x in c)]
            if cells:
                t = ["<table>", "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells[0]) + "</tr>"]
                for r in cells[1:]: t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
                t.append("</table>"); out.append("\n".join(t))
            continue
        if re.match(r"^-{3,}\s*$", l): flush(); out.append("<hr>"); i += 1; continue
        if not l.strip(): flush(); i += 1; continue
        para.append(l.strip()); i += 1
    flush(); return "\n".join(out)

# ----------------------------------------------------------------- sources
def section_synoptiques(titre_prefixe):
    """extrait une section '## <prefixe>…' de SYNOPTIQUES.md (jusqu'au prochain ##)."""
    txt = open(SYNO, encoding="utf-8").read().splitlines(); out = []; dedans = False
    for l in txt:
        if l.startswith("## "):
            if dedans: break
            dedans = l[3:].strip().startswith(titre_prefixe)
            if dedans: out.append("## " + l[3:].strip()); continue
        if dedans: out.append(l)
    if not out: return f"## {titre_prefixe}\n\n_(section introuvable dans SYNOPTIQUES.md)_"
    return "\n".join(out)

def inventaire_html():
    reg = json.load(open(REG, encoding="utf-8")); objs = [o for o in reg["objets"] if o.get("statut") != "abandonne"]
    cats = [("materiel", "Matériel"), ("structure", "Structures"), ("stand", "Stands"), ("personne", "Personnes (rôles)"), ("contrainte", "Contraintes"), ("document", "Documents")]
    out = [f"<p>Extrait du registre <code>evenement/registre.json</code> ({len(objs)} objets actifs). Les quantités, poids et puissances marqués « à confirmer » sont des estimations ou des valeurs de classe de matériel.</p>"]
    for cat, titre in cats:
        lst = sorted([o for o in objs if o["categorie"] == cat], key=lambda o: o["id"])
        if not lst: continue
        out.append(f"<h3>{titre} ({len(lst)})</h3><table><tr><th>Désignation</th><th>Qté</th><th>Dimensions (m)</th><th>kg</th><th>W</th><th>Fournisseur</th><th>Statut</th></tr>")
        for o in lst:
            d = o.get("dimensions_m") or {}; dims = " × ".join(str(d.get(k)) for k in ("l", "h", "p") if d.get(k) is not None)
            out.append(f"<tr><td>{html.escape(o['nom'])}</td><td>{o.get('quantite', '')}</td><td>{dims}</td><td>{o.get('poids_kg') if o.get('poids_kg') is not None else '?'}</td><td>{o.get('puissance_w') if o.get('puissance_w') is not None else '?'}</td><td>{html.escape(str(o.get('fournisseur', '') or ''))}</td><td>{o.get('statut', '').replace('_', ' ')}</td></tr>")
        out.append("</table>")
    return "\n".join(out)

def photos_html(noms, legendes):
    out = ['<div class="photos">']
    for n in noms:
        f = os.path.join(PHOTOS, n + ".jpg")
        if not os.path.exists(f): out.append(f'<figure class="manque"><div>photo manquante : {html.escape(n)}</div></figure>'); continue
        out.append(f'<figure><img src="photos/{n}.jpg" alt="{html.escape(n)}"><figcaption>{html.escape(legendes.get(n, n.replace("-", " ")[3:]))}</figcaption></figure>')
    out.append("</div>"); return "\n".join(out)

# ----------------------------------------------------------------- assemblage
CSS = """
:root{--txt:#1d2228;--dim:#5b6470;--line:#d5dae0;--acc:#b8690f;--fond:#f6f1e8}
*{box-sizing:border-box} html{font-size:15px} body{margin:0;color:var(--txt);font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.5;background:#fff}
.page{max-width:860px;margin:0 auto;padding:28px 32px 60px}
header.doc{border-bottom:3px solid var(--acc);padding-bottom:12px;margin-bottom:20px}
header.doc h1{font-size:30px;margin:0 0 4px;letter-spacing:-.01em} header.doc .sous{color:var(--dim);font-size:15px} header.doc .meta{font-size:12.5px;color:var(--dim);margin-top:8px}
nav.toc{background:var(--fond);border-radius:10px;padding:12px 18px;margin:0 0 24px;font-size:13.5px} nav.toc h2{margin:0 0 6px;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--acc)} nav.toc ol{margin:0;padding-left:20px} nav.toc li{margin:2px 0}
section.sec{margin:0 0 30px} section.sec>h1{font-size:22px;border-left:5px solid var(--acc);padding-left:12px;margin:28px 0 12px}
h2{font-size:17px;margin:20px 0 8px} h3{font-size:14.5px;margin:16px 0 6px;color:var(--dim);text-transform:uppercase;letter-spacing:.05em} h4{font-size:14px;margin:12px 0 4px}
p{margin:6px 0 10px} ul,ol{margin:4px 0 10px;padding-left:22px} li{margin:2px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:6px 0 14px} th,td{border:1px solid var(--line);padding:5px 7px;vertical-align:top;text-align:left} th{background:var(--fond);font-weight:600} tr:nth-child(even) td{background:#fafafa}
table.syno td.lien{color:var(--dim);font-style:italic;white-space:nowrap}
code{background:#f0f0f0;padding:1px 4px;border-radius:3px;font-size:.92em} pre{background:#f4f4f4;border:1px solid var(--line);border-radius:6px;padding:8px 10px;font-size:11.5px;overflow:auto;white-space:pre-wrap}
details.code summary{font-size:12px;color:var(--dim);cursor:pointer}
.photos{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:8px 0 16px} figure{margin:0;break-inside:avoid} figure img{width:100%;border-radius:6px;border:1px solid var(--line)} figcaption{font-size:12px;color:var(--dim);margin-top:3px} figure.manque div{border:1px dashed var(--line);padding:30px;text-align:center;color:var(--dim);font-size:12px}
.encart{background:var(--fond);border-left:4px solid var(--acc);padding:8px 12px;border-radius:0 6px 6px 0;margin:10px 0} .a-completer{background:#fff3c4;padding:0 4px;border-radius:3px}
footer.doc{margin-top:40px;border-top:1px solid var(--line);padding-top:10px;font-size:12px;color:var(--dim)}
@media print{html{font-size:11.5pt} .page{max-width:none;padding:0} section.sec{break-before:page} section.sec:first-of-type{break-before:auto} nav.toc{break-after:page} h1,h2,h3{break-after:avoid} figure{break-inside:avoid} tr{break-inside:avoid} thead{display:table-header-group} details.code{display:none} a{color:inherit;text-decoration:none}}
"""

def construire(doc, plan):
    titre, sous = doc["titre"], doc.get("sous_titre", "")
    date = plan.get("date", datetime.date.today().isoformat()); version = plan.get("version", "")
    corps, toc = [], []
    for k, s in enumerate(doc["sections"], 1):
        if "md" in s:
            txt = open(os.path.join(SECTIONS, s["md"]), encoding="utf-8").read()
            m = re.match(r"^#\s+(.*)", txt.strip()); t = s.get("titre") or (m.group(1) if m else s["md"])
            if m: txt = txt.strip().split("\n", 1)[1] if "\n" in txt.strip() else ""
            contenu = md2html(txt, niveau_base=1)
        elif "synoptiques" in s:
            txt = section_synoptiques(s["synoptiques"]); t = s.get("titre") or re.sub(r"^\d+\.\s*", "", txt.splitlines()[0][3:])
            contenu = md2html("\n".join(txt.splitlines()[1:]), niveau_base=1)
        elif "inventaire" in s:
            t = s.get("titre", "Inventaire du matériel"); contenu = inventaire_html()
        elif "photos" in s:
            t = s.get("titre", "Photos de la maquette"); contenu = md2html(s.get("intro", ""), 1) + photos_html(s["photos"], plan.get("legendes_photos", {}))
        else: continue
        toc.append(f'<li><a href="#s{k}">{html.escape(t)}</a></li>')
        corps.append(f'<section class="sec" id="s{k}"><h1>{k}. {html.escape(t)}</h1>{contenu}</section>')
    meta = " · ".join(x for x in [plan.get("organisateur", ""), f"version {version}" if version else "", date, plan.get("contact", "")] if x)
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(titre)}</title><style>{CSS}</style></head>
<body><div class="page"><header class="doc"><h1>{html.escape(titre)}</h1><div class="sous">{html.escape(sous)}</div><div class="meta">{html.escape(meta)}</div></header>
<nav class="toc"><h2>Sommaire</h2><ol>{''.join(toc)}</ol></nav>
{''.join(corps)}
<footer class="doc">{html.escape(plan.get('pied', 'Document de travail généré depuis le dépôt du projet (exports/generer_exports.py). Les mentions « à compléter » et « à confirmer » sont à traiter avant envoi.'))}</footer></div></body></html>"""

def main():
    sans_pdf = "--sans-pdf" in sys.argv
    plan = json.load(open(PLAN, encoding="utf-8")); faits = []
    for doc in plan["documents"]:
        h = construire(doc, plan); chemin = os.path.join(ICI, doc["fichier"] + ".html")
        open(chemin, "w", encoding="utf-8").write(h); faits.append(chemin)
        if not sans_pdf:
            pdf = os.path.join(ICI, doc["fichier"] + ".pdf")
            r = subprocess.run(["node", os.path.join(ICI, "rendre_pdf.js"), chemin, pdf, f"{doc['titre']} — {plan.get('organisateur', '')}"], capture_output=True, text=True)
            if r.returncode == 0: faits.append(pdf)
            else: print("  PDF non produit pour", doc["fichier"], ":", (r.stderr or r.stdout).strip()[:300])
    for f in faits: print(f"{os.path.relpath(f, RACINE)}  ({os.path.getsize(f)//1024} ko)")

if __name__ == "__main__":
    main()
