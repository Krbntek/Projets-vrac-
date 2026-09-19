# Mapping façade — Basilique-cathédrale de Saint-Denis

Dossier technique : relevé vectoriel de la façade occidentale + dimensionnement
vidéo (Resolume) et laser (MadMapper).

---

## 0. À lire avant tout le reste : deux points bloquants

### 0.1 Le chantier de la tour nord

Le remontage de la tour nord et de sa flèche est **en cours depuis le 14 mars 2025**
et court jusqu'à **2029-2030**. Un échafaudage de **plus de 90 m** est monté sur le
flanc nord (côté **gauche** de la façade quand on lui fait face), et **2026-2027 sont
les années consacrées à la partie haute de la tour**. La photo que tu m'as donnée est
antérieure au chantier : elle ne montre **pas** l'échafaudage.

Conséquences directes :

- une partie du parvis est emprise de chantier → ta position projecteur à 122,88 m
  et ton implantation public sont à revalider sur place ;
- la travée gauche de la façade est potentiellement masquée ou bâchée ;
- le porteur du chantier peut devenir un **support de projection** intéressant
  (bâche technique = surface plane blanche, bien plus réflective que la pierre)
  ou une **contrainte absolue** (interdiction de projeter dessus).

**Action n°1 : appeler le CMN et la maîtrise d'œuvre du chantier avant de chiffrer
quoi que ce soit.** Tout le dimensionnement ci-dessous suppose une façade dégagée.

### 0.2 Autorisations

Monument historique + cathédrale en activité + domaine public + plusieurs milliers
de personnes. Il faut, en parallèle :

| Interlocuteur | Objet |
|---|---|
| CMN (Centre des monuments nationaux) | gestionnaire du monument, autorisation de projeter sur la façade |
| DRAC Île-de-France / ACMH | monument historique, avis sur l'atteinte au monument |
| Affectataire (diocèse) | usage cultuel, horaires, accès |
| Ville de Saint-Denis | occupation du parvis, extinction de l'éclairage public |
| Préfecture 93 | manifestation > plusieurs milliers de personnes, sûreté, secours |
| DGAC / préfecture | **obligatoire dès qu'un faisceau laser sort dans le ciel** |

Le laser est le point le plus sensible : pas de balayage public (audience scanning)
sans dossier de conformité, et tout faisceau vers le ciel se déclare.

---

## 1. Le SVG de la façade — méthode, précision, limites

### Ce que tu voulais, ce que je te donne

Tu demandes « le fichier SVG **exact** ». Soyons nets : **il n'existe pas de SVG exact
de cette façade en accès libre**, et je ne peux pas en fabriquer un à partir d'une
photo. Le relevé exact existe — il a été refait pierre par pierre pour le chantier
de la tour nord — mais il est chez l'ACMH / la maîtrise d'œuvre, en DWG.

**Ce que je te livre est une élévation métrique cotée, reconstruite par
photogrammétrie approchée**, exploitable immédiatement pour :

- préparer les contenus à la bonne géométrie et au bon ratio ;
- pré-construire le masque et le découpage des surfaces dans MadMapper / Resolume ;
- faire les calculs de puissance et d'optique ;
- préparer les tracés laser.

Ce n'est **pas** un relevé au centimètre. Précision estimée : **± 3 à 5 %**, soit
± 1 m environ sur la hauteur totale. Pour du mapping c'est sans conséquence (le warp
absorbe), pour du laser en tracé fin c'est à recaler sur site (voir § 1.4).

**Le relevé exact, comment l'obtenir :** demande à l'ACMH / au service de la
Conservation régionale des monuments historiques (DRAC IdF) le relevé de la façade
occidentale en DWG. Ils l'ont, ils le donnent régulièrement aux scénographes sous
convention. Deuxième voie : un scan lidar de façade par un géomètre (compter
~2 500 à 5 000 € pour une façade de cette taille, livré en DWG/OBJ) — c'est la
dépense qui sécurise tout le reste sur une prod de cette ampleur.

### 1.1 Calage de l'échelle

Photo de référence : élévation frontale 1280 × 2007 px.

Mesures extraites automatiquement de l'image (segmentation du ciel, détection de
gradients) :

