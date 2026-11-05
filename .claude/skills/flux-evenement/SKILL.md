---
name: flux-evenement
description: >
  Accueillir, trier et consolider tout ce qu'un organisateur d'événement envoie en vrac
  — slides et inventaires de matériel (PDF, PPTX, XLSX, photos de listes), devis de
  loueurs, illustrations et maquettes graphiques, photos des lieux et des équipes,
  notes vocales, données d'API et open data (cadastre, IGN, météo, transports,
  OpenStreetMap) — pour en faire un registre d'objets unique, cohérent et sourcé, qui
  alimente le plan d'implantation 3D (outils/implantation-3d.html), le projet Unreal
  (unreal/implantation.json) et l'inventaire technique. Utilise cette skill dès que
  l'utilisateur dépose un média en disant « voilà le matos », « la liste de Novelty »,
  « les photos de la place », « l'équipe », « les visuels », « récupère les données de… »,
  « ajoute ça au projet », ou envoie plusieurs fichiers hétérogènes sans consigne
  précise : chaque dépôt est une entrée du flux, à ranger, décrire et relier aux objets
  existants, jamais à traiter isolément.
---

# Flux d'entrée d'un événement

Un événement se monte avec des informations qui arrivent **dans le désordre, de
sources différentes, sous des formes différentes** : un devis en PDF, trois photos
prises sur place, une liste de matos en slide, un lien vers le cadastre, une note
vocale. Chacune apporte des objets (un projecteur, un stand, une zone, une personne,
une contrainte). Le travail de cette skill est de **transformer chaque dépôt en objets
dans un registre unique**, avec leur source, puis de propager ce qui est spatial vers
le plan 3D et le projet Unreal.

Le principe à tenir : **on ne traite jamais un média isolément**. Un devis Novelty ne
produit pas un résumé du devis ; il produit des objets « vidéoprojecteur », « optique »,
« échafaudage » avec leurs dimensions, leur poids, leur puissance, et un lien vers la
page du devis. La semaine suivante, une photo du camion montrera ces mêmes objets, et
on les reliera, on ne les recréera pas.

## Où ça vit

```
evenement/
├── registre.json              ← LE registre : tous les objets, toutes catégories
├── INVENTAIRE.md              ← généré : totaux, manques, par catégorie
└── entrees/
    └── 2026-11-02_devis-novelty/
        ├── fiche.md           ← ce que c'est, d'où ça vient, ce qu'on en a tiré
        └── (le média brut, non versionné s'il est lourd)
```

Chaque dépôt devient un dossier `entrees/<AAAA-MM-JJ>_<source-courte>/` avec sa
`fiche.md`. Le registre pointe vers l'entrée (`source.entree`) ; on peut toujours
remonter d'un objet au document qui l'a fait naître. C'est ce qui rend le registre
défendable devant un loueur, une commission de sécurité ou un co-organisateur.

Le modèle d'objet et ses catégories sont dans `references/schema-objets.md`. Lis-le
avant le premier ajout ; il est court, et les champs obligatoires par catégorie
(dimensions et poids pour le matériel, rôle pour les personnes, licence pour les
données) sont ce qui fait la valeur du registre plus tard.

## Le protocole, dépôt par dépôt

1. **Créer l'entrée** : dossier daté, média brut dedans, `fiche.md` avec origine, date,
   qui l'a envoyé, et en une phrase ce que ça contient.
2. **Extraire les objets** selon le type de média (ci-dessous). Un objet = une ligne du
   registre, avec `source` renseigné.
3. **Relier** : avant de créer, chercher dans le registre un objet équivalent
   (`scripts/ingerer.py chercher "projecteur"`). Même matériel sous deux noms → une
   seule fiche, deux sources. Dire à l'utilisateur ce qui a été fusionné.
4. **Valider** (`scripts/ingerer.py valider`) : champs manquants, unités, doublons.
   Lister les manques à l'utilisateur plutôt que d'inventer une dimension.
5. **Propager** : `scripts/ingerer.py inventaire` régénère `INVENTAIRE.md` ;
   `scripts/ingerer.py vers-implantation` pousse les objets qui ont un bloc
   `implantation` vers `unreal/implantation.json`. Dire ce qui a changé dans le plan.

