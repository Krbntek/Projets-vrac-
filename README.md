# Projets-vrac-
## Mapping de façade

- **[`outils/calculateur-mapping.html`](outils/calculateur-mapping.html)** —
  calculateur de dimensionnement (éclairement, optique, pavage, composition).
  Générique : il sert à tous les chantiers. Source unique, à ne pas dupliquer.
- **[`outils/demo-evenement.html`](outils/demo-evenement.html)** — la **démo animée**
  de la soirée (16 h → 2 h) pour la mairie : ciel, extinction, foule, village, show,
  caméra plan-séquence, enregistrement vidéo direct.
- **[`outils/implantation-3d.html`](outils/implantation-3d.html)** —
  maquette 3D de l'implantation : façade, place, projecteurs, lasers, régie,
  vue de dessus, et contrôle géométrique de la sécurité laser.
- **[`unreal/`](unreal/)** — le plan en projet **Unreal Engine 5** : un fichier 3D par
  élément (GLB + OBJ), scène complète avec lumières, script d'assemblage du niveau.
  `unreal/implantation.json` est la source commune au visualiseur et à Unreal.
- **[`evenement/`](evenement/)** — le registre d'objets de l'événement (matériel,
  stands, personnes-rôles, contraintes, données) et l'inventaire généré.
- **[`.claude/skills/flux-evenement/`](.claude/skills/flux-evenement/)** — la skill
  qui accueille les dépôts en vrac (devis, slides, photos, open data) et les
  transforme en objets du registre, puis les propage au plan.
- **[`.claude/skills/mapping-facade/`](.claude/skills/mapping-facade/)** —
  la méthode complète : relevé photogrammétrique, génération d'élévation SVG,
  calculs d'optique et de puissance, config Resolume/MadMapper, autorisations.
- **[`mapping-basilique-saint-denis/`](mapping-basilique-saint-denis/)** —
  étude de cas : façade occidentale de la basilique Saint-Denis.
