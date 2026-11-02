# Projet Unreal — plan d'implantation 3D

Le plan d'implantation (façade, parvis, bloc central, village, sono, lumières)
sous forme de **fichiers 3D que tu charges dans Unreal Engine 5** pour le retravailler
élément par élément.

```
unreal/
├── implantation.json              ← LA SOURCE (export JSON du visualiseur HTML)
├── generer_projet_unreal.py       ← fabrique tous les fichiers ci-dessous
└── MappingSaintDenis/
    ├── MappingSaintDenis.uproject ← à ouvrir avec Unreal 5.3+ (5.4 conseillé)
    ├── Config/
    └── Content/
        ├── Import/
        │   ├── Scene/Implantation.glb         scène complète, hiérarchie + 8 lumières
        │   ├── Elements/SM_*.glb  (+ .obj)    un fichier par élément, à l'origine
        │   └── placement.json                 où va chaque instance, en cm, repère Unreal
        └── Python/assembler_scene.py          assemble le niveau dans l'éditeur
```

## Ouvrir et assembler (5 minutes)

1. **Ouvre** `MappingSaintDenis.uproject` (double-clic ou Epic Launcher → *Browse*).
   Au premier lancement Unreal propose de créer le dossier `Intermediate` : accepte.
2. Vérifie que **Python Editor Script Plugin** est actif (*Edit → Plugins*, il l'est par
   défaut dans le `.uproject`). Redémarre si demandé.
