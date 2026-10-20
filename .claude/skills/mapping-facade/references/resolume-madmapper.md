# Resolume, MadMapper et laser — la config logicielle

## Répartition des rôles

La combinaison la plus stable sur un spectacle de façade :

- **Resolume Arena** → la vidéo, tous les projecteurs ;
- **MadMapper + MadLaser** → le laser, sortie ILDA via DAC (Ether Dream, Helios) ou
  directement sur l'ampli du laser.

Synchronisation : **timecode MTC/LTC** depuis la régie son, c'est le plus fiable en
extérieur. Ableton Link si tout est sur le même réseau. **Ne fais pas transiter la
vidéo par NDI entre les deux logiciels** : à ces résolutions, la latence et la charge
réseau ne le supportent pas.

**Arena, pas Avenue** : c'est Arena qui a l'Advanced Output (slices, warping,
**soft edge blending**, masking). Sans blend, pas de pavage.

---

## Résolution de composition

Raisonne en **densité de pixels par mètre**, c'est la seule grandeur qui se compare
d'un projet à l'autre :

| Densité | Verdict |
|---|---|
| < 30 px/m | plancher absolu, grands aplats seulement |
| 50 – 70 px/m | correct au-delà de 20 m de recul du public |
| **100 px/m et plus** | confortable, on peut dessiner la pierre |

```
densité = résolution horizontale de la machine / largeur d'image en mètres
```

Une 4K (3840 px) sur 34,7 m donne 111 px/m, soit 9 mm par pixel. La même machine en
WUXGA (1920) donne 55 px/m, soit 18 mm : suffisant pour des aplats, insuffisant pour
du tracé fin ou de la petite typo.

**Taille de composition** pour un pavage de R rangées, avec un recouvrement de `o`
mètres :

```
blend_px   = o × densité
hauteur    = R × (résolution verticale) − (R−1) × blend_px
```

Arrondis la hauteur au multiple de 8 supérieur (confort des codecs).

Exemple : 2 × 3840×2160, recouvrement 1,7 m à 111 px/m = 189 px
→ composition **3840 × 4136**, 15,9 Mpx par image.

---

## Correspondance SVG → pixels

Le SVG de la skill est à **1 unité = 1 cm**. Pour une composition à D px/m :

```
facteur d'import = D / 100
```

À 111 px/m, on importe le SVG à **111 %**. Une façade de 32,5 m fait alors 3 597 px
dans une composition de 3 840 : les 243 px restants sont le débord latéral, à
conserver comme marge de bleed pour le warp.

Workflow contenus : **SVG → Illustrator / After Effects** (le SVG en calque de
repérage verrouillé, à l'échelle) → rendu → **encodage DXV3 avec Alley** → Resolume.

---

## Débit et machine

DXV3 en 3840 × 4136 à 60 fps : compter **400 à 700 Mo/s** de lecture disque **par
flux**.

- **NVMe obligatoire.** Pas de SATA, pas de disque réseau.
- Plusieurs couches vidéo pleine résolution simultanées → multiplier d'autant.
  Prévoir du NVMe en RAID 0, ou limiter le nombre de couches.
- GPU avec **deux sorties 4K60 natives** en DisplayPort minimum.
- Vérifier que Resolume tient 60 fps **preview fermée** — la preview coûte cher.

---

## Advanced Output, pas à pas

1. `Output > Advanced` → créer **un écran par projecteur**.
2. Sur chacun, une **slice** prenant sa part de la composition (pour 2 rangées :
   0→2160 et (2160−blend)→hauteur).
3. Onglet **Edge Blending** sur la bande de recouvrement. La courbe gamma s'ajuste
   **sur site, de nuit, sur la matière** — jamais en salle : la pierre n'a pas le
   gamma d'un écran, et un blend réglé au bureau se voit comme une barre claire.
4. **Warping** par slice pour coller la géométrie réelle. C'est là que les ± 5 % du
   relevé photogrammétrique se rattrapent.
5. **Masque** : rastériser le `_MASQUE.svg` en PNG à la résolution de la composition,
   le poser en couche de masque au-dessus de tout. Le ciel et les bâtiments voisins
   restent noirs. Sur un monument en ville, ce n'est pas une option : la lumière qui
   déborde va dans les fenêtres des riverains.

**Avant la mise en place**, fais tourner les contenus sur le SVG dans Resolume en
« dry run ». Ça révèle immédiatement les éléments qui tombent sur un contrefort ou
dans une baie.

---

## Laser : le budget de points

Un galvo scanne à **30 kpps** (30 000 points/seconde). Pour un tracé stable à 30 fps
sans scintillement :

```
budget = 30 000 / 30 = 1 000 points par image, blanking compris
```

C'est très peu, et ça contraint le fichier bien plus que la géométrie :

- **pas de remplissage** — un laser trace, il ne remplit pas ;
- **pas de texte vectorisé complexe**, pas de dégradé, pas de flou ;
- **chemins fermés** de préférence : moins de sauts de blanking ;
- **2 ou 3 calques allumés au maximum** en simultané, sinon ça clignote ;
- **les cercles sont les formes les plus chères** : un cercle propre coûte 60 à 100
  points. Une rosace à 3 anneaux et 12 rayons mange déjà 40 % du budget.

Ce dernier point est aussi une bonne nouvelle : sur une façade d'église, **la rosace
seule fait une très belle image laser**, et c'est le geste le plus évident.

Le `_LASER.svg` produit par la skill respecte ces contraintes (trait seul, une
trentaine de primitives). Vérifie quand même le compte de points dans MadLaser avant
de valider un tableau.

---

## Sécurité laser

- **Aucun balayage du public** sans dossier de conformité. À grande distance, la
  divergence ne suffit pas à garantir l'innocuité : il faut un calcul de **NOHD**
  (distance nominale de risque oculaire) fourni par le prestataire, et une zone
  d'exclusion physique.
- **Faisceaux vers le ciel : déclaration obligatoire** (DGAC / préfecture). Vérifie
  les zones d'approche aéroportuaires — en Île-de-France, c'est quasi systématique.
- **Prestataire certifié**, opérateur présent pendant tout le spectacle, coupure
  d'urgence accessible en régie.
- La pierre claire « accroche » très bien le laser : inutile de surpuissancer. Un
  6-10 W RGB suffit largement sur une grande façade.