| Repère | y ou x photo (px) |
|---|---|
| Niveau du parvis | y = 1935 |
| Arase du parapet crénelé | y = 1040 |
| Sommet du pignon central | y ≈ 790 |
| Pointe de la flèche de la tour sud | y = 153 |
| Croix / girouette | y = 89 |
| Rive gauche du massif | x = 118 |
| Rive droite du massif | x = 1115 |
| Axe de symétrie (axe portail central + rosace) | x = 645 |
| Axes des contreforts intermédiaires | x = 437 et 784 |

**Échelle retenue : 30,70 px/m**, obtenue par recoupement de deux cotes publiées :

- hauteur publiée du corps de façade **29 m** → (1935 − 1040)/29 = **30,86 px/m** ;
- hauteur publiée de la **tour sud 58 m** → (1935 − 153)/58 = **30,72 px/m**.

Les deux convergent à 0,5 % près sur deux mesures indépendantes : le calage est
solide. Il donne une largeur de massif de **(1115 − 118)/30,70 = 32,5 m**, cohérente
avec les 39 m publiés pour la largeur maximale de l'édifice (mesurée au transept,
donc plus large que le massif occidental).

### 1.2 Cotes du modèle (mètres, 0 = niveau du parvis)

| Élément | Cote |
|---|---|
| Largeur hors-tout du massif | **32,50 m** |
| Largeur travée centrale (entre axes de contreforts) | 11,30 m |
| Largeur travées latérales | 10,60 m |
| Larmier du soubassement | 1,40 m |
| Imposte des portails latéraux / central | 4,90 / 5,40 m |
| Grande corniche au-dessus des portails | 10,60 m |
| Appui des baies hautes | 12,20 m |
| Sommet des baies hautes | 23,00 m |
| **Centre de la rosace-horloge** | **22,50 m**, Ø 6,00 m (cadre mouluré) |
| Bandeau d'arcature à statues | 23,10 → 25,90 m |
| Corniche sous parapet | 28,40 m |
| **Arase du parapet crénelé** | **29,20 m** |
| Sommet du pignon central | 37,30 m |
| Sommet de la statue du pignon | 38,40 m |
| Tour sud — emprise en plan | x de +5,20 à +15,80 m (10,60 m de large) |
| Tour sud — abat-sons bas | 30,10 → 36,30 m |
| Tour sud — abat-sons hauts | 37,00 → 49,00 m |
| Tour sud — arase de la tour carrée | 50,60 m |
| **Tour sud — pointe** | **58,00 m** |
| Tour sud — croix / girouette | 60,10 m |

### 1.3 Les fichiers

| Fichier | Usage |
|---|---|
| `facade-saint-denis_ELEVATION.svg` | Élévation complète, **12 calques nommés**. Le fichier de travail : import Illustrator / After Effects / MadMapper, construction des contenus. |
| `facade-saint-denis_MASQUE.svg` | Silhouette pleine, blanc sur transparent. Masque alpha pour Resolume / AE. |
| `facade-saint-denis_LASER.svg` | Tracé simplifié, **trait seul, sans remplissage, ~35 primitives**. Fichier de départ pour MadMapper + MadLaser. |
| `generer_facade_svg.py` | Le générateur. **Toutes les cotes sont en tête de fichier** : tu changes une valeur après relevé sur site, tu relances, les 3 SVG sont régénérés cohérents. |

**Convention du SVG : 1 unité SVG = 1 cm réel.**
viewBox `0 0 3250 6100` = 32,50 m × 61,00 m.
Le **sol est exactement sur le bord inférieur** du viewBox, l'**axe de symétrie est à
x = 1625**. Donc : un contenu fabriqué à 3250 × 6100 px se place à 1 px = 1 cm, et
n'importe quelle résolution de travail s'en déduit par un simple facteur.

Calques de `_ELEVATION.svg` :

```
00-CALAGE       axe, ligne de sol, mire 5 m, croix de calage aux 4 angles (magenta)
10-CONTOUR      silhouette générale -> ton masque
20-MASSES       volumes principaux : massif + fût de tour
30-CONTREFORTS  4 contreforts + tourelle d'escalier
40-CORNICHES    7 lignes horizontales structurantes
50-PORTAILS     3 portails, voussures concentriques
60-ROSACE       rosace-horloge, 12 lobes
70-BAIES        grande baie centrale, lancettes, plaques d'inscription
80-ARCATURES    arcature à statues + médaillons
85-PIGNON       pignon central + statue
90-TOUR         abat-sons, tourelles d'angle, toit, lanternon, croix
95-CRENELAGE    parapets crénelés
```

