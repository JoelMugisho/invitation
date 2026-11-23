# Contexte du projet Mugi

Ce document sert de brief autonome à tout assistant de programmation qui intervient sur le dépôt. Il décrit le produit, les décisions déjà prises et l'état constaté du code. Il ne remplace pas la lecture des règles de sécurité (`SECURITY.md`) ni les spécifications visuelles (`DESIGN.md`).

## 1. Projet et objectif

Mugi est une plateforme SaaS de gestion d'événements. L'objectif est d'aider les organisateurs à créer des événements, inviter des participants, vendre des billets et, plus tard, gérer des collectes, des pétitions et des sondages. Le produit doit être une application web responsive et une PWA ; aucune application mobile native n'est prévue.

La marketplace de marchands en marque grise est envisagée pour plus tard et n'est pas prioritaire. Les paiements futurs doivent pouvoir prendre en charge le mobile money et les cartes, en CDF et USD, par l'intermédiaire d'un agrégateur partenaire. Ne pas présenter un partenaire, des tarifs ou une fonctionnalité de paiement comme déjà disponibles sans confirmation.

## 2. Architecture et décisions techniques

- Architecture cible : **microservices**, organisée par domaines métier. Chaque service possède son API et sa base de données indépendante.
- Backend choisi : **Django + Django REST Framework (DRF)**, Python, ORM Django et migrations intégrées de Django.
- Base : PostgreSQL, une base indépendante par service.
- Frontend cible initialement défini : Next.js, React, TypeScript et Tailwind CSS.
- Déploiement envisagé : AWS ou Azure, à décider ultérieurement.
- Services qui communiqueront le feront par API ou événements ; commencer simplement et introduire ces mécanismes quand le besoin est réel.
- Toutes les clés primaires sont des UUID.
- Aucune clé étrangère ne traverse la frontière d'un service. Une référence vers un objet d'un autre service est un UUID stocké sous un nom explicite tel que `organisateur_ref` ou `middle_user_ref`, sans contrainte de base. Les références sont vérifiées par API ou événement de confiance.
- Les relations Django `ForeignKey` sont permises entre modèles appartenant au même service et à la même base.

## 3. Services métier

### Invitations — premier service