Rends compte en quelques lignes : combien d'objets créés, reliés, ce qui manque, ce
qui a bougé dans l'implantation. Pas de résumé du document : les objets sont le résumé.

## Selon le média

**Slides, PDF, tableurs, devis, inventaires** — lis tout le document, pas la première
page. Chaque ligne de matériel devient un objet `materiel` avec quantité, dimensions,
poids, puissance électrique, et la page d'origine. Les devis ont souvent les poids et
puissances dans les fiches techniques en annexe : c'est là qu'il faut aller, parce que
ce sont ces chiffres qui dimensionnent l'électricité et les charges au sol. Un prix
n'est pas un objet ; il va dans `source.montant_ht` de l'objet concerné.

**Photos de lieux** — décris ce qu'elles montrent (sol, mobilier urbain, arbres,
candélabres, accès, bordures, pentes, prises, regards), et rattache à une zone du plan.
S'il y a une référence d'échelle (une voiture, une porte, un passage piéton, une
personne), estime les dimensions et dis que c'est une estimation. Une photo d'un
obstacle qui n'est pas dans le plan (un arbre, un abribus, un candélabre dans l'axe
de projection) est une information de première importance : crée l'objet `espace` et
signale le conflit potentiel avec les faisceaux.

**Photos d'équipe et de personnes** — on enregistre un **rôle** (régie son, SSIAP,
bénévole accueil, référent prévention), une équipe, un moyen de contact si donné, et
une entrée. **Pas de description physique, pas d'identification à partir du visage,
pas de recoupement avec d'autres sources pour savoir qui est qui.** Si la photo sert
seulement à compter des gens ou voir une tenue (gilets, badges), dis-le et ne crée
pas d'objets nominatifs. Si l'utilisateur donne les noms lui-même, on les prend, avec
le consentement présumé de l'organisation.

**Illustrations, maquettes, moodboards, visuels de com'** — objets `contenu` : format,
palette, motifs, ce à quoi ça sert (affiche, contenu de mapping, décor de stand). Note
l'auteur et les droits si connus. Ce sont des sources d'inspiration pour les contenus
du mapping : on en tire une direction (couleurs dominantes, rythme, motifs), jamais une
copie d'une œuvre identifiable.

**API et open data** — ne colle pas un extrait à la main : écris la requête, lance-la,
garde la réponse brute dans l'entrée avec la date et l'URL, et crée les objets
`donnee` avec la licence. `references/sources-ouvertes.md` liste les sources utiles en
France (adresse, cadastre, bâti 3D IGN, OpenStreetMap, météo, transports) et ce
qu'elles apportent au plan. Le cadastre et le bâti IGN sont ce qui remplace les boîtes
« voisins » du plan 3D par de vrais volumes.

**Notes vocales, messages, échanges** — on extrait les décisions et les contraintes,
pas la conversation : « la mairie éteint l'éclairage public de 22 h à 1 h » est un
objet `contrainte` daté et sourcé ; le reste est dans la fiche d'entrée.

## Ce qui remonte dans le plan 3D et Unreal

Seuls les objets qui ont un bloc `implantation` sont spatiaux : ils ont un élément 3D
(`SM_Tonnelle_asso`, `SM_PA_Stack`…) et une position, ou appartiennent à un groupe que
le plan place tout seul (le village, les totems). `vers-implantation` les fusionne dans
`unreal/implantation.json` ; ensuite c'est le cycle habituel : visualiseur HTML pour
vérifier, `unreal/generer_projet_unreal.py` pour régénérer les GLB, `assembler_scene.py`
dans l'éditeur.

Quand un objet de matériel entre avec des dimensions différentes de celles du plan
(un conteneur 10' au lieu de 20', une tonnelle 4 × 4), c'est le plan qui s'aligne sur
le registre, pas l'inverse — et on le dit, parce que ça peut changer un contrôle
(obstruction d'un cône, largeur d'allée).

## Ce qu'on ne fait pas

- Inventer une dimension, un poids ou une puissance manquants : on marque `?` et on
  demande. Un registre avec des trous honnêtes vaut mieux qu'un registre plausible.
- Reconnaître ou décrire des personnes à partir de leur visage.
- Copier un visuel d'artiste dans un contenu de mapping.
- Traiter un dépôt sans le ranger dans une entrée datée : un objet sans source est un
  objet qu'on ne pourra pas défendre.