### 1.4 Recalage sur site (30 min, indispensable)

Avant la prod des contenus, un passage sur le parvis avec un télémètre laser :

1. largeur au sol entre les deux rives du massif (cote attendue **32,5 m**) ;
2. hauteur de la corniche au-dessus des portails (attendue **10,6 m**) ;
3. hauteur du parapet (attendue **29,2 m**) ;
4. diamètre du cadre de la rosace (attendu **6,0 m**) ;
5. hauteur et largeur de l'ouverture du portail central (modèle : 5,2 × 5,5 m).

Tu reportes les écarts dans les constantes en tête de `generer_facade_svg.py`,
tu relances, et tous les calculs ci-dessous se refont avec `calculateur-mapping.html`.

---

## 2. Surfaces à traiter

| Zone | Surface |
|---|---|
| Corps de façade (32,5 × 29,2) | 949 m² |
| Pignon central | 48 m² |
| **A — corps + pignon** | **997 m²** |
| Tour sud au-dessus du parapet (10,6 × 28,8) | 305 m² |
| **B — tout, tour comprise** | **1 302 m²** |
| Travée centrale seule (portail + rosace + pignon) | 378 m² |
| Rectangle englobant total (32,5 × 60,1) | 1 953 m² |

Ces surfaces sont la clé de tout le dimensionnement : **la lumière se divise par la
surface, pas par la distance.**

---

## 3. Optique — implantation à 122,88 m

### 3.1 Rapport de projection

Rapport de projection **TR = distance / largeur d'image**.

| Largeur d'image | TR à 122,88 m | Hauteur obtenue en 16:9 | en 16:10 |
|---|---|---|---|
| 32,5 m (largeur exacte) | **3,78 : 1** | 18,3 m | 20,3 m |
| **34,7 m (avec 1,10 m de débord de chaque côté)** | **3,54 : 1** | **19,5 m** | 21,7 m |
| 21,1 m (mode portrait) | 5,82 : 1 | — | — |
| 11,3 m (travée centrale seule) | 10,9 : 1 | 6,4 m | 7,1 m |

Des zooms longs standard (type 2,4-4,7 : 1 sur tri-DLP) couvrent 3,54 et 3,78 sans
problème. Pour la travée centrale seule à 10,9 : 1, il faut une optique ultra-longue
(gamme 8-13 : 1) — **à vérifier disponibilité chez le loueur**, c'est une optique rare.

⚠️ **Le 122,88 m est à revérifier** : sur ta capture, le point haut est posé sur le
parvis, pas sur le plan de la façade. Mesure au télémètre depuis le nu du mur.
Quelques mètres d'écart changent le rapport de projection et donc le choix d'optique.

### 3.2 Le vrai problème : le format, pas la distance

