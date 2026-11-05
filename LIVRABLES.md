# Livrables — où est quoi

| Je veux… | Fichier | Comment l'ouvrir |
|---|---|---|
| **Envoyer un dossier** (mairie, préfecture, prestataires) | `exports/dossier-technique.pdf`, `exports/fiche-declaration.pdf` (champs à compléter), `exports/plan-implantation.pdf`, `exports/inventaire-materiel.pdf` | PDF A4, n'importe quel lecteur |
| La même chose en page web simple | `exports/*.html` (mêmes noms) | double-clic, sans réseau ni 3D |
| **La vidéo de la démo** | `exports/demo-soiree.mp4` (60 s, 1280 × 720) | VLC, lecteur vidéo, pièce jointe de mail |
| **Les photos** | `exports/photos/01…15-*.jpg` | légendes dans `exports/dossier/plan.json` |
| **Tester la démo animée en local** | `outils/demo-evenement.html` | double-clic dans Chrome ou Firefox (charge three.js depuis le réseau) ; en ligne : https://claude.ai/artifact/QpJGtbyad4SqdgK5KoQqnQ |
| **Tester des configurations** (studio : catalogue, quantités possédées / à louer, souris, contrôles, PNG, JSON v3) | `outils/studio-implantation.html` | double-clic ; en ligne : https://claude.ai/artifact/879PsFAU4oFvcnjRTDd2QW |
| **Déplacer les éléments du plan complet** | `outils/implantation-3d.html` | double-clic ; glisser-déposer, variantes, Exporter JSON ; en ligne : https://claude.ai/artifact/71WAU7uw4JiS5Rf54EmmNE |
| Calculer un autre mapping | `outils/calculateur-mapping.html` | double-clic |
| **Ouvrir dans Unreal Engine 5** | `unreal/MappingSaintDenis/MappingSaintDenis.uproject` puis *Tools → Execute Python Script* → `Content/Python/assembler_scene.py` | mode d'emploi : `unreal/README.md` |
| Les éléments 3D un par un | `unreal/MappingSaintDenis/Content/Import/Elements/SM_*.glb` (+ `.obj`) | import dans Unreal, Blender, Cinema 4D… |
| La source commune des positions | `unreal/implantation.json` | export JSON du visualiseur → remplacer ce fichier |
| Le dossier technique source (synoptiques Mermaid) | `evenement/SYNOPTIQUES.md` | GitHub le rend avec les schémas |
| Le registre du matériel | `evenement/registre.json`, `evenement/INVENTAIRE.md` | skill `flux-evenement` |
| L'élévation SVG de la façade | `mapping-basilique-saint-denis/*.svg` | MadMapper, Resolume, Illustrator |

Régénérer les exports : `python3 exports/generer_exports.py` (HTML + PDF) et `node exports/rendre_video.js` (photos + vidéo). Détails : `exports/README.md`.
