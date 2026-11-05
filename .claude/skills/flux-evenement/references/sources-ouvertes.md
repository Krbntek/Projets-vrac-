# Sources ouvertes utiles à un événement en France

Ce qu'elles apportent au plan, et comment on les enregistre. Pour chacune : garder la
réponse brute dans l'entrée, noter l'URL exacte, la date, la licence. Les API changent ;
si un appel échoue, lire la doc du jour avant d'insister.

## Le lieu

**Adresse → coordonnées** — Base Adresse Nationale, `https://api-adresse.data.gouv.fr/search/?q=…`
Donne lat/lon, code INSEE, parcelle. Point de départ pour tout le reste. Licence Ouverte.

**Cadastre — emprise des bâtiments** — `https://cadastre.data.gouv.fr/` (Etalab), GeoJSON
par commune : `…/bundler/cadastre-etalab/communes/<INSEE>/geojson/batiments`.
Saint-Denis (93) = INSEE `93066`. C'est ce qui remplace les boîtes « voisins » du plan
3D par les vraies emprises du parvis. Pas de hauteur dans le cadastre.

**Bâti 3D avec hauteurs** — IGN Géoplateforme, BD TOPO (couche `BATIMENT`, attribut
`HAUTEUR`), en WFS : `https://data.geopf.fr/wfs/ows?SERVICE=WFS&…&TYPENAME=BDTOPO_V3:batiment`.
Licence Ouverte. Avec le cadastre, ça donne des volumes réalistes autour de la place.
Aussi : orthophotos (WMTS `ORTHOIMAGERY.ORTHOPHOTOS`) pour une texture de sol.

**OpenStreetMap** — Overpass API, `https://overpass-api.de/api/interpreter`, requête sur
une bbox : arbres (`natural=tree`), candélabres (`highway=street_lamp`), bancs, arrêts,
bornes. Ce sont les obstacles qui ne sont ni dans le cadastre ni dans la BD TOPO et qui
coupent un faisceau. Licence ODbL (attribution obligatoire).

**Plaine Commune / Saint-Denis** — portail open data de l'intercommunalité
(`opendata.plainecommune.fr`) : mobilier urbain, éclairage public, voirie, manifestations.
Vérifier ce qui est publié, ça bouge.

## Le temps et l'environnement

**Météo** — Open-Meteo, `https://api.open-meteo.com/v1/forecast?latitude=…&longitude=…&hourly=…`
sans clé, prévisions horaires : vent (tonnelles, échafaudage — au-delà de 50 km/h on
démonte les toits), pluie, température, humidité (visibilité des faisceaux, buée sur
les optiques). Licence CC-BY 4.0. Pour l'historique : Météo-France sur data.gouv.fr.

**Heures de coucher du soleil** — `https://api.sunrise-sunset.org/json?lat=…&lng=…&date=…`
Décide l'heure de début du mapping : il faut la nuit noire, pas le crépuscule.

**Bruit** — Bruitparif pour l'Île-de-France (`bruitparif.fr`, open data) : niveaux de
fond, utiles pour le dossier son et les riverains.

## Les gens et les accès

**Transports** — Île-de-France Mobilités, PRIM (`prim.iledefrance-mobilites.fr`, clé
gratuite) : horaires temps réel, derniers métros/tram (Saint-Denis Basilique : ligne 13,
tram T1 et T8). Dimensionne la sortie du public.

**Population et jauge** — INSEE pour la commune ; la jauge du parvis, c'est la surface
utile × 2 pers/m² (le plan la calcule), à confronter au dossier préfecture.

**Événements concurrents** — `openagenda.com` (API), agenda de la ville : éviter un
match au Stade de France le même soir.

## Comment on les enregistre

```bash
python3 scripts/ingerer.py ajouter --json '{
  "id":"data-cadastre","categorie":"donnee","type":"cadastre-batiments",
  "nom":"Bâtiments cadastre Saint-Denis (93066)",
  "url":"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/93066/geojson/batiments",
  "licence":"Licence Ouverte 2.0","recupere_le":"2026-11-02T10:12:00Z",
  "fichier":"batiments.geojson","statut":"confirme",
  "source":{"entree":"2026-11-02_cadastre"}}'
```

Le fichier brut va dans `evenement/entrees/2026-11-02_cadastre/` (il est ignoré par Git
s'il est lourd : le registre garde l'URL pour le refaire).

## Pour passer des données au plan 3D

Les emprises de bâtiments (cadastre + hauteur BD TOPO) se convertissent en entrées
`voisins` de `unreal/implantation.json` : pour chaque bâtiment, sa boîte englobante
`{x0,x1,z0,z1,h}` dans le repère du plan (origine au centre de la façade, Z vers la
place). Il faut d'abord fixer l'orientation de la façade (azimut) pour tourner les
coordonnées géographiques dans ce repère ; c'est une rotation + translation, à écrire
une fois dans un petit script de l'entrée, pas à la main.
