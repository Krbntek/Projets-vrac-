# Projet Unreal — plan d'implantation 3D (version 2)

Le plan d'implantation (façade, parvis, tour Layher, régie, podium-catwalk, camion-écran,
village sur les flancs, repos, sono, lumières, câbles, armoires) sous forme de **fichiers 3D
que tu charges dans Unreal Engine 5** pour le retravailler élément par élément.

```
unreal/
├── implantation.json              ← LA SOURCE (schéma v2, export de la démo ou du visualiseur)
├── generer_projet_unreal.py       ← fabrique tous les fichiers ci-dessous
└── MappingSaintDenis/
    ├── MappingSaintDenis.uproject ← compatible Unreal 5.0 à 5.5 (conversion proposée à l'ouverture)
    ├── Config/
    └── Content/
        ├── Import/
        │   ├── Scene/Implantation.glb         scène complète, hiérarchie + 10 lumières
        │   ├── Elements/SM_*.glb  (+ .obj)    48 éléments, chacun à l'origine
        │   ├── placement.json                 64 acteurs, en cm, repère Unreal
        │   └── demo_params.json               paramètres de la démo (phases, matériaux, lumières, caméras)
        └── Python/assembler_scene.py          assemble le niveau dans l'éditeur
                   demo_sequence.py            crée la Level Sequence de la soirée
```

## Ouvrir et assembler (5 minutes)

1. **Ouvre** `MappingSaintDenis.uproject` (double-clic ou Epic Launcher → *Browse*).
   Au premier lancement Unreal propose de créer le dossier `Intermediate` : accepte.
2. Vérifie que **Python Editor Script Plugin** est actif (*Edit → Plugins*, il l'est par
   défaut dans le `.uproject`). Redémarre si demandé.
3. **Tools → Execute Python Script…** → `Content/Python/assembler_scene.py`.
   Le script importe les 48 éléments en Static Mesh dans `/Game/Implantation/Meshes`,
   crée le niveau `/Game/Maps/Implantation`, place les 64 acteurs rangés par dossier
   dans l'Outliner (`00_Site`, `01_Facade`, `02_Bloc_central`, `03_Village`, `04_Sono`,
   `05_Lumieres`, `06_Faisceaux`, `07_Cameras`, `08_Scene_catwalk`, `09_Camion_DJ`,
   `10_Electricite_cables`, `11_Repos_stockage`), ajoute **10 SpotLights en lumens**
   (40 000 lm par VP, 4 totems, 2 wash, 2 projecteurs de scène), un SkyLight de nuit et
   deux caméras.
4. Tu as un niveau où **chaque objet est un acteur séparé** avec son propre Static Mesh :
   déplace, remplace, rhabille.

**Sans script** : *File → Import Into Level…* → `Content/Import/Scene/Implantation.glb`.
Tout arrive d'un coup, hiérarchie et lumières comprises (`KHR_lights_punctual`).

## Ce que représentent les éléments

