---
name: mapping-facade
description: >
  Méthode complète pour préparer un mapping vidéo et/ou laser sur une façade :
  relevé photogrammétrique coté à partir d'une photo, génération d'une élévation
  SVG métrique multi-calques pour MadMapper, Resolume, Illustrator ou After
  Effects, et dimensionnement chiffré — rapport de projection, nombre et puissance
  des vidéoprojecteurs, éclairement en lux, pavage et edge blending, résolution de
  composition, budget de points ILDA, autorisations françaises. Utilise cette skill
  dès qu'il est question de projeter des images sur un bâtiment — façade, église,
  cathédrale, château, mairie — même si l'utilisateur ne dit que « mapping »,
  « projection architecturale », « son et lumière », « combien de projecteurs »,
  « quel rapport d'optique », « combien de lumens », « il me faut le SVG de cette
  façade », ou qu'il arrive avec une photo de bâtiment et l'envie de projeter
  dessus. Vaut aussi pour une demande partielle : juste le relevé, juste la
  puissance, juste le choix d'optique.
---

# Mapping de façade — du relevé au dimensionnement

Préparer un mapping, c'est répondre à quatre questions dans cet ordre :
**quelle est la géométrie réelle du bâtiment ?** → **quelle toile vectorielle ?** →
**combien de machines et quelle puissance ?** → **quelle config logicielle ?**

Prises dans le désordre, elles produisent des études fausses qui ne se voient qu'au
montage, quand le camion est déjà là. La valeur de cette skill est surtout dans les
deux premières étapes : si le calage d'échelle est faux, tout le reste l'est aussi,
silencieusement.

## Avant toute chose : trois questions au commanditaire

Pose-les en premier, même si on ne te demande « qu'un SVG ». Elles changent le
projet, pas juste ses détails.