Ta façade fait **32,5 m × 37,3 m** (jusqu'au pignon) → ratio **0,87**, quasi carré.
Un projecteur est en **16:9 (1,78)** ou **16:10 (1,60)**. Un seul projecteur réglé
pour couvrir la largeur ne donne que 18-20 m de haut : **la moitié de la façade**.

Et si tu règles pour couvrir la hauteur (37,3 m), il te faut 66 m de largeur d'image :
**tu jettes 50 % de ta lumière à côté du bâtiment.** C'est l'erreur classique qui fait
qu'une installation « suffisante sur le papier » est grise sur site.

**Solution retenue : 2 projecteurs empilés verticalement (stack vertical + blend).**

```
        ┌──────────────────────────────┐  37,3 m  sommet du pignon
        │   PROJO HAUT  34,7 × 19,5 m  │
        │                              │
        ├─ ─ ─ ─ blend 1,70 m ─ ─ ─ ─ ─┤  ~18,7 m
        │                              │
        │   PROJO BAS   34,7 × 19,5 m  │
        └──────────────────────────────┘  0 m  parvis
            34,7 m (1,10 m de débord de chaque côté)
```

- TR **3,54 : 1** pour les deux, même optique, même distance ;
- recouvrement vertical **1,70 m** (≈ 190 px en 4K) pour le soft edge ;
- couverture totale **34,70 × 37,34 m = 1 296 m²**, soit toute la façade hors tour ;
- **77 % des pixels tombent sur la pierre** (997 m² de pierre sur 1 296 m² éclairés),
  contre ~45 % avec un projecteur unique réglé sur la hauteur.

Pour la **tour sud** (10,6 m de large × 28,8 m au-dessus du parapet, ratio 0,37) :
un 3ᵉ projecteur en **portrait** (rotation 90°), largeur d'image 16,3 m pour 29 m de
haut. 35 % de débord, inévitable. Honnêtement : **si le budget est contraint, laisse
la tour en éclairage architectural statique** (quelques découpes / wash LED) et
concentre la vidéo sur le corps de façade. Visuellement c'est plus lisible, et la
tour reste habitée par la lumière.

### 3.3 Hauteur d'implantation du projecteur

Image de 19,5 m de haut, centre de l'image basse à ~9,7 m, centre de l'image haute à
~28 m. En exploitant le **lens shift vertical** d'un tri-DLP (typiquement ± 60-70 %) :

- projecteur à **7-8 m de haut**, shift maxi vers le haut, **tilt ≈ 0°** →
  **aucun keystone, aucune perte de pixels, mise au point homogène** ;
- projecteur au sol (2 m) → il faut incliner de ~7-8° et corriger en numérique :
  perte de pixels, perte de netteté en haut, et la ligne de vue passe au niveau des
  têtes du public.

→ **Prévoir une tour de projection (échafaudage/layher) de 6 à 8 m**, avec local
technique fermé, ou un balcon / une fenêtre d'étage en face. À 122 m avec
**plusieurs milliers de personnes entre le projecteur et la façade**, la hauteur
n'est pas un confort : c'est ce qui garantit que personne ne coupe le faisceau.

Profondeur de champ : la façade est plane, les contreforts ne saillent que d'environ
1,9 m sur 123 m de tirage — **aucun problème de netteté**.

---

## 4. Puissance lumineuse — le point dur de ton projet

### 4.1 La formule

```
E (lux) = (N × F × η) / S_éclairée

N = nombre de projecteurs
F = flux unitaire (lumens ANSI)
η = rendement réel de l'installation ≈ 0,70
    (flux nominal vs flux réel, vieillissement, modes éco, pertes optiques,
     atténuation dans la zone de blend)
S_éclairée = surface du RECTANGLE projeté, pas la surface de pierre
```

⚠️ **Le piège classique** : diviser par la surface de pierre. La lumière se répartit
sur tout le rectangle projeté, débords compris. Sur notre pavage, le rectangle fait
**1 296 m²** alors que la pierre n'en représente que 997 — diviser par 997 surestime
l'éclairement de 30 %.

Luminance perçue sur la pierre : `L (cd/m²) = E × ρ / π`, avec ρ ≈ 0,55 pour du
calcaire clair ravalé (la façade a été nettoyée en 2012-2015, tant mieux : une façade
encrassée descend à ρ ≈ 0,25 et il faut doubler la puissance).

### 4.2 Ce que donnent 2 × 10 000 lm

Sur le pavage retenu (2 rangées, 1 296 m² éclairés) :

| Configuration | Flux installé | Éclairement | Luminance |
|---|---|---|---|
| **2 × 10 000 lm** | 20 000 lm | **10,8 lux** | 1,9 cd/m² |
| 4 × 20 000 lm | 80 000 lm | 43 lux | 7,6 cd/m² |
| 4 × 30 000 lm | 120 000 lm | 65 lux | 11,4 cd/m² |
| **5 × 30 000 lm** | 150 000 lm | **81 lux** | 14,2 cd/m² |
| 6 × 30 000 lm | 180 000 lm | 97 lux | 17,0 cd/m² |

*(au-delà de 2 machines, on empile plusieurs projecteurs sur la même rangée — le
pavage reste à 2 zones, seule la puissance monte)*

Cas particulier, **travée centrale seule** : 2 projecteurs en portrait **sur la même
zone** (double stack, pas de pavage), image 12,3 × 21,9 m = 269 m² → couvre le portail
central, la grande baie et la rosace-horloge.

| Configuration | Flux installé | Surface | Éclairement |
|---|---|---|---|
| **2 × 10 000 lm sur la travée centrale** | 20 000 lm | 269 m² | **52 lux** |

### 4.3 Les cibles

| Contexte | Éclairement visé |
|---|---|
| Noir complet, éclairage public **éteint**, nuit sans lune | 30 - 50 lux (minimum viable) |
| Extinction partielle, ambiance urbaine résiduelle | **80 - 120 lux** (recommandé) |
| Éclairage public maintenu | > 250 lux — irréaliste, **il faut éteindre** |
| Captation vidéo / photo presse | 150 lux et plus |

Flux à installer pour la façade entière hors tour (1 296 m² éclairés, η = 0,70) :

| Cible | **Flux installé** | Équivalent |
|---|---|---|
| 30 lux | **55 500 lm** | 2 × 30 k |
| 50 lux | **92 500 lm** | 3 × 30 k |
| 80 lux | **148 000 lm** | **5 × 30 k** |
| 120 lux | **222 000 lm** | 8 × 30 k |

### 4.4 Verdict franc

**2 × 10 000 lm, c'est 11 lux sur ta façade. C'est 7 fois trop peu** pour un
événement à plusieurs milliers de personnes sur un parvis urbain. Le rendu sera un
gris délavé, et le premier lampadaire non éteint tue le spectacle.

Trois issues, par ordre de préférence :

1. **Monter en puissance.** Cible réaliste : **5 à 6 projecteurs de 30 000 lm**
   (150 000 à 180 000 lm installés) → 81 à 97 lux. C'est le niveau attendu pour
   un mapping de monument devant ce public. En parc de loueur classique, la gamme est
   là : tri-DLP laser 4K de 20 000 à 40 000 lm (Panasonic PT-RQ22K / PT-RQ35K,
   Barco UDX-4K32, Christie D4K40-RGB). **À faire confirmer par Novelty** — c'est
   leur métier, ils te sortiront la config et surtout la disponibilité à la date.
2. **Réduire la toile.** Avec 2 × 10 000 lm, mappe **la travée centrale seule**
   en 2 machines portrait double-stackées sur la même zone (12,3 × 21,9 m =
   269 m² : portail central + grande baie + rosace-horloge) → **52 lux**, ça tient.
   Tu perds l'effet « façade entière », tu gagnes une image qui existe vraiment. Le
   reste de la façade se traite au **wash architectural** — beaucoup moins cher au
   lumen que de la vidéo.
3. **Garder 2 × 10 000 lm sur toute la façade.** À déconseiller. Si c'est imposé, il
   faut alors : extinction totale de l'éclairage public sur le parvis **et** les rues
   adjacentes, contenus très contrastés (noirs profonds, aplats saturés, pas de
   dégradés fins), et accepter que ce soit une projection d'ambiance, pas un mapping.

**Redondance :** sur un événement à plusieurs milliers de personnes, un projecteur
qui tombe en panne = la moitié de l'image qui disparaît. Prévoir **1 machine de
spare gréée et alignée**, ou un doublement en stack sur les zones critiques.

### 4.5 Électricité

| Poste | Puissance |
|---|---|
| Projecteur laser 10 000 lm | ~1,6 - 2,2 kW |
| Projecteur laser 30 000 lm | ~3,5 - 4,5 kW |
| Config 6 × 30 k + serveurs + réseau + clim local | **~30 kW** |
| Config 2 × 10 k + serveur | ~6 kW |

Prévoir **une alimentation dédiée 63 A tri minimum** (125 A tri pour la grosse
config), un groupe de secours ou au moins un onduleur sur les serveurs, et un local
technique tempéré : à 122 m du bâtiment, tu es sur le domaine public, donc coffret,
gardiennage et câblage protégé au passage du public.

---

## 5. Resolume — mise en œuvre

### 5.1 Version

**Resolume Arena** obligatoire, pas Avenue : c'est Arena qui a l'**Advanced Output**
(slices, warping, **soft edge blending**, masking). Sans blend, pas de stack vertical.

### 5.2 Résolution de composition

Sur la config 2 projecteurs 4K empilés :

| Paramètre | Valeur |
|---|---|
| Couverture totale | 34,70 × 37,34 m |
| Projecteurs | 2 × 3840 × 2160 |
| Recouvrement blend | 1,70 m ≈ 190 px |
| **Composition Resolume** | **3840 × 4131 px** (arrondir à **3840 × 4136**, multiple de 8) |
| Densité | **111 px/m** → 9 mm/pixel |
| Poids d'image | 16,0 Mpixels / frame |

En WUXGA (1920 × 1200) la densité tombe à **55 px/m** (18 mm/px) : acceptable pour
un public à plus de 20 m, insuffisant pour des détails fins (tracés de tracery,
typographie petite).

Repère métier : **30 px/m** = plancher pour un grand bâtiment, **100 px/m et plus** =
confortable, on peut dessiner la pierre. À 111 px/m tu es bien.

### 5.3 Correspondance SVG → pixels

Le SVG est à **1 unité = 1 cm**. Pour une comp à **111 px/m** :

```
facteur = 111 px/m ÷ 100 cm/m = 1,11
=> importer le SVG à 111 % pour être au pixel près
=> 32,5 m de façade = 3 597 px dans une comp de 3 840 px de large
   (les 243 px restants = le débord de 1,10 m de chaque côté : garde-les,
    c'est ta marge de bleed pour le warp)
```

Workflow contenus : **SVG → Illustrator / After Effects** (comp 3840 × 4136,
le SVG en calque de repérage verrouillé) → rendu → **encodage DXV3 avec Alley** →
Resolume.

### 5.4 Flux de données

DXV3 en 3840 × 4136 à 60 fps : compter **400 à 700 Mo/s** de lecture disque par flux.

- **NVMe obligatoire** (pas de SATA, pas de disque réseau) ;
- si plusieurs couches vidéo pleine résolution jouent en même temps, multiplier
  d'autant → prévoir **NVMe en RAID 0** ou réduire le nombre de couches simultanées ;
- GPU : au moins une RTX 4080 / A4500 avec **2 sorties 4K60 natives** (DisplayPort),
  et surveiller que Resolume reste à 60 fps stables en preview *fermée*.

### 5.5 Advanced Output

1. `Output > Advanced` → créer **2 écrans**, un par projecteur.
2. Sur chacun, une **slice** prenant sa moitié de la composition (0-2160 et 1970-4130).
3. Onglet **Edge Blending** sur la bande de recouvrement, courbe gamma à ajuster
   **sur site, de nuit, sur la pierre** — jamais en salle, la pierre n'a pas le gamma
   d'un écran.
4. **Warping** par slice pour coller la géométrie réelle (c'est là que les ± 5 % du
   relevé se rattrapent).
5. Masque : importer `facade-saint-denis_MASQUE.svg` rastérisé en PNG à la résolution
   de la comp, en **couche de masque** au-dessus de tout → le ciel et les bâtiments
   voisins restent noirs. Non négociable sur un monument : la lumière qui déborde va
   dans les fenêtres des riverains.

### 5.6 Pré-visualisation

Avant la mise en place, fais tourner les contenus sur la photo rectifiée + le SVG
dans Resolume en « dry run » : ça révèle immédiatement les contenus qui tombent sur
un contrefort ou dans une baie.

---

## 6. MadMapper + laser

### 6.1 Répartition des rôles

La combinaison la plus stable :

- **Resolume Arena** → la vidéo (les 2-6 projecteurs) ;
- **MadMapper + MadLaser** → le laser (sortie ILDA via DAC Ether Dream / Helios,
  ou directement en ILDA sur l'ampli du laser).

Synchronisation des deux : **timecode MTC/LTC** depuis la régie son (le plus fiable
en extérieur), ou Ableton Link si tout est sur le même réseau. Évite de faire
transiter la vidéo par NDI entre les deux logiciels : à ces résolutions, la latence
et la charge réseau ne le supportent pas.

### 6.2 Contraintes du fichier laser

Un galvo scanne à **30 kpps** (30 000 points/seconde). Pour un tracé stable à 30 fps
sans scintillement :

```
budget = 30 000 pps ÷ 30 fps = 1 000 points par image, blanking compris
```

C'est **très peu**. D'où `facade-saint-denis_LASER.svg` : trait seul, sans
remplissage, ~35 primitives, points d'ancrage réduits au minimum.

Règles pour ce fichier :

- **pas de remplissage** — un laser ne remplit pas, il trace ;
- **pas de texte vectorisé complexe**, pas de dégradé, pas de flou ;
- **chemins fermés** de préférence (moins de sauts de blanking) ;
- **pas plus de 2 ou 3 calques allumés simultanément**, sinon le tracé clignote ;
- les cercles (rosace) sont les formes les plus coûteuses : un cercle propre = 60 à
  100 points. Les 3 cercles + 12 rayons de la rosace = déjà ~400 points, soit 40 %
  du budget. **La rosace seule fait une très belle image laser** — c'est d'ailleurs
  le geste le plus évident sur cette façade.

### 6.3 Sécurité laser

- **Aucun balayage du public.** À 122 m, la divergence ne suffit pas à garantir
  l'innocuité : il faut un calcul de NOHD (distance nominale de risque oculaire)
  fourni par le prestataire, et une zone d'exclusion physique.
- **Faisceaux vers le ciel : déclaration obligatoire** (DGAC / préfecture) — la
  basilique est dans la zone d'approche de Paris-Le Bourget.
- Prestataire laser **certifié**, avec opérateur présent pendant tout le show et
  coupure d'urgence accessible en régie.
- Le laser sur pierre claire « accroche » très bien : inutile de surpuissancer.
  Un 6-10 W RGB est largement suffisant sur cette surface.

---

## 7. Récapitulatif des décisions à prendre

| # | Décision | Recommandation |
|---|---|---|
| 1 | État du chantier tour nord | **À vérifier immédiatement auprès du CMN** — bloquant |
| 2 | Relevé exact | Demander le DWG à l'ACMH/DRAC, ou scan lidar géomètre |
| 3 | Distance réelle | Re-mesurer au télémètre depuis le nu de la façade |
| 4 | Surface mappée | **Corps de façade 32,5 × 37,3 m** ; tour en wash |
| 5 | Nombre de projecteurs | **5 à 6 × 30 000 lm** (81-97 lux). 2 × 10 k ⇒ travée centrale seule (52 lux) |
| 6 | Implantation | 2 zones empilées, TR 3,54:1, blend 1,70 m, **tour de 6-8 m** |
| 7 | Composition Resolume | **3840 × 4136**, 111 px/m, DXV3, NVMe |
| 8 | Logiciels | Resolume **Arena** (vidéo) + MadMapper/MadLaser (laser), sync **timecode** |
| 9 | Électricité | 63 A tri mini, 125 A tri pour la grosse config, secours |
| 10 | Extinction éclairage public | **À négocier avec la Ville — conditionne tout le rendu** |

---

## Sources

- [Basilique Saint-Denis — Wikipédia](https://fr.wikipedia.org/wiki/Basilique_Saint-Denis) (108 × 39 × 29 m ; flèche nord 86 m)
- [Basilique cathédrale de Saint-Denis — VisitParisRegion](https://www.visitparisregion.com/fr/basilique-cathedrale-de-saint-denis) (tour sud 58 m)
- [Reconstruction de la tour et de la flèche — Passerelles / BnF](https://passerelles.essentiels.bnf.fr/fr/chronologie/construction/55e1a07f-e1e6-47e3-a690-ef8c003c9159-basilique-saint-denis/article/502a4e01-5de0-4eff-bd1f-f08f359671c3-reconstruction-la-tour-et-la-fleche-la-basilique-cathedrale-saint-denis)
- [Reconstruction of the tower and the north spire — Basilique cathédrale Saint-Denis](https://www.saint-denis-basilique.fr/en/notre-actualite/reconstruction-of-the-tower-and-the-north-spire-of-the-cathedral-basilica-of-saint-denis) (chantier 2025 → 2029/2030, échafaudage 90 m)
- [Flèche de la basilique cathédrale Saint-Denis — Fondation du patrimoine](https://www.fondation-patrimoine.org/les-projets/fleche-de-la-basilique-cathedrale-saint-denis/90868)
- [Remontage du clocher nord — La Pierre d'Angle / ANABF](https://anabf.org/pierredangle/dossiers/combler-la-lacune/remontage-du-clocher-nord-et-de-la-fleche-de-la-basilique-saint-denis)
