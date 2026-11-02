# Implantation cotée

Repère : X = axe de la façade (0 au centre, positif côté cour / est), Z = distance au plan
de la façade. Toutes les cotes en mètres, issues de `unreal/implantation.json` (version 2),
la source commune de la démo, du visualiseur et du projet Unreal. Chaque ensemble se
déplace dans `outils/implantation-3d.html` (glisser-déposer) ; les contrôles géométriques se
recalculent et le JSON exporté alimente tout le reste.

| Ensemble | Position | Emprise | Notes |
|---|---|---|---|
| Façade mappée | z = 0 | 32,5 m de large, corps à 29,2 m, pignon 37,3 m, tour 60,1 m | relevé photogrammétrique ± 3 à 5 % |
| Camion 20 m³ | x = 0, z = 4,2 | 7,3 m (+ 1,6 m de hayon) × 2,2 m, 3,15 m de haut | cabine côté jardin, hayon côté cour, écran 4,3 × 2,2 m côté public |
| Piles de subs (4) | x = ±17,2 et ±21, z = 4 | 0,6 × 0,75 m, 2,8 m de subs + têtes | hors du cône du VP 1 ; têtes TP-980 sur les piles extérieures, T24N sur les intérieures |
| Wash de façade (2) | x = ±13, z = 5,5 | au sol, 0,5 m | cibles (−10 ; 26) et (10,5 ; 44) |
| Coffrets son (2) | x = ±25, z = 1,6 | 0,8 × 0,4 × 1,2 m | pieds de façade |
| Zone public | x = −26 à 26, z = 7 à 61 | 2 808 m² bruts, 2 712 m² nets | sans barrières, couloirs de 4 m de chaque côté |
| Tours de délai (2) | x = ±13, z = 38 | 1,4 × 1,4 m, 5 m de haut | îlots tenus par un agent, 2 × TP-980 chacune |
| Catwalk | x = −1,2 à 1,2, z = 45,4 à 57,4 | 2,4 × 12 m, 1,50 m | sans garde-corps (face jouée), bandes LED |
| Tête de scène | x = −3 à 3, z = 57,4 à 61,4 | 6 × 4 m, 1,50 m | garde-corps au fond et sur les côtés, 2 escaliers latéraux, backline |
| Coulisses | z = 61,4 à 64,4 | 3 m × 10 m | hors public, câble régie → podium |
| Régie étanche | x = −3,03 à 3,03, z = 64,4 à 66,9 | conteneur 20' 6,06 × 2,44 × 2,59 m, surélevé de 1,20 m | vitre vers la façade, porte et escalier côté tour |
| Tour VP Layher | x = −4,6 à 4,6, z = 68,5 à 71,5 | 3 travées × 3,07 m, plancher à 10,3 m, 12,9 m hors tout | VP à 10,8 m (lentille), lasers à 11,4 m, 8 lests |
| Stands (8) | x = ±8,1, ±12,3, ±16,5, ±20,7 ; z = 67,5 | tonnelles 3 × 3 m | 1,2 m entre tonnelles, 2 m avec la tour, comptoirs côté façade |
| Totems lumière (4) | x = ±10,2 et ±18,6, z = 67,5 | 5,5 m | dans les intervalles de tonnelles |
| Projecteurs de scène (2) | x = ±4,6, z = 58,4 | pieds 3,6 m | angles de la tête de scène |
| TGBT | x = −6,5, z = 72 | 1,2 × 0,6 × 1,8 m | derrière la tour, côté jardin |
| Coffret lumière · stands | x = 6,5, z = 72 | 0,8 × 0,4 × 1,2 m | derrière la tour, côté cour |
| Bâche opaque | x = −7 à 7, z = 72,8 | 2,2 m de haut | cache le repos |
| Tonnelle repos | x = 0, z = 75,5 | 6 × 3 m | bancs, table eau, 9 assis |
| Tonnelle stockage | x = 0, z = 79,2 | 3 × 3 m | 6 flight-cases |
| Groupe électrogène (option) | x = −12,5, z = 78 | 3,2 × 1,5 × 2,2 m | 100 kVA insonorisé, zone d'exclusion 2 m |

**Vidéoprojecteurs** : 2 machines classe 40 000 lm à 70 m, rapport 2,02 → deux images de
34,7 × 19,5 m empilées (centres à 9,7 m et 27,6 m), 41 lux sur la façade ; 4 machines
donneraient 83 lux. Le VP 2 travaille en shift maximal (inclinaison + warp). Le camion
ombre le bas de la façade de 0 à 2,5 m sur 9,6 m de large : zone noire dans le contenu.

**Lasers** : 2 × 10 W sur la tour, cibles sur la façade entre 5,5 m et le pignon, jamais vers
le ciel ni le public ; le bas du faisceau passe à plus de 9 m au-dessus de la zone public.
