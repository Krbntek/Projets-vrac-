# Entrée — 2026-11-02 · book NoName Prestation

**Origine** : `book_noname_prestation.pdf`, 25 pages, 26 Mo — déposé dans la conversation,
**non versionné** (règle du dépôt : les médias lourds restent hors Git, le registre suffit).
**Envoyé par** : l'organisateur, avec la consigne « 4 stacks de 4 subs homemade par Sound
Agency, et le nombre de têtes que tu estimes nécessaire ».
**Contenu** : le parc son / lumière / DJ de NoName Prestation — subs SACH118 (fabrication
maison avec Sound Agency, 1 × 18", 1 700 W AES, 141 dB), TH118, KS28, SAPFX121, A15 Wide,
line array KAMA TP-980, têtes T24N (2 × 12" + 3", 1 400 W AES), Soundboks, EPM-8, console
X32, DDJ-1000 / DDJ-400, Starway Mode B (150 W, 16 ch), PAR 64 LED, GrandMA3 Command Wing,
SM58, DSP T-Rack 306 / 408, amplis Sanway D20K (20 000 W), Powersoft K10, D4×3000.

## Ce qui a été retenu (objets `objets.json`)

| Choix | Objet | Pourquoi |
|---|---|---|
| 16 × SACH118 en 4 piles de 4 | `sub-02` | demande de l'organisateur ; piles à ±17,2 et ±21 m, hors du cône du VP 1 (une pile à ±8,5 m ombrait les portails latéraux sur 3 m) |
| 12 × KAMA TP-980 | `pa-02` | **estimation** : 2 × 4 en stacks sur les piles extérieures + 2 × 2 sur tours de délai à 38 m, pour tenir 102 dB(A) jusqu'au fond des 54 m sans dépasser devant |
| 6 × T24N | `pa-03` | 2 × 2 in-fill sur les piles intérieures + 2 retours de catwalk |
| 2 × EPM-8 | `mon-01` | retours du DJ sur le hayon |
| 2 × D20K, 3 × K10, 1 × D4×3000 | `amp-01..03` | 8 canaux subs (2 par canal), 6 canaux têtes (2 par canal), 4 canaux fills / retours |
| DSP 408 + 306, X32, 2 × DDJ-1000 | `dsp-01..02`, `mix-01`, `dj-01` | système principal en régie, délais calés sur place |
| 12 × Mode B, 12 × PAR 64 LED, GrandMA3 CW | `lum-01..02`, `ctl-01` | 4 totems (2 + 2), 2 wash de façade (2), 4 PAR scène |
| 8 × SM58 | `mic-01` | HF à demander pour le catwalk |

Les objets `sub-01` et `pa-01` du plan initial passent en `abandonne` ; `tot-01`, `ech-01`,
`cont-01` sont mis à jour (totems dans le village, tour Layher avec nomenclature, régie
surélevée). Nouveaux objets d'implantation : `pod-01` (catwalk), `cam-01` (camion), `tonn-02`
(repos / stockage), `cab-01` (passages de câbles), `arm-01` (armoires), `ge-01` (groupe).

## Ce qui manque encore

- **quantités disponibles** chez NoName pour chaque référence (le book ne les donne pas) ;
- fiches techniques lisibles : dimensions, poids, SPL, angles de couverture des TP-980 et
  T24N — les valeurs du registre sont des **estimations** marquées comme telles ;
- la **prédiction acoustique** qui confirme ou corrige le nombre de têtes et le calage
  des 4 piles de subs (2 groupes L/R de 2 piles : allées de puissance au centre) ;
- consommation électrique réelle des amplis (le registre prend 1/8 de la puissance
  nominale, usage musique) ;
- les HF, les DI, les pieds, les câbles — à chiffrer avec le devis.

Les synoptiques son, lumière, vidéo, captation et électricité qui s'appuient sur ces objets
sont dans `evenement/SYNOPTIQUES.md`.
