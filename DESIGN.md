# Design system Mugi

Source de vérité visuelle : le fichier Figma ci-dessous. En cas de doute, lire le cadre concerné via le serveur MCP Figma (`get_design_context`, `get_screenshot`, `get_variable_defs`) plutôt que de deviner.

## Fichier Figma

Fichier : https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency (clé `ZmK8nvkNc5q7ihcIHJh8y6`)

| Écran / élément | Node ID | Lien direct |
|---|---|---|
| Accueil (Homepage) | `1:2` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=1-2 |
| Organiser — Créer un événement | `43:154` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=43-154 |
| Invitations digitales | `46:336` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=46-336 |
| Billetterie | `47:538` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=47-538 |
| Collecte de fonds | `48:730` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=48-730 |
| Pétition et sondage | `49:889` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=49-889 |
| Market place | `50:1042` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=50-1042 |
| Overlay — Toutes les fonctionnalités (bouton Play) | `51:1319` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=51-1319 |
| Overlay — Achat de billet | `51:1444` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=51-1444 |
| Overlay — Paiement confirmé | `51:1509` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=51-1509 |
| Composants Mugi (bibliothèque) | `38:5` | https://www.figma.com/design/ZmK8nvkNc5q7ihcIHJh8y6/Creative-Agency?node-id=38-5 |

Les cadres « Vidéo — planche d'éléments » et « Vidéo — planche 2 » servent à la vidéo promotionnelle : ne pas les intégrer au site.

## Couleurs (variables Figma « Mugi — Couleurs »)

Palette stricte : uniquement ces quatre couleurs et leurs transparences.

| Token | Valeur | Usage |
|---|---|---|
| `--mugi-clair` | `#C16B2E` | Boutons, accents, mots mis en valeur, icônes sur fond blanc |
| `--mugi-fonce` | `#6A2D00` | Survol des boutons, bas des dégradés, fond de la pilule de menu (35 %) |
| `--mugi-noir` | `#000000` | Titres ; texte courant à 75 % d'opacité ; séparateurs à 10 % |
| `--mugi-blanc` | `#FFFFFF` | Fonds de section et de carte, texte sur fond marron |
| `--mugi-degrade` | `linear-gradient(135deg, #C16B2E 0%, #6A2D00 100%)` | Héros, sections alternées, pastilles d'icônes, appels à l'action |

## Typographie

Police unique : **DM Sans** (Google Fonts), graisses 400, 500, 600, 700, 900.

| Rôle | Taille / interligne | Graisse | Remarques |
|---|---|---|---|
| Titre de héros | 72 px / 106 % | Black 900 | lettre-espacement −3 % |
| Titre de section | 64 px / 105 % | Bold 700 | un mot clé peut prendre le dégradé |
| Titre de carte | 28 px | SemiBold 600 | |
| Texte courant | 20–22 px / 30–34 px | Regular 400 | noir 75 % |
| Bouton | 18 px (grand), 16 px (petit) | SemiBold 600 | |
| Menu | 22 px | SemiBold 600 | |

## Mise en page

- Largeur de référence 1920 px, contenu sur 1596 px (marges de 162 px).
- Sections : padding vertical 150 px ; alternance fond blanc / fond dégradé.
- Grilles : cartes de 504 px (3 colonnes, gouttière 42 px) ou 369 px (4 colonnes, gouttière 40 px).
- Mobile-first obligatoire (PWA) : toutes les pages doivent fonctionner dès 360 px.

## Composants (cadre « Composants Mugi »)

| Composant | Variantes / propriétés | Détails |
|---|---|---|
| Bouton | Taille Grand/Petit · Style Marron/Blanc · État Défaut/Survol | Grand : padding 30×50, rayon 20. Petit : 16×28, rayon 14. Survol : fond `#6A2D00` + ombre `0 10px 24px rgba(0,0,0,.18)`, transition 0,2 s |
| Navigation/Lien | Défaut / Survol (blanc 14 %) / Actif (blanc 24 %) | Icône 24 px + libellé, pilule rayon 999 |
| En-tête | Logo + menu | Menu dans une pilule `#6A2D00` à 35 % + flou d'arrière-plan 16 px. Liens : Accueil, Organiser, Invitations, Billetterie, Pétition et sondage, Market place |
| Carte/Fonctionnalité | Défaut / Survol | Rayon 40, padding 40, ombre `0 8px 35px 5px rgba(0,0,0,.10)`. Survol : bordure 2 px `#C16B2E` + ombre `0 18px 50px rgba(0,0,0,.16)`. Pastille d'icône 72 px, rayon 22, fond dégradé |
| Carte/Étape | Numéro, titre, description | Rayon 40, numéro Bold 56 en `#C16B2E` |
| Carte/Statistique | Libellé, valeur, détail | Rayon 32, valeur Bold 52 |
| Carte/Événement | Défaut / Survol | Image 280 px, catégorie, titre, date, lieu, prix, bouton Petit « Acheter » |
| Carte/Modèle | Défaut / Survol | Photo plein cadre 288×380, voile dégradé noir, titre blanc |
| Carte/Type de billet | Nom, prix, description, jauge de ventes | |
| Ligne/Fonctionnalité | Défaut / Survol (marron 10 %) | Utilisée dans l'overlay « Toutes les fonctionnalités » |
| Filtre | Défaut / Actif (dégradé) | Bascule au clic |
| Pied de page | — | Colonnes Produit, Liens utiles, Contact, Newsletter |

Icônes : **Lucide** (même jeu que la maquette) — `home`, `calendar-plus`, `mail`, `ticket`, `heart-handshake`, `file-signature`, `store`, `qr-code`, `scan-line`, `users`, `upload`, `circle-check`, `wine`, `bar-chart-3`, `smartphone`, `credit-card`, `message-circle`, `shield-check`, `receipt`, `target`, `download`, `user-check`, `map-pin`, `calendar`, `clock`, `tag`, `layers`, `search`, `arrow-right`, `x`, `play`, `share-2`, `check`, `lock`, `palette`, `code`.

## Interactions du prototype (à reproduire)

- Changement de page : fondu/glissement 0,45 s ease-out, l'en-tête reste fixe visuellement.
- Bouton Play de l'accueil → overlay « Toutes les fonctionnalités » (fondu 0,3 s) ; chaque ligne mène à sa page ; fermeture par la croix ou clic sur le fond.
- Carte d'événement (Market place) → overlay « Achat de billet » → bouton « Payer » → overlay « Paiement confirmé ».
- Liens « Comment ça marche », « Voir les modèles », « Découvrir les sondages » : défilement doux vers la section.
- Le lien du menu de la page courante est à l'état Actif.

## Marque

- Nom : **Mugi** (prononcé « Mougui »).
- Logo : le point devant « Mugi » fait partie du logo.
- Textes de la maquette (noms, prix, événements, témoignages, contacts) : exemples à remplacer, jamais présentés comme réels.