| Élément | Quoi | Mesure |
|---|---|---|
| `SM_Facade` | silhouette extrudée + ouvertures en creux + rosace | 32,5 × 60,1 m, 3 m d'épaisseur — relevé photogrammétrique ± 3-5 % |
| `SM_Nef`, `SM_Voisin_1..4`, `SM_Sol`, `SM_ZonePublic` | nef, bâtiments voisins (**volumes à l'estime**), parvis, zone public 52 × 54 m | |
| `SM_TourLayher` | tour Allround : 3 travées × 3,07 m, 5 niveaux de 2 m, montants, moises, diagonales, rosettes, planchers acier, planchers à trappe + échelles, garde-corps, plinthes, bâche de toit, 8 lests béton, tronc de câbles | plancher 10,3 m, 12,9 m hors tout |
| `SM_Regie` | conteneur 20' sur praticables (+1,2 m), vitre côté façade, porte + escalier côté tour, sorties de câbles | 6,06 × 2,44 × 2,59 m |
| `SM_Podium` | tête 6 × 4 + catwalk 2,4 × 12 à 1,50 m, garde-corps, 2 escaliers latéraux, bandes LED (`M_LedScene`), jupes, backline, retours | origine au centre de la tête, catwalk vers la façade |
| `SM_Camion` | 20 m³ : cabine, caisse, roues, hayon déployé avec garde-corps, table DJ, retours, écran sur le flanc (`M_Ecran` émissif) | 7,3 + 1,6 m de hayon |
| `SM_Tonnelle_<type>` | tonnelle 3 × 3, toit coloré par type, comptoir côté façade, lests | prévention, secours, accueil, buvette, asso |
| `SM_Repos`, `SM_Stockage`, `SM_BacheRepos` | tonnelle repos 6 × 3 (bancs, table), tonnelle stockage 3 × 3 (flight-cases), bâche opaque 14 m | derrière la tour |
| `SM_SubStack`, `SM_TetesPA`, `SM_FrontFill`, `SM_DelaiTour` | pile de 4 SACH118 ; 4 têtes TP-980 (posées sur les piles extérieures, y = 2,8 m) ; 2 T24N (piles intérieures) ; tour de délai 5 m avec 2 têtes | |
| `SM_Totem`, `SM_WashFacade`, `SM_ProjScene` | totem 5,5 m avec 2 barres + 2 PAR, wash au sol, projecteur de scène sur pied | |
| `SM_Armoire_1..4`, `SM_GroupeElectrogene` | TGBT, coffrets son jardin / cour, coffret lumière · stands, GE 100 kVA (option) | |
| `SM_Cables` | passages de câbles au sol avec bandes jaunes, en coordonnées monde (278 m) | |
| `SM_Projecteur`, `SM_Laser` | les machines | |
| `SM_ConeVP_n`, `SM_FaisceauLaser_n`, `SM_FaisceauTotem_n`, `SM_FaisceauWash_n`, `SM_FaisceauScene_n`, `SM_Sono_Couverture` | **volumes d'étude** translucides : ce que chaque appareil éclaire ou couvre. À masquer pour un rendu « beau » | |

Les matériaux sont des PBR simples nommés `M_Pierre`, `M_Galva`, `M_Deck`, `M_Ecran`,
`M_LedScene`… : à remplacer par les tiens. Les jupes du catwalk (`M_Jaune` sur les faces
latérales) attendent la texture texte « SCÈNE OUVERTE · À VOUS ! » de la démo.

## Repères et unités

- `implantation.json` : **mètres**, X = axe de la façade (0 au centre, + côté cour),
  Y = hauteur, Z = recul depuis le plan de la façade (0 = façade, 70 = tour).
- Les GLB sont en mètres, Y vers le haut (norme glTF). L'importeur Unreal convertit en
  cm, Z vers le haut, **sans rien toucher**. Laisse *Uniform Scale* à 100 (défaut).
- `placement.json` est déjà en cm, repère Unreal : X avant = recul, Y droite = axe
  façade, Z = hauteur. Façade en X = 0, tour en X = 7 000, camion en X = 420.

## Modifier l'implantation

1. dans `outils/implantation-3d.html` (contrôles géométriques) ou directement dans
   `implantation.json` : déplace, ajoute, renomme → **Exporter JSON** ;
2. remplace `unreal/implantation.json` par le fichier exporté (schéma v2 : il contient
   `podium`, `camion`, `repos`, `electricite`) ;
3. `python3 generer_projet_unreal.py` (dépendances : `pip install trimesh shapely numpy mapbox_earcut`) ;
   le script vide `Elements/` des anciens `SM_*` avant d'écrire ;
4. dans Unreal, relance `assembler_scene.py` : il vide les acteurs tagués `implantation`
   et les repose. **Ce que tu as ajouté à la main dans le niveau est conservé**.

Si tu retravailles un `SM_*` directement dans Unreal, fais-le sur une **copie** sous un
autre nom, sinon le prochain import l'écrase.

## La démo animée (pour la mairie)

Deux versions du même scénario (16 h → 2 h, 14 phases : montage, village, scène ouverte,
DJ sur le hayon, défilé des luttes, concert, extinction, mapping, lasers, rap, DJ de
clôture, sortie), avec les **mêmes paramètres** dans `Content/Import/demo_params.json` :

- **`outils/demo-evenement.html`** — autonome, dans un navigateur : personnages avec
  visages, performeurs, cortège et banderoles, écran du camion animé, légende technique
  avec nomenclature Layher, jauges et bilan électrique, boutons *Enregistrer la vidéo* et
  *Image*. C'est la version à montrer tout de suite, vérifiée en rendu.
- **`Content/Python/demo_sequence.py`** — à lancer après `assembler_scene.py` :
  matériaux à paramètres, soleil + ciel + brouillard volumétrique, candélabres et
  lumières de stands, puis la **Level Sequence `Seq_Soiree`** (1 h = 10 s) : soleil,
  allumage des groupes par phase (`eclairage_public`, `village`, `sono`, `ambiance`,
  `mapping`, `lasers`), visibilité des volumes d'étude, caméra sur le plan-séquence.
  Les nouveaux flags (`scene_ouverte`, `dj_hayon`, `defile`, `live`, `rap`,
  `ecran_camion`) sont dans les phases ; les personnages, le cortège et l'écran animé
  ne sont pas générés dans Unreal : MetaHumans / Crowd et un Media Player sur `M_Ecran`
  sont à brancher à la main. Non exécuté dans Unreal ici (voir ci-dessous).

## Ce qui n'est pas là

- Pas de `.uasset` ni de `.umap` versionnés : ils sont produits par l'éditeur au premier
  assemblage.
- Pas de texture : les matériaux sont des couleurs.
- Les voisins sont des boîtes. Pour un rendu crédible, prends le cadastre
  (`cadastre.data.gouv.fr`) ou le modèle 3D de l'IGN (*BD TOPO* bâti 3D) — voir la skill
  `flux-evenement`, référence `sources-ouvertes.md`.
- Pas de personnages : la foule, les performeurs et le DJ sont dans la démo HTML seulement.

## Vérifications faites

Le GLB de scène a été rechargé par un lecteur glTF indépendant (three.js r128) : 64
maillages, 10 lumières, emprise −120 → 120 m en X, −108 → 160 m en Z, positions conformes
à la démo. Les cônes de faisceaux ont la pointe sur l'appareil et la base sur la cible
(corrigé en v2). **Le projet n'a pas été ouvert dans Unreal lui-même** — pas de licence
Unreal dans l'environnement où il a été fabriqué. Le `.uproject`, l'assembleur Python et
les réglages suivent l'API officielle (`unreal.AssetImportTask`, `EditorActorSubsystem`,
`LightUnits.LUMENS`), mais le premier lancement peut demander un ajustement ; si le
script bloque, l'import `Into Level` du GLB de scène est la voie sans risque.
