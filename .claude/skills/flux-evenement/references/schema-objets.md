# Le modèle d'objet — `evenement/registre.json`

Un fichier JSON, une liste d'objets. Chaque objet a un `id` stable (on ne le change
jamais, même si le nom change), une `categorie`, un `type`, un `nom`, un `statut`, une
`source`, et des champs propres à sa catégorie.

```json
{
  "version": 1,
  "evenement": "Mapping Saint-Denis — parvis",
  "objets": [ … ]
}
```

## Champs communs

| Champ | Obligatoire | Valeurs |
|---|---|---|
| `id` | oui | `<prefixe>-<nn>` : `vp-01`, `stand-03`, `zone-parvis`, `pers-05`, `data-cadastre` |
| `categorie` | oui | `materiel` · `structure` · `espace` · `stand` · `personne` · `contenu` · `donnee` · `contrainte` · `document` |
| `type` | oui | libre mais stable : `videoprojecteur`, `optique`, `laser`, `enceinte`, `sub`, `totem`, `tonnelle`, `conteneur`, `echafaudage`, `groupe-electrogene`, `arbre`, `candelabre`, `acces`… |
| `nom` | oui | tel que la source le nomme |
| `quantite` | matériel, stand | entier |
| `statut` | oui | `a_confirmer` · `confirme` · `reserve` · `livre` · `abandonne` |
| `source` | oui | `{"entree": "2026-11-02_devis-novelty", "page": 3, "ligne": "VP 40k laser"}` + `montant_ht` si c'est un devis |
| `notes` | non | texte libre |
| `implantation` | si spatial | voir plus bas |

## Par catégorie

### `materiel` — ce qui se loue, se transporte, se branche
```json
{"id":"vp-01","categorie":"materiel","type":"videoprojecteur","nom":"Tri-DLP laser 40 000 lm 4K",
 "quantite":4,"fournisseur":"Novelty","statut":"a_confirmer",
 "dimensions_m":{"l":0.62,"h":0.42,"p":0.70},"poids_kg":92,"puissance_w":4200,
 "specifique":{"lumens":40000,"resolution":"3840x2400","optique_tr":"1.4-2.4"},
 "source":{"entree":"2026-11-02_devis-novelty","page":3,"montant_ht":1800},
 "implantation":{"element":"SM_Projecteur","groupe":"projecteurs"}}
```
`dimensions_m`, `poids_kg`, `puissance_w` sont **attendus** : s'ils manquent, `valider`
le dit. Ce sont eux qui donnent le bilan électrique, les charges sur l'échafaudage et
le volume de camion.

### `structure` — échafaudage, tour, conteneur, barrières, scène
Comme `materiel`, plus `charge_admissible_kg` si connu. Le conteneur régie est une
`structure` de type `conteneur`, dimensions 6,06 × 2,44 × 2,59 pour un 20'.

### `espace` — ce qui est déjà là : zones, accès, obstacles, réseaux
```json
{"id":"esp-04","categorie":"espace","type":"candelabre","nom":"Candélabre côté cour, axe VP",
 "position_m":{"x":9,"z":48},"hauteur_m":8,"statut":"confirme",
 "source":{"entree":"2026-11-03_photos-parvis","fichier":"IMG_2231.jpg"},
 "notes":"estimé depuis la photo, référence : passage piéton 4 m"}
```
Un `espace` avec `position_m` et `hauteur_m` devient un obstacle candidat dans le
plan 3D (à ajouter à `voisins` ou en objet dédié) — et peut couper un cône de VP.

### `stand` — un emplacement du village
```json
{"id":"stand-01","categorie":"stand","type":"prevention","nom":"Prévention — asso X",
 "quantite":1,"besoins":{"elec_w":500,"eau":false,"tables":2,"chaises":4},
 "contact":"…","statut":"confirme","source":{"entree":"2026-11-01_mail-assos"},
 "implantation":{"groupe":"village","ordre":0}}
```
`type` ∈ `prevention` · `secours` · `accueil` · `buvette` · `asso` (= couleurs des toits).
`ordre` est la place dans l'allée en partant de la régie.

### `personne` — un rôle, pas une identité biométrique
```json
{"id":"pers-03","categorie":"personne","type":"ssiap","nom":"SSIAP 1 — société Y",
 "equipe":"securite","quantite":4,"contact":"…","statut":"a_confirmer",
 "source":{"entree":"2026-11-02_devis-securite"}}
```
Pas de champ pour l'apparence. Si une photo sert à l'identification d'un rôle (gilet
« régie »), on note le rôle.

### `contenu` — visuels, maquettes, médias du spectacle
```json
{"id":"cont-02","categorie":"contenu","type":"illustration","nom":"Affiche — version 2",
 "format":"PNG 4961×7016","auteur":"…","droits":"à confirmer",
 "palette":["#1d2a3d","#c8a24a","#e8e0c8"],"usage":["affiche","motif mapping"],
 "statut":"a_confirmer","source":{"entree":"2026-11-04_visuels"}}
```

### `donnee` — ce qui vient d'une API ou d'un open data
```json
{"id":"data-cadastre","categorie":"donnee","type":"cadastre-batiments","nom":"Bâtiments cadastre, Saint-Denis",
 "url":"https://cadastre.data.gouv.fr/…","licence":"Licence Ouverte 2.0","recupere_le":"2026-11-02T10:12:00Z",
 "fichier":"batiments.geojson","statut":"confirme","source":{"entree":"2026-11-02_cadastre"},
 "notes":"emprise des bâtiments autour du parvis, pour remplacer les voisins du plan"}
```

### `contrainte` — une décision ou une règle qui s'impose au plan
```json
{"id":"ctr-01","categorie":"contrainte","type":"eclairage-public","nom":"Extinction 22 h – 1 h",
 "valeur":"22:00-01:00","emetteur":"Ville de Saint-Denis","statut":"a_confirmer",
 "source":{"entree":"2026-11-05_reunion-mairie"},"impact":["puissance VP","horaires show"]}
```

### `document` — devis, autorisations, plans, PV
```json
{"id":"doc-02","categorie":"document","type":"devis","nom":"Devis Novelty n° 2026-118",
 "date":"2026-10-28","emetteur":"Novelty","montant_ht":24800,"statut":"a_confirmer",
 "source":{"entree":"2026-11-02_devis-novelty"},"objets":["vp-01","opt-01","ech-01"]}
```

## Le bloc `implantation`

Il relie un objet au plan 3D. Deux formes :

- **positionné** : `{"element":"SM_Totem","x":-31,"z":10,"y":0,"rot_deg":0}` — mètres,
  repère du plan (X axe façade, Z recul).
- **groupé** : `{"groupe":"village","ordre":2}` ou `{"groupe":"projecteurs"}` — c'est
  le plan qui calcule la place (allée du village, plateforme VP). C'est la forme à
  préférer pour tout ce qui suit la logique du bloc central.

`vers-implantation` lit ces blocs et met à jour `unreal/implantation.json` : les
stands du village (ordre, nom, type), les projecteurs (lumens, TR), les totems et wash
positionnés. Il ne touche pas au reste du fichier.

## Unités, toujours

Mètres, kilogrammes, watts, lumens. Les dimensions en `{"l","h","p"}` = largeur,
hauteur, profondeur de l'objet posé. Une valeur inconnue se note `null`, jamais 0.