1. **Le bâtiment est-il en travaux ?** Échafaudage, bâche, emprise de chantier sur le
   parvis. Sur un monument, c'est fréquent et ça dure des années. Cherche-le
   activement sur le web (le chantier d'un monument est toujours documenté) — ne te
   fie pas à une photo, elle est peut-être antérieure de cinq ans.
2. **L'éclairage public peut-il être éteint ?** C'est le paramètre qui décide du
   rendu, bien avant le nombre de projecteurs. S'il reste allumé, aucune puissance
   raisonnable ne sauve l'image.
3. **Quelle distance de recul est réellement disponible, et dans l'axe ?** Pas la
   distance maximale : celle où on peut poser une tour, sans public dans le faisceau.

## Étape 1 — Caler l'échelle (l'étape qui décide de tout)

**Ne calibre jamais sur une seule référence.** Une erreur de calage ne se voit pas :
elle se propage dans les surfaces, donc dans les lumens, donc dans le devis.

La méthode qui marche à partir d'une photo d'élévation :

1. Repère le niveau du sol, l'axe, et deux ou trois points hauts, en pixels.
2. Trouve **deux cotes publiées indépendantes** du bâtiment (hauteur de nef, hauteur
   de tour, largeur, diamètre d'une rose). Wikipédia, les sites d'offices de
   tourisme, les fiches de monuments, les dossiers de restauration.
3. Calcule px/m avec chacune. **Si elles convergent à moins de 5 %, le calage est
   prouvé.** Si elles divergent, une des deux cotes ne désigne pas ce que tu crois —
   typiquement « hauteur » qui veut dire hauteur sous voûte intérieure et pas hauteur
   de façade. Tranche avant de continuer.
4. Déduis les autres dimensions, y compris la largeur, de cette échelle.

```bash
python3 scripts/mesurer_facade.py calibrer --sol 1935 \
        --controle 1040=29 --controle 153=58 \
        --largeur-px 997 --convertir 790 89 1245
```

Le script fait le recoupement, signale la divergence et convertit tes repères.

**Attention aux pièges de la photo** : les personnages au premier plan sont bien plus
près de l'objectif que la façade et donnent une échelle fausse de 30 à 50 %. Une
photo « redressée » garde souvent de la perspective résiduelle : si l'axe de symétrie
mesuré (axe du portail, centre de la rose) ne tombe pas au milieu des deux rives, la
moitié la plus proche de l'objectif est dilatée. Dans ce cas, **symétrise par paires**
autour de l'axe réel plutôt que de tracer la photo telle quelle.

## Étape 2 — Relever la géométrie

Trois mesures sont fiables et automatisables ; le reste se lit à l'œil.

```bash
python3 scripts/mesurer_facade.py silhouette facade.jpg --polyligne
python3 scripts/mesurer_facade.py lignes facade.jpg --zone 140,1000,800,1990
python3 scripts/mesurer_facade.py recadrer facade.jpg --boite 820,1700,1120,2007 --zoom 3
```

- **silhouette** : segmentation du ciel. C'est la mesure la plus sûre de toutes, et
  c'est exactement ce dont le masque a besoin.
- **lignes** : énergie de gradient cumulée → corniches, bandeaux, appuis
  (horizontales) et contreforts, refends, travées (verticales). Les pics proches par
  paires sont les deux arêtes d'un même élément.
- **recadrer** : pour tout le reste. N'essaie pas d'automatiser la détection des
  baies : les ombres portées ont le même contraste que la pierre, et un recadrage
  agrandi lu à l'œil donne de meilleurs résultats en moins de temps.

## Étape 3 — Produire le SVG

### Dis la vérité sur ce que tu livres

S'il s'agit d'un monument, **le relevé exact existe** (il a servi aux restaurations)
mais il est en DWG chez l'architecte en chef des monuments historiques ou à la DRAC,
pas en ligne. Dis-le, et donne les deux voies d'accès : demande sous convention, ou
scan lidar par un géomètre (ordre de grandeur 2 500 à 5 000 € pour une grande
façade). Ce que tu produis est **une élévation métrique cotée à ± 3 à 5 %** — sans
conséquence pour du mapping (le warp absorbe), à recaler pour du laser en tracé fin.

Ne laisse jamais croire que c'est un relevé de géomètre.

### La convention, toujours la même

    Modèle : X en mètres, 0 = axe de symétrie ; Y en mètres, 0 = sol, vers le haut
    SVG    : 1 unité = 1 cm réel
             le SOL est sur le bord INFÉRIEUR du viewBox
             l'axe de symétrie est au MILIEU du viewBox

Ce n'est pas cosmétique : avec ça, n'importe quel contenu fabriqué à N px/m se cale
par un simple facteur, le masque s'aligne tout seul, et deux personnes qui travaillent
sur des fichiers différents restent d'accord.

### Le code

Copie `scripts/svg_facade.py` **dans le dossier du projet** (les dossiers de projet
partent chez des prestataires, ils doivent être autonomes), puis écris un
`generer_facade_svg.py` qui déclare les cotes en tête et assemble les calques :

```python
from svg_facade import Facade, apercu_png
F = Facade(largeur_m=32.5, hauteur_doc_m=61.0)
(F.calque("00-CALAGE", F.calque_calage(Y_SOMMET, y_croix=Y_PARAPET), 'fill="none"')
  .calque("10-CONTOUR", [F.polygone(points_silhouette)])
  .calque("50-PORTAILS", F.portail(0, 2.60, 5.50, 5.35, 5.40, n_voussures=5))
  .ecrire("facade_ELEVATION.svg", titre, desc))
```

Primitives disponibles : `rect`, `ligne`, `cercle`, `polygone`, `baie_cintree`,
`baie_ogivale`, `portail`, `rosace`, `crenelage`, `arcature`, `contrefort`,
`pignon`, `calque_calage`. Lis l'en-tête de `svg_facade.py` pour les signatures.

**Garde toutes les cotes en constantes nommées en tête de fichier.** Le relevé sur
site arrivera, et il faut qu'une correction d'une valeur régénère l'ensemble.

### Livre trois fichiers, pas un

| Fichier | Pour |
|---|---|
| `*_ELEVATION.svg` | le travail : calques nommés, import Illustrator / AE / MadMapper |
| `*_MASQUE.svg` | silhouette pleine → masque alpha Resolume/AE. La lumière qui déborde va dans les fenêtres des riverains : sur un monument, ce n'est pas négociable |
| `*_LASER.svg` | trait seul, sans remplissage, peu de points |

Nomme les calques avec un préfixe numérique (`10-CONTOUR`, `20-MASSES`…) : l'ordre
d'empilement reste lisible dans tous les logiciels.

**Regarde toujours le rendu PNG** (`apercu_png`). Une élévation fausse se voit à
l'œil en une seconde et ne se lit jamais dans des coordonnées.

### Propose le recalage sur site

Liste 4 ou 5 cotes à vérifier au télémètre, avec la valeur attendue, et dis où les
reporter dans le script. Trente minutes sur place sécurisent toute la production de
contenu.

## Étape 4 — Dimensionner

**Lis `references/optique-et-puissance.md` avant de donner le moindre chiffre.**
Les trois contre-intuitions qui s'y trouvent sont la raison d'être de cette skill :

- l'éclairement se calcule sur la **surface émise**, pas sur la surface de pierre ;
- le **rapport d'optique ne change pas** le nombre de machines, il ne fixe que la
  distance ;
- le nombre de machines est fixé par **l'accord de format** (→ zones) et le **flux
  unitaire** (→ empilement). Pour en avoir moins, on monte en classe de machine.

Ne te contente pas de valider la config qu'on te propose : si elle est sous-dimensionnée,
dis-le avec le facteur ("c'est 8 fois trop peu"), puis propose **deux issues** — monter
en puissance, ou réduire la toile à une travée. La seconde est souvent la bonne et
personne n'y pense.

## Étape 5 — Config logicielle et laser

`references/resolume-madmapper.md` : résolution de composition, correspondance SVG →
pixels, Advanced Output, edge blending, débit disque DXV3, budget de points ILDA et
sécurité laser.

## Étape 6 — Autorisations

`references/autorisations-france.md`. En France, sur un monument avec du public, ça
se mène en parallèle de la technique et c'est le chemin critique. Un mapping sur
monument historique sans l'accord du gestionnaire ne se fait pas, quel que soit le
matériel réservé.

## Le calculateur partagé — source unique

**Ne réécris jamais un calculateur depuis zéro.** Il en existe un, générique, qui sert
à tous les projets :

```
https://raw.githubusercontent.com/Krbntek/Projets-vrac-/main/outils/calculateur-mapping.html
```

(si la branche `main` ne l'a pas encore, essaie
`refs/heads/claude/church-facade-mapping-9znqus` sur le même chemin)

Il prend n'importe quelle façade, a des préréglages, retient les réglages du chantier
dans le navigateur, et calcule : éclairement, rapport de projection, pavage, parc
nécessaire, résolution de composition, table distance ↔ optique.

Le contrat de synchronisation, dans les deux sens :

- **au début d'un projet** : récupère ce fichier, copie-le dans le dossier du projet
  ou ouvre-le tel quel — ne fabrique pas une variante ;
- **quand tu l'améliores** (nouveau calcul, correction) : l'amélioration va dans
  `outils/calculateur-mapping.html` du dépôt, et elle est poussée. Tous les projets
  en bénéficient ;
- **quand tu corriges une formule** : vérifie que le document du projet et le
  calculateur donnent les mêmes chiffres sur au moins trois configurations. Un
  écart entre les deux est un bug, pas un arrondi.

## Les erreurs qui coûtent cher

Elles reviennent toutes, sur tous les projets.

1. **Diviser les lumens par la surface de pierre.** Surestime l'éclairement de 30 à
   40 %. C'est la surface émise qui compte.
2. **Caler l'échelle sur une seule référence.** Ou pire, sur les silhouettes humaines
   au premier plan d'une photo.
3. **Croire qu'une optique plus courte « donne plus de lumière ».** À image constante,
   les lumens sur la pierre sont les mêmes à 40 m qu'à 123 m.
4. **Oublier le format.** Une machine 16:9 calée sur la hauteur d'une façade quasi
   carrée jette 60 % de sa lumière à côté du bâtiment. C'est le réflexe naturel, et
   c'est le pire choix possible.
5. **Promettre un shift sans vérifier.** Sur un stack vertical, la machine haute
   demande couramment 100 % de décalage, hors plage usuelle (± 60-70 %) : il faut
   incliner et corriger au warp, ~10-15 % de pixels. Et en mode portrait, les axes de
   shift tournent avec la machine — c'est le petit débattement horizontal qui doit
   rattraper toute la hauteur.

## Structure de livraison

```
mapping-<lieu>/
├── README.md                  chiffres clés + avertissements
├── CALCULS-MAPPING.md          le dossier : calage, cotes, optique, puissance, logiciel, autorisations
├── generer_facade_svg.py       cotes en tête, régénère tout
├── svg_facade.py               copie de la bibliothèque (autonomie du dossier)
├── facade-*_ELEVATION.svg
├── facade-*_MASQUE.svg
├── facade-*_LASER.svg
└── apercu-*.png
```

Et le calculateur reste dans `outils/`, partagé, jamais dupliqué.

## Étude de cas

Un dossier complet appliquant cette méthode, avec les chiffres réels et les deux
corrections de formule qui ont été faites en route, dans le même dépôt :
`mapping-basilique-saint-denis/CALCULS-MAPPING.md`. Utile comme modèle de rédaction
et de niveau de détail attendu.
