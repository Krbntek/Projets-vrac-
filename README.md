# Projets vrac — outils techniques spectacle

Petits outils autonomes (un fichier HTML chacun, zéro dépendance, zéro réseau) pour la
préparation technique d'événements : vidéo-mapping, DMX, liaisons HF.

## 🎯 calculateur-mapping.html — v4

Calculateur de vidéo-mapping : couverture, photométrie et calibrage d'un parc de projecteurs
sur une surface réelle (façade, scénographie suspendue, écran).

**Utilisation** : télécharger le fichier et l'ouvrir dans un navigateur. Sur iPhone/Mac :
l'enregistrer dans Fichiers (iCloud Drive) puis l'ouvrir ; il fonctionne hors-ligne et peut
être épinglé à l'écran d'accueil. Rien ne quitte l'appareil.

**Fonctions principales**
- 1 ou 2 projecteurs, parc nominatif (propriétaire, flux, puissance, éditables), tri du parc ;
- surfaces prédéfinies en cartes visuelles (silhouettes : Panthère, façade Saint-Denis…) ou personnalisée ;
- photométrie : lux, nits, contraste effectif selon pollution lumineuse, matière (pierre,
  scéno peinte, etc.) et texture du support ; échelle de rendu « Invisible → Très bon » ;
- harmonisation automatique des deux images (même taille → même éclairement), conseils
  d'atténuation (ND, diaphragmes, niveau vidéo) ;
- décalage d'optique contrôlé, consommation électrique (kW, A, circuits 16 A, kWh) ;
- exports statiques : impression/PDF, rapport HTML autonome, configuration JSON (export/import) ;
- personnalisation : palettes (sombre, clair, contraste max, personnalisée), taille du texte,
  densité des étiquettes — pensé pour le téléphone ;
- encart « Transparence & méta » : équations recalculées en direct, références, méthode, limites.

**Modifier les données** : les blocs `LENSES`, `MODELS`, `PARC`, `MATS`, `TEXS`, `SURFACES`
sont en tête du code JavaScript, commentés. Les données non recoupées sont marquées ⚠ dans
l'interface, avec un tableau des sources en bas de page.

## Ajouter une référence (projecteur ou optique)

Les catalogues sont standardisés en tête du code JavaScript, chacun avec un **gabarit à
copier-coller** et un champ `src` qui trace la source de chaque valeur :
- `CONFIG` — les paramètres principaux (recul de la surface personnalisée, graduations du
  schéma, rendement η, usure lampe, dérive laser, cible lux, électricité…) ;
- `LENSES` / `MODELS` / `PARC` — optiques, modèles, machines physiques.

Deux façons d'ajouter une référence :
1. **À la main** : copier le gabarit du bloc concerné, remplir les champs depuis le manuel
   fabricant, mettre `verif:false` sur toute valeur non confirmée (elle s'affichera ⚠).
2. **Par Claude** : donner le nom exact du produit (ex. « ajoute le Panasonic PT-RZ120 »),
   et demander de retrouver la fiche fabricant, recouper au moins deux sources, remplir le
   gabarit et noter les sources dans `src` — sans jamais inventer une valeur : ce qui n'est
   pas confirmé reste `verif:false`.

⚠ Le rapport de projection d'une même optique peut changer selon la série de projecteurs :
une entrée par série dans `LENSES` quand le fabricant donne des plages différentes.

## Autres fichiers
- `dmx-simple-3d.html`, `Liaison HF basique antennes crmx-antennes-3d.html`,
  `Angle puissance et interférences HF light rf-dmx-champ-3d.html` : visualisations 3D DMX/HF.

## Licence & production
Code libre sous licence [MIT](LICENSE). Outils co-développés avec l'assistant IA Claude
(Anthropic) via Claude Code : l'humain fixe les besoins, fournit les données de terrain et
valide ; l'IA écrit le code et recoupe les spécifications. Les valeurs restent théoriques :
vérification au luxmètre sur site indispensable.
