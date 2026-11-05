# Annexes, sources et mise à jour

**Pièces du dossier**

- `exports/dossier-technique.pdf` — ce document ;
- `exports/fiche-declaration.pdf` — résumé pour les services (à compléter) ;
- `exports/plan-implantation.pdf` — cotes et vues ;
- `exports/inventaire-materiel.pdf` — matériel et structures ;
- `exports/demo-soiree.mp4` — la démo animée (16 h → 2 h en 60 s) ; `exports/photos/` ;
- `outils/demo-evenement.html` — la démo interactive (navigateur), `outils/implantation-3d.html`
  — le plan 3D où l'on déplace les ensembles, `unreal/` — le projet Unreal Engine 5 ;
- `mapping-basilique-saint-denis/` — élévation SVG de la façade et calculs de projection.

**Sources des références Layher** : notice étaiement Allround DOC0345
(<https://www.layher.nl/-/media/layher/documentatie/06-ondersteuning/french/fr-traditionele-kopspindel-badding-ondersteuningen-ar-doc0345-0621.pdf>),
fiche FIS 64 plancher acier LW (<https://www.layher.fr/permadoc/FIS_64_Plancher_acier_LW.pdf>),
brochure Allround (<https://steigerhuur.nl/wp-content/uploads/2017/01/brochure_schoorsteensteigers.pdf>),
catalogue « Layher Éléments » à consulter pour les références non confirmées
(<https://www.layher.fr/wp-content/uploads/2024/05/layher_elements_juin_2021.pdf>).

**Ce qui est estimé** : dimensions, poids et nombre de têtes de la sono (fiches NoName et
prédiction acoustique à venir), appels électriques des amplis (1/8 de la puissance
nominale), charge du hayon (plaque du véhicule), lestage de la tour (note de calcul),
volumes des bâtiments voisins (cadastre à intégrer).

**Mettre à jour ce dossier** : modifier l'implantation dans `outils/implantation-3d.html`
(glisser-déposer, variantes), exporter le JSON vers `unreal/implantation.json`, puis
`python3 exports/generer_exports.py`. Le contenu des sections est dans
`exports/dossier/sections/*.md` et l'ordre dans `exports/dossier/plan.json`.