Gère les événements privés avec liste d'invités nommés : fêtes, deuils, cultes, journées portes ouvertes, etc. Les rôles métier définis au départ sont l'Organisateur et le « Middle user » (agent de l'organisateur avec permissions limitées par événement).

Fonctionnalités attendues :

- Catégories d'événement et modèles réutilisables.
- Création et gestion d'événements, invités et réponses RSVP.
- Un QR code opaque et unique par invité, sans données personnelles encodées.
- Check-in par caméra de smartphone ou navigateur, sans douchette. Les Middle users autorisés effectuent le scan ; un scan accepté doit être enregistré et les doubles scans détectés de façon atomique.
- Envoi d'invitations par email ou WhatsApp, état de livraison et relances.
- Accompagnants (+1/famille).
- Champs et réponses personnalisés définis par catégorie (par exemple régime alimentaire ou message de condoléances).
- Droits des Middle users par événement : check-in seulement, gestion des invités, ou gestion complète.

Modèles métier prévus dans la base Invitations :

1. `Organisateur` : UUID, nom, email unique, téléphone, statut, date de création, mot de passe stocké uniquement sous forme hachée. `tenant_ref` nullable est une référence externe future, sans FK.
2. `MiddleUser` : UUID, FK interne vers l'organisateur, nom, email unique, téléphone, statut, date de création et mot de passe haché.
3. `CategorieInvitation` : nom, description, icône/couleur.
4. `TemplateInvitation` : catégorie nullable, organisateur nullable (null signifie modèle plateforme), nom, contenu, visuel et date de création.
5. `Invitation` : organisateur, catégorie, modèle optionnel, titre, description, lieu, dates d'événement et de limite RSVP, statut brouillon/publié/clos, visuel et date de création.
6. `Invite` : invitation, nom, email et téléphone optionnels, canal préféré email/WhatsApp, QR unique, statut RSVP en attente/accepté/refusé et date de réponse. Exiger au moins un moyen de contact et vérifier la cohérence avec le canal choisi.
7. `Presence` : invité, invitation, Middle user, horodatage, résultat validé/refusé/déjà scanné et méthode scan QR. Garantir que l'invité appartient à l'invitation enregistrée.
8. `AccesMiddleUser` : Middle user, invitation, type d'accès et date d'attribution ; unicité de la paire Middle user/invitation.
9. `Envoi` / notification : invité, canal, statut envoyé/livré/échoué, numéro de tentative et date.
10. `Accompagnant` : invité, nom optionnel et présence booléenne.
11. `ChampPersonnalise` : catégorie, libellé, type texte/choix/nombre, caractère obligatoire.
12. `OptionChamp` : options d'un champ de type choix (extension nécessaire au schéma initial).
13. `ReponseChamp` : champ, invité et valeur ; une réponse par paire champ/invité.

Les modèles doivent être gérés par le **Django ORM**. Les changements de schéma doivent utiliser exclusivement les migrations Django rangées dans `migrations/`. Ne pas réintroduire SQLAlchemy ni Alembic.

### Billetterie — service ultérieur

Gère les événements publics (concerts, matchs, spectacles), sans liste préalable d'invités. Deux modes d'émission sont prévus :

- `physique_existant` : l'organisateur a ses billets imprimés ; le service suit le stock et les ventes, sans créer de billets individuels ni QR codes.
- `genere_plateforme` : une vente payée crée un billet individuel avec QR unique ; celui-ci peut être contrôlé à l'entrée.

Modèles prévus : catégorie de billet, modèle de billet, événement vendu (`Billet`), types de billet/tarifs, ventes, billets émis et contrôles. Le stock doit être protégé contre la survente en cas de ventes concurrentes. Une vente payée augmente les quantités vendues ; remboursement/annulation les corrige. Le point de vente est possible pour un Middle user autorisé. Les références aux organisateurs et Middle users sont des UUID `_ref`, jamais des FK inter-services.

### Services futurs

Collecte de fonds, pétitions/sondages et marketplace. La marketplace n'est pas prioritaire. Ne pas commencer ces services avant que le périmètre Invitations soit suffisamment établi.

## 4. Marque et design

- Nom de marque : **Mugi**, prononcé « Mougui ». Le point devant « Mugi » fait partie du logo.
- `DESIGN.md` est la source de vérité visuelle et contient le lien Figma, les écrans, la palette, la typographie DM Sans, les composants et les interactions à reproduire.
- Respecter la palette et les règles de `DESIGN.md`. Concevoir mobile-first à partir de 360 px.
- Les noms, événements, prix, témoignages et contacts présents dans la maquette sont des exemples ; ne pas les présenter comme des données réelles.
- Les écrans « planche d'éléments » pour vidéo promotionnelle ne font pas partie du site.

## 5. État constaté du dépôt (23 novembre 2026)

- Le dépôt est encore en phase initiale et contient déjà un projet Django/DRF, PostgreSQL via la configuration Django, un Dockerfile et un `docker-compose.yml`.
- Le projet Django est dans `Invitations/`, avec la configuration dans `Invitations/config/`.
- L'application Django métier actuellement nommée `donnees` est dans `Invitations/donnees/`. Ses modèles ORM sont dans `models.py` ; il existe aussi des vues et des templates HTML/CSS/images.
- La route `/health` existe. Le chemin `/` sert la page d'accueil globale. Des pages de prototype existent aussi pour organiser, invitations, billetterie, collecte, pétition et marketplace.
- Les modèles Django couvrent le domaine Invitations et incluent une table d'options pour les champs personnalisés de type choix.
- Au moment de l'inspection, `Invitations/donnees/migrations/` ne contient que `__init__.py` : la migration initiale reste à créer et à examiner avant son application.
- Le frontend cible était Next.js/React/TypeScript/Tailwind, mais le prototype actuel utilise les templates rendus par Django. Ne pas entreprendre une migration vers Next.js sans demande ou décision explicite ; signaler clairement cette différence si elle affecte le travail.
- Le dépôt contient des changements non commités. Ne pas utiliser `git reset`, `git clean`, supprimer des changements utilisateur ou écraser des fichiers existants. Examiner `git status` avant toute opération Git.
- `.env` peut contenir des secrets locaux : ne jamais afficher ou copier son contenu, ne jamais le committer. Utiliser `.env.example` avec des valeurs fictives.

## 6. Sécurité

Lire `SECURITY.md` avant tout changement lié à l'API, aux données ou au frontend et appliquer les règles pertinentes. Principes essentiels :

- Autorisation côté serveur, à chaque endpoint et pour chaque ressource ; vérifier l'appartenance à l'organisateur et l'accès du Middle user. Ne jamais faire confiance aux UUID/roles fournis par le navigateur.
- Prévenir CSRF quand l'authentification par cookies est utilisée ; utiliser les protections Django, ne pas désactiver CSRF globalement.
- Prévenir XSS avec l'échappement Django/React par défaut ; ne pas insérer du HTML utilisateur non assaini.
- Utiliser l'ORM Django et ses paramètres ; pas de concaténation SQL avec des entrées utilisateur.
- Les mots de passe ne sont jamais stockés en clair. Utiliser les fonctions de hachage Django (Argon2 configuré lorsque disponible), pas de chiffrement réversible ni de fonction maison.
- Secrets hors du code et hors de Git. HTTPS en production, CORS limité aux origines nécessaires, erreurs publiques génériques, journaux sans secrets ni données personnelles inutiles.
- Le Top 10 OWASP est un guide de sensibilisation, pas une garantie de sécurité. `SECURITY.md` contient les détails et les références.

**À harmoniser :** `SECURITY.md` contient encore une mention de SQLAlchemy/SQLModel dans la règle d'injection SQL ; la stack retenue est Django ORM. Corriger cette mention dans un travail de documentation pertinent.

## 7. Façon de collaborer avec le propriétaire

Le propriétaire débute en programmation et veut apprendre tout en construisant le produit.

- Répondre en français simple, sans supposer une expérience préalable.
- Avancer par petites étapes concrètes ; expliquer quoi faire, dans quel fichier ou terminal, et pourquoi.
- Le propriétaire utilise Cursor pour le code. Lorsqu'il demande une modification, implémenter une tâche délimitée si demandé, puis expliquer simplement les fichiers et décisions concernés.
- Ne pas noyer la réponse dans une longue architecture ou des étapes futures non demandées. Limiter l'exploration du dépôt aux fichiers utiles à la tâche et garder les réponses concises pour maîtriser les coûts de tokens.
- Expliquer les commandes avant de proposer au propriétaire de les exécuter. Ne jamais demander ni afficher de mots de passe, jetons ou secrets.
- Ne pas créer plusieurs microservices ni toute l'infrastructure distribuée d'un seul coup. Construire d'abord le service Invitations par étapes compréhensibles.
- Avant les migrations de base, expliquer ce qu'elles changent et demander au propriétaire de les examiner ; ne pas exécuter une opération destructive ou effacer de données sans demande explicite.
- Lorsqu'une consigne ancienne du README contredit l'état actuel ci-dessus, ne pas repartir de zéro : vérifier les fichiers actuels et demander une clarification seulement si un choix réel est nécessaire.