3. **Tools → Execute Python Script…** → `Content/Python/assembler_scene.py`.
   Le script importe les 31 éléments en Static Mesh dans `/Game/Implantation/Meshes`,
   crée le niveau `/Game/Maps/Implantation`, place les 41 acteurs rangés par dossier
   dans l'Outliner (`00_Site`, `01_Facade`, `02_Bloc_central`, `03_Village`, `04_Sono`,
   `05_Lumieres`, `06_Faisceaux`, `07_Cameras`), ajoute **8 SpotLights en lumens**
   (40 000 lm pour chaque VP, cône calculé depuis le rapport d'optique), un SkyLight de
   nuit et deux caméras (public à 1,70 m ; bloc central).
4. Tu as un niveau où **chaque objet est un acteur séparé** avec son propre Static Mesh :
   déplace, remplace, rhabille.

**Sans script** : *File → Import Into Level…* → `Content/Import/Scene/Implantation.glb`.
Tout arrive d'un coup, hiérarchie et lumières comprises (`KHR_lights_punctual`).
Pratique pour voir vite, moins pour retravailler.

## Ce que représentent les éléments

| Élément | Quoi | Mesure |
|---|---|---|
| `SM_Facade` | silhouette extrudée + ouvertures en creux + rosace | 32,5 × 60,1 m, 3 m d'épaisseur — relevé photogrammétrique ± 3-5 % |
| `SM_Nef` | volume de la nef derrière la façade | 32,5 × 24 × 105 m, indicatif |
| `SM_Voisin_1..4` | bâtiments autour de la place | **volumes à l'estime, à remplacer par le cadastre** |
| `SM_Sol`, `SM_ZonePublic` | parvis, zone public 60 × 54 m | |
| `SM_PlateformeVP` | échafaudage 9 × 3 m à 10 m, garde-corps, bâche | |
| `SM_Regie` | conteneur 20' : vitre côté façade, porte côté village, clim | 6,06 × 2,44 × 2,59 m |
| `SM_Tonnelle_<type>` | tonnelle 3 × 3, toit coloré par type, comptoir | prévention, secours, accueil, buvette, asso |
| `SM_PA_Stack` | 2 subs + line array sur mât | 6,5 m |
| `SM_Totem`, `SM_WashFacade` | mâts lumière 5,5 m, wash au sol | |
| `SM_Projecteur`, `SM_Laser` | les machines | |
| `SM_ConeVP_n`, `SM_FaisceauLaser_n`, `SM_FaisceauTotem_n`, `SM_FaisceauWash_n` | **volumes d'étude** translucides : ce que chaque appareil éclaire. Pas d'ombre, à masquer pour un rendu « beau » | |
| `SM_Sono_Couverture` | secteurs de couverture des PA au sol | 90°, 62 m, visée 10° vers l'intérieur |

Les matériaux sont des PBR simples (couleur, rugosité, métal) nommés `M_Pierre`,
`M_Regie`, `M_ConeVP`… : à remplacer par les tiens.

## Repères et unités

- `implantation.json` : **mètres**, X = axe de la façade (0 au centre, + côté cour),
  Y = hauteur, Z = recul depuis le plan de la façade (0 = façade, 70 = plateforme VP).
- Les GLB sont en mètres, Y vers le haut (norme glTF). L'importeur Unreal convertit en
  cm, Z vers le haut, **sans rien toucher**. Laisse *Uniform Scale* à 100 (défaut).
- `placement.json` est déjà en cm, repère Unreal : X avant = recul, Y droite = axe
  façade, Z = hauteur. Façade en X = 0, plateforme VP en X = 7 000.

## Modifier l'implantation

Le cycle est toujours le même, dans ce sens :

1. dans `outils/implantation-3d.html` : déplace, ajoute, renomme → **Exporter JSON** ;
2. remplace `unreal/implantation.json` par le fichier exporté ;
3. `python3 generer_projet_unreal.py` (dépendances : `pip install trimesh shapely numpy mapbox_earcut`) ;
4. dans Unreal, relance `assembler_scene.py` : il vide les acteurs tagués `implantation`
   et les repose. **Ce que tu as ajouté à la main dans le niveau est conservé**, ce que
   le script avait posé est remplacé.

Si tu retravailles un `SM_*` directement dans Unreal, fais-le sur une **copie** sous un
autre nom, sinon le prochain import l'écrase.

## La démo animée (pour la mairie)

Deux versions du même scénario (16 h → 2 h : montage, village, crépuscule, extinction,
mapping, lasers, sortie), avec les **mêmes paramètres** dans
`Content/Import/demo_params.json` — matériaux (couleur, rugosité, métal, relief,
émission des fenêtres et vitraux), soleil (élévation, température de couleur, ciel),
lumières (lumens, Kelvin, cônes), caméra (plan-séquence), foule :

- **`outils/demo-evenement.html`** — autonome, dans un navigateur, textures
  procédurales, bouton *Enregistrer la vidéo* (WebM) et *Image* (PNG). C'est la
  version à montrer tout de suite, vérifiée en rendu.
- **`Content/Python/demo_sequence.py`** — à lancer après `assembler_scene.py` :
  crée les matériaux à paramètres dans `/Game/Implantation/Materials`, le soleil
  + Sky Atmosphere + nuages + brouillard volumétrique (ce qui rend les cônes et
  faisceaux visibles dans l'air), les candélabres et lumières de stands, puis la
  **Level Sequence `Seq_Soiree`** (100 s à 30 i/s, 1 h = 10 s) : rotation et
  intensité du soleil, allumage des groupes par phase, visibilité des volumes
  d'étude, caméra CineCamera sur le plan-séquence. Rendu vidéo : *Movie Render
  Queue* sur `Seq_Soiree`. Non exécuté dans Unreal ici (voir avertissement ci-dessous).

L'image du mapping : dans la démo HTML c'est une toile procédurale animée
(nappes, lignes d'architecture, rosace qui pulse). Dans Unreal, `M_ImageMapping`
attend un **Render Target ou un Media Player** : branche ta vidéo de contenu dessus,
masquée au corps de façade (la tour reste en wash).

## Ce qui n'est pas là

- Pas de `.uasset` ni de `.umap` versionnés : ils sont produits par l'éditeur au
  premier assemblage. Unreal les génère en quelques secondes, ça évite des binaires
  dans Git.
- Pas de texture : les matériaux sont des couleurs. La façade n'a pas sa photo plaquée.
- Les voisins sont des boîtes. Pour un rendu crédible du parvis, prends le cadastre
  (`cadastre.data.gouv.fr`) ou le modèle 3D de l'IGN (`geoservices.ign.fr`, *BD TOPO*
  bâti 3D) — voir la skill `flux-evenement`, référence `sources-ouvertes.md`.

## Vérifications faites

Le GLB de scène a été rechargé par un lecteur glTF indépendant (three.js r128) : 41
maillages, 8 lumières, positions conformes au visualiseur. Les GLB d'éléments sont
étanches (`SM_Facade` : 32,5 × 60,1 × 3,1 m). **Le projet n'a pas été ouvert dans
Unreal lui-même** — pas de licence Unreal dans l'environnement où il a été fabriqué.
Le `.uproject`, l'assembleur Python et les réglages suivent l'API officielle
(`unreal.AssetImportTask`, `EditorActorSubsystem`, `LightUnits.LUMENS`), mais le premier
lancement peut demander un ajustement ; si le script bloque, l'import `Into Level` du
GLB de scène est la voie sans risque.
