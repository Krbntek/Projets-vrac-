# Exports — ce qu'on envoie, ce qu'on imprime

Tout ce dossier se régénère depuis le dépôt ; rien n'est à éditer à la main dans les
fichiers produits.

| Fichier | Quoi | Pour qui |
|---|---|---|
| `dossier-technique.html` / `.pdf` | le dossier complet : présentation, implantation cotée, photos heure par heure, sécurité, puissance et jauges, synoptiques son · lumière · vidéo · captation · électricité, câbles, tour Layher, 14 points à vérifier, inventaire, annexes | mairie, préfecture, commission de sécurité, prestataires |
| `fiche-declaration.html` / `.pdf` | 3 pages : identification, nature, jauge, dispositif en quelques lignes, pièces jointes — **avec des champs « à compléter »** | la déclaration et les premiers mails |
| `plan-implantation.html` / `.pdf` | les cotes de chaque ensemble et les vues | monteurs, loueurs, Ville |
| `inventaire-materiel.html` / `.pdf` | le registre en tableaux + nomenclature Layher | devis, loueurs |
| `demo-soiree.mp4` | la démo animée rendue image par image, 16 h → 2 h en 60 s, 1280 × 720 | mails, présentation |
| `photos/*.jpg` | 15 vues de la maquette, nommées par phase ou par sujet | dossiers, mails |

Les versions HTML s'ouvrent partout, sans 3D ni réseau ; les PDF sont en A4 avec en-tête,
pied de page numéroté et un sommaire.

## Régénérer

```
python3 exports/generer_exports.py          # HTML + PDF (PDF via Chromium / Playwright : node)
python3 exports/generer_exports.py --sans-pdf
```

Photos et vidéo : la démo se rend en navigateur sans écran (Chromium + Playwright, script
`exports/rendre_video.js`) :

```
node exports/rendre_video.js                # photos/*.jpg + images de la vidéo, puis ffmpeg → demo-soiree.mp4
```

(≈ 1 s par image sur une machine avec GPU, bien plus lent en rendu logiciel.) Depuis la
démo ouverte dans un navigateur, les boutons **⤓ Image** et **⏺ Enregistrer la vidéo**
donnent la même chose en direct (MP4 ou WebM selon le navigateur ; dans claude.ai, la page
demande confirmation avant d'enregistrer le fichier).

## Réorganiser un dossier

- l'**ordre et la composition** de chaque document sont dans `dossier/plan.json` : une
  ligne par section, déplacer une ligne suffit ;
- le **texte** des sections est dans `dossier/sections/*.md` (Markdown simple : titres,
  listes, tableaux, gras) ;
- les sections `synoptiques` viennent de `evenement/SYNOPTIQUES.md` (titre `##` cité par
  son début) : un seul texte source pour le dossier et le dépôt ;
- `inventaire` lit `evenement/registre.json` ; `photos` prend les noms de `photos/` et
  leurs légendes dans `plan.json` ;
- les schémas Mermaid deviennent des tableaux « De → Liaison → Vers » pour rester lisibles à
  l'impression ; le code Mermaid reste visible (dépliable) dans la version HTML.

Les coordonnées et dimensions du dossier (`sections/implantation.md`) sont recopiées de
`unreal/implantation.json` : après un déplacement dans `outils/implantation-3d.html`,
exporter le JSON, le mettre dans `unreal/`, puis mettre à jour ce tableau.
