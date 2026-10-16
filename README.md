# Plateforme SaaS de gestion d'événements

## Présentation du projet

je veux construire une application web progressive (PWA) de gestion d'événements. Je veux comprendre les choix techniques et écrire le code moi-même avec l'aide de Cursor.

La plateforme pourra couvrir plusieurs besoins : invitations à des événements privés, billetterie pour des événements publics, collecte de fonds, pétitions et sondages. Une marketplace en marque grise est envisagée plus tard et n'est pas prioritaire. Il s'agit d'une application web/PWA, pas d'une application mobile native.

## Stack technique prévue

- Interface web : Next.js, React, TypeScript et Tailwind CSS
- API : Django et Django REST Framework
- Base de données : PostgreSQL
- Hébergement envisagé : AWS ou Azure
- Paiement futur : agrégateur partenaire pour mobile money et cartes, en CDF et USD

Nous choisirons les versions et les outils au moment de les installer, puis nous expliquerons les choix.

## Architecture microservices

Le projet sera construit selon une **architecture microservices** : chaque grande fonctionnalité sera un service indépendant, avec sa propre responsabilité, son API et sa propre base de données. Le premier service sera Invitations ; la Billetterie et les autres domaines seront développés séparément au fil du projet.

Les services pourront communiquer par API ou par événements. Nous apprendrons ces mécanismes progressivement et ne créerons pas d'infrastructure distribuée complexe avant d'en avoir besoin.

Une base de données ne doit pas contenir de clé étrangère vers les tables d'un autre service. Pour référencer un objet externe, conserver son UUID dans un champ de référence, par exemple `organisateur_ref` ou `middle_user_ref`, sans contrainte de clé étrangère. Les clés primaires sont des UUID.

Nous construirons progressivement et garderons chaque service aussi simple que possible.

## Services prévus

### Invitations — premier service

Gère les événements privés organisés autour d'une liste d'invités nommés : fêtes, deuils, cultes, journées portes ouvertes et événements similaires.

Fonctions envisagées :

- Organisateurs et collaborateurs (« Middle users ») avec droits limités par événement.
- Catégories d'événements et modèles d'invitation réutilisables.
- Événements, invités, RSVP et QR codes uniques.
- Check-in des invités par caméra d'un smartphone ou d'un navigateur.
- Envois par email ou WhatsApp, suivi et relances.
- Accompagnants et champs de réponse personnalisés selon la catégorie.

Les données envisagées comprennent les organisateurs, Middle users, catégories, modèles, événements, invités, présences/check-ins, accès des collaborateurs, notifications, accompagnants, champs personnalisés et réponses.

### Billetterie — service ultérieur

Gère les événements publics et les ventes de billets. Deux modes sont prévus :

1. `physique_existant` : l'organisateur vend des billets imprimés par ses soins ; la plateforme suit uniquement les quantités, sans créer de QR codes.
2. `genere_plateforme` : la plateforme émet un billet par achat, avec QR code unique et contrôle à l'entrée.

Le service devra gérer les événements, types et tarifs de billets, stocks, ventes, paiements, remboursements, billets émis et scans. Il référencera les organisateurs et collaborateurs du service concerné avec des UUID dans des champs `_ref`, sans clé étrangère entre services.

## Façon de travailler et d'apprendre

Cursor doit agir comme un tuteur, pas réaliser tout le projet à ma place.

- Je débute : expliquer les notions en français simple, avec des exemples concrets.
- Avancer par petites étapes et commencer par le service Invitations.
- Donner une seule action à la fois : quoi faire, dans quel fichier ou terminal, et pourquoi.
- Me laisser écrire le code moi-même. Ne pas créer, modifier ou supprimer des fichiers à ma place, sauf si je le demande explicitement.
- Ne pas lancer de commande sans d'abord expliquer ce qu'elle fait et me laisser l'exécuter.
- Après chaque étape, attendre que je partage le résultat ou pose mes questions avant de continuer.
- Quand il y a une erreur, m'aider à la comprendre et à la corriger plutôt que de remplacer tout le code.
- Ne pas ajouter d'emblée PostgreSQL, authentification, paiements, déploiement ou infrastructure distribuée. Introduire ces sujets quand les bases précédentes sont comprises.
- Respecter les frontières de service : pas de clés étrangères inter-services, utiliser des UUID et des champs de référence `_ref`.
- Avant tout changement de code, consulter `SECURITY.md` et appliquer les règles pertinentes à l'étape en cours.

## Première étape suggérée

Examiner ce dépôt, vérifier les outils nécessaires, puis m'expliquer comment préparer un petit service Django REST pour Invitations avec une route `GET /health`. Cette route sert seulement à confirmer que l'API démarre et répond. N'ajouter ni base de données ni autre service à cette première étape.
