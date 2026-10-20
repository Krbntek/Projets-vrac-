# Mapping façade — Basilique-cathédrale de Saint-Denis

Kit de préparation d'un mapping vidéo + laser sur la **façade occidentale** :
élévation vectorielle métrique, masque, tracé laser, et calculs de dimensionnement.

![Élévation](apercu-elevation.png)

## Contenu

| Fichier | Quoi |
|---|---|
| **[CALCULS-MAPPING.md](CALCULS-MAPPING.md)** | **Le dossier technique.** Calage, cotes, optique, puissance, Resolume, laser, autorisations. À lire en premier. |
| `facade-saint-denis_ELEVATION.svg` | Élévation complète, 12 calques nommés — fichier de travail |
| `facade-saint-denis_MASQUE.svg` | Silhouette pleine → masque alpha Resolume / AE |
| `facade-saint-denis_LASER.svg` | Tracé simplifié trait seul → MadMapper / MadLaser |
| [`../outils/calculateur-mapping.html`](../outils/calculateur-mapping.html) | Calculateur interactif **partagé** (lux, optique, pavage, comp). Source unique pour tous les projets de mapping — ne pas dupliquer |
| `generer_facade_svg.py` | Générateur des 3 SVG — toutes les cotes en tête de fichier |
| `svg_facade.py` | Bibliothèque de primitives (copie de la skill `mapping-facade`, pour que ce dossier reste autonome) |
| `apercu-*.png` | Rendus de contrôle |

## Convention SVG

**1 unité SVG = 1 cm réel.** viewBox `0 0 3250 6100` = 32,50 m × 61,00 m.
Sol sur le bord inférieur, axe de symétrie à `x = 1625`.

## Chiffres clés

| | |
|---|---|
| Largeur du massif occidental | 32,50 m |
| Hauteur au parapet / au pignon | 29,20 m / 37,30 m |
| Hauteur de la tour sud | 58,00 m (60,10 m à la croix) |
| Surface de pierre, hors tour | 997 m² |
| Distance conseillée | **55 à 80 m → TR 1,6 à 2,3 : 1** (zooms standard) |
| Pavage retenu | 2 zones empilées, blend 1,70 m, 1 354 m² émis, 74 % sur la pierre |
| Composition Resolume | 3840 × 4136 px — **111 px/m** |
| **Puissance pour 80 lux** | **~155 000 lm — parc le plus court : 4 × 40 k** |

## Deux avertissements

1. **Chantier de la tour nord en cours** (mars 2025 → ~2030, échafaudage > 90 m sur
   le flanc nord). À vérifier auprès du CMN **avant** tout chiffrage.
2. L'élévation est un **relevé photogrammétrique approché (± 3 à 5 %)**, pas un
   relevé de géomètre. Voir § 1.4 du dossier pour le protocole de recalage sur site.

## Régénérer

```bash
python3 generer_facade_svg.py
```

## Méthode

Ce dossier applique la skill [`mapping-facade`](../.claude/skills/mapping-facade/),
qui contient la méthode généralisée (relevé, calage d'échelle, optique, puissance,
Resolume/laser, autorisations) et les scripts réutilisables.
