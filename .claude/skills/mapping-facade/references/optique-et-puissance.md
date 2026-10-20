# Optique et puissance — le dimensionnement chiffré

À lire avant de donner le moindre chiffre sur un projet de mapping.
Trois idées fausses coûtent cher ; elles sont traitées ici dans l'ordre où elles
font des dégâts.

## Table des matières

1. [Surfaces : laquelle au dénominateur](#1-surfaces)
2. [Éclairement : la formule](#2-éclairement)
3. [Les cibles en lux](#3-cibles)
4. [Le format décide du nombre de zones](#4-format)
5. [Le flux unitaire décide du nombre de machines](#5-flux)
6. [Le rapport d'optique ne décide de rien](#6-optique)
7. [Hauteur d'implantation et lens shift](#7-shift)
8. [Électricité](#8-électricité)
9. [Exemple complet](#9-exemple)

---

<a name="1-surfaces"></a>
## 1. Surfaces : laquelle au dénominateur

Trois surfaces différentes, qu'on confond tout le temps :

| | Quoi | Sert à |
|---|---|---|
| **S_pierre** | la maçonnerie réellement éclairée | juger du gâchis, pas à calculer les lux |
| **S_cadre** | le rectangle englobant de la façade | cadrer les contenus |
| **S_émise** | somme des surfaces d'image de **toutes** les machines | **le calcul des lux** |

```
S_émise = nombre de zones × (largeur d'image × hauteur d'image)
```

La bande de recouvrement entre deux zones y est comptée **deux fois**, et c'est
correct : chaque machine y est atténuée de moitié par le blend. Cette lumière est
dépensée, elle n'éclaire rien de plus.

**L'erreur classique** est de diviser par S_pierre. Sur une façade typique elle
surestime l'éclairement de 30 à 40 %. Sur un devis, c'est la différence entre une
image qui existe et une image grise.

<a name="2-éclairement"></a>
## 2. Éclairement : la formule

```
E (lux) = (N × F × η) / S_émise

N  nombre de projecteurs
F  flux unitaire en lumens ANSI
η  rendement réel ≈ 0,70
   (flux nominal vs réel, vieillissement, modes éco, pertes optiques)
```

Luminance perçue sur la matière :

```
L (cd/m²) = E × ρ / π
```

| Matière | ρ |
|---|---|
| calcaire clair ravalé, enduit blanc | 0,50 – 0,60 |
| pierre non nettoyée, grès, brique claire | 0,25 – 0,35 |
| brique rouge, pierre sombre, ardoise | 0,10 – 0,20 |
| bâche de chantier blanche | 0,70 – 0,85 |

Une façade encrassée demande **le double** de puissance. Si le bâtiment a été
nettoyé récemment, c'est une bonne nouvelle à mentionner. Si une bâche d'échafaudage
couvre une partie, c'est paradoxalement la meilleure surface du chantier.

<a name="3-cibles"></a>
## 3. Les cibles en lux

| Contexte | Visé |
|---|---|
| Noir complet, éclairage public **éteint**, nuit sans lune | 30 – 50 lux (minimum viable) |
| Extinction partielle, ambiance urbaine résiduelle | **80 – 120 lux** (recommandé) |
| Éclairage public maintenu | > 250 lux — irréaliste, il faut éteindre |
| Captation vidéo / photo presse | 150 lux et plus |

L'extinction de l'éclairage public se négocie avec la commune et conditionne le
rendu bien davantage que le nombre de machines. Mets-la dans les décisions à
prendre, en haut de liste.

<a name="4-format"></a>
## 4. Le format décide du nombre de zones

Une façade de monument est souvent **quasi carrée** (ratio 0,8 à 1,0). Une machine
est en 16:9 (1,78) ou 16:10 (1,60). C'est ce désaccord, et rien d'autre, qui impose
plusieurs zones.

Métrique de comparaison : **la part des lumens émis qui tombe sur de la matière.**

Exemple sur une façade de 32,5 × 37,3 m (997 m² de pierre, + une tour de 305 m²) :

| Arrangement | Image unitaire | Zones | Émis | Sur la pierre | Rendement |
|---|---|---|---|---|---|
| 1× paysage 16:9, calé sur la **hauteur** | 66,3 × 37,3 | 1 | 2 473 m² | 997 | **40 %** ❌ |
| 1× portrait 16:9, calé sur la largeur | 34,7 × 61,7 | 1 | 2 141 m² | 1 302 | 61 % |
| 2× portrait côte à côte | 21,0 × 37,3 | 2 | 1 565 m² | 997 | 64 % |
| 1× portrait 16:10, calé sur la largeur | 34,7 × 55,5 | 1 | 1 927 m² | 1 276 | 66 % |
| **2× paysage 16:9 empilées** | 34,7 × 19,5 | 2 | 1 353 m² | 997 | **74 %** ✅ |
| **2× paysage 16:10 empilées** | 34,7 × 21,7 | 2 | 1 505 m² | 1 129 | **75 %** ✅ |

Ce qu'il faut en retenir, et qui se généralise :

- **le réflexe naturel est le pire choix.** Une machine en paysage réglée pour couvrir
  la hauteur jette 60 % de sa lumière à côté du bâtiment ;
- **empiler verticalement deux images paysage** est presque toujours l'optimum sur une
  façade haute ;
- **le portrait n'économise pas de lumens**, mais il économise de la complexité : une
  seule zone, pas de blend, une sortie vidéo, et les parties hautes (tour, clocher)
  sont traitées en prime. C'est un vrai argument quand l'équipe est légère ;
- **prévois 1 m de débord de chaque côté**. Ça coûte peu de lumens et ça sauve le warp.

Calcul du nombre de rangées pour couvrir une hauteur H avec un recouvrement o :

```
rangées = ceil( (H - o) / (hauteur d'image - o) )
```

<a name="5-flux"></a>
## 5. Le flux unitaire décide du nombre de machines

Dans un pavage à Z zones, l'éclairement ne dépend que du nombre de machines
**empilées par zone** :

```
E = S × F × η / A_zone       S = machines par zone,  N = Z × S
```

Même exemple, 2 zones de 677 m² :

| Flux unitaire | N = 2 | N = 4 | N = 6 |
|---|---|---|---|
| 10 000 lm | 10 lux | 21 lux | 31 lux |
| 20 000 lm | 21 lux | 41 lux | 62 lux |
| 30 000 lm | 31 lux | 62 lux | 93 lux |
| **40 000 lm** | 41 lux | **83 lux** | 124 lux |
| **50 000 lm** | **52 lux** | 103 lux | 155 lux |
| **60 000 lm** | **62 lux** | 124 lux | 186 lux |

Parc minimal pour une cible :

| Cible | en 20 k | en 30 k | en 40 k | en 50-60 k |
|---|---|---|---|---|
| 50 lux | 6 | 4 | 4 | **2** |
| 80 lux | 8 | 6 | **4** | **4** |
| 120 lux | 12 | 8 | 6 | **4** |

**Pour avoir moins de machines, il faut monter en classe, pas changer d'optique.**
Passer de 30 k à 50-60 k divise le parc par deux à éclairement égal — c'est aussi la
classe où le prix par machine s'envole, donc présente l'arbitrage plutôt que de
trancher à la place du client.

Classes disponibles en location (tri-DLP laser) : 10 k, 20 k, 30 k, 40 k, puis
50-60 k en gamme événementielle lourde. Ne cite pas de modèle précis sans vérifier :
les parcs bougent. Dis la classe et renvoie la disponibilité au loueur.

**Redondance** : au-delà de quelques milliers de spectateurs, une machine en panne
= une zone entière qui disparaît. Prévois une machine de spare gréée et alignée.

<a name="6-optique"></a>
## 6. Le rapport d'optique ne décide de rien

```
TR = distance / largeur d'image
```

Le rapport de projection ne relie que deux grandeurs : **où tu te mets** et **quelle
largeur tu couvres**. Il ne modifie ni le format de l'image, ni sa luminosité.

- Changer d'optique à image constante = changer de place, rien d'autre.
- La largeur d'image étant imposée par la façade, **le TR n'est pas une variable de
  conception : c'est une conséquence de la distance choisie.**
- À image constante, **les lumens sur la matière sont les mêmes à 40 m qu'à 120 m.**
  Une optique courte ne « donne » pas plus de lumière.

Où se mettre, alors ? Dans la plage des **zooms standard, TR 1,4 à 2,4 : 1** :

- ce sont les optiques les plus courantes en parc, les moins chères, les mieux
  corrigées et celles qui transmettent le mieux ;
- le tilt de la machine haute reste modéré ;
- on reste assez loin sans traverser toute la place, donc moins de public dans l'axe.

En dessous de TR 1,0 les optiques courtes sur grosses machines sont rares, chères et
plus distordues. Au-delà de TR 3,0 on ne gagne rien : mêmes lumens, optique plus
longue, plus de public dans le faisceau, plus d'atmosphère traversée (une nuit
humide, ça se voit).

Pour une image large de L mètres, la distance confortable est donc **1,4 L à 2,4 L**.

<a name="7-shift"></a>
## 7. Hauteur d'implantation et lens shift

Sur un stack vertical, la zone basse est triviale et **la zone haute est le
problème**. Image de hauteur h, centre de la zone haute à c mètres, machine à y
mètres : il faut rattraper (c − y), soit (c − y)/h en pourcentage de hauteur d'image.

Avec deux zones de 19,5 m et une machine à 8 m : la zone basse demande 9 % de shift,
la zone haute **100 %** — au-delà de la plage usuelle (± 60-70 %, à vérifier pour le
couple machine + optique retenu).

Trois issues :

1. **incliner la machine haute et corriger au warp** — pratique courante, coût ≈ 10 à
   15 % de pixels. La netteté n'est pas affectée : la façade est plane et le tirage
   long, la profondeur de champ est énorme ;
2. **surélever** la machine haute pour rester en shift pur — tour lourde, rarement
   réaliste ;
3. **reculer** : plus la distance est grande, plus le tilt nécessaire est faible.
   C'est le seul avantage réel des grandes distances.

**Piège du mode portrait** : quand on tourne une machine de 90°, les axes de shift
tournent avec elle. Le grand débattement vertical devient horizontal sur le mur —
inutile, on est centré — et c'est le petit débattement horizontal (± 30-40 %) qui
doit rattraper toute la hauteur. Le portrait impose donc presque toujours du tilt.

**Hauteur de la tour de projection** : 6 à 8 m. Avec du public entre la machine et le
bâtiment, ce n'est pas un confort, c'est ce qui garantit que personne ne coupe le
faisceau. Prévois un local technique fermé et gardé.

<a name="8-électricité"></a>
## 8. Électricité

| Poste | Puissance |
|---|---|
| Projecteur laser 10 000 lm | ~1,6 – 2,2 kW |
| Projecteur laser 30 000 lm | ~3,5 – 4,5 kW |
| Projecteur laser 50-60 000 lm | ~6 – 8 kW |
| Serveurs, réseau, clim du local | 2 – 4 kW |

Estimation rapide : **~0,16 W par lumen installé**, plus le local technique.

Un parc de 4 × 40 k ≈ 20 kW → **63 A tri dédié** minimum. Au-delà, 125 A tri.
Prévois un secours (groupe ou au moins un onduleur sur les serveurs) et un câblage
protégé au passage du public.

<a name="9-exemple"></a>
## 9. Exemple complet

Façade 32,5 × 37,3 m, 997 m² de pierre, calcaire clair (ρ = 0,55), cible 80 lux.

1. **Format** → 2 zones paysage 16:9 empilées, image 34,7 × 19,5 m chacune,
   recouvrement 1,7 m → couverture 34,7 × 37,3 m, **S_émise = 1 354 m²**, 74 % des
   lumens sur la pierre.
2. **Puissance** → 80 × 1 354 / 0,70 = **155 000 lm installés**. Le parc le plus
   court : **4 × 40 000 lm** (2 par zone) = 83 lux. Avec des 30 k il en faut 6.
3. **Distance** → image de 34,7 m, plage confortable 1,4 à 2,4 × 34,7 =
   **49 à 83 m**, soit TR 1,4 à 2,4 : 1, zooms standard.
4. **Implantation** → tour de 7 m, machine basse en shift seul, machine haute
   inclinée de ~13° à 70 m et corrigée au warp.
5. **Électricité** → 160 000 lm × 0,16 ≈ 26 kW + local → **63 A tri**, secours prévu.
6. **Vérification** → les mêmes chiffres doivent sortir du calculateur partagé
   (`outils/calculateur-mapping.html`). Un écart est un bug, pas un arrondi.
