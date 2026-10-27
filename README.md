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

## Autres fichiers
- `dmx-simple-3d.html`, `Liaison HF basique antennes crmx-antennes-3d.html`,
  `Angle puissance et interférences HF light rf-dmx-champ-3d.html` : visualisations 3D DMX/HF.

## Licence & production
Code libre sous licence [MIT](LICENSE). Outils co-développés avec l'assistant IA Claude
(Anthropic) via Claude Code : l'humain fixe les besoins, fournit les données de terrain et
valide ; l'IA écrit le code et recoupe les spécifications. Les valeurs restent théoriques :
vérification au luxmètre sur site indispensable.
