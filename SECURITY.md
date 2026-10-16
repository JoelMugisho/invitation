# Règles de sécurité du projet

Ce fichier est la base de sécurité à consulter avant de concevoir ou modifier une fonctionnalité. Cursor doit appliquer les règles pertinentes, expliquer les protections proposées et signaler les décisions qui nécessitent un choix du propriétaire du projet. La sécurité doit être mise en place progressivement, au moment où chaque surface est créée ; ne pas ajouter des couches incomprises ou des middleware inutiles.

Ces règles réduisent les risques, mais ne constituent ni une certification ni une garantie d'absence de vulnérabilités. Le Top 10 OWASP est un document de sensibilisation, pas une liste exhaustive de contrôles.

## Principes obligatoires

- Sécurité côté serveur : toute validation métier, authentification et décision d'autorisation doit être faite côté API. L'interface ne constitue jamais une barrière de sécurité.
- Refus par défaut : protéger chaque route non publique et n'accorder que les permissions nécessaires.
- Isolation des comptes et événements : chaque requête doit vérifier que l'utilisateur peut accéder à l'objet demandé. Ne jamais se fier à un UUID, `organisateur_ref`, `tenant_id` ou identifiant reçu du navigateur comme preuve d'autorisation.
- Validation à l'entrée : utiliser des schémas typés et des contraintes de taille/format/valeur côté serveur. Refuser les champs inattendus lorsque c'est approprié. Valider aussi les réponses des services externes.
- Messages d'erreur sûrs : réponses génériques en production, sans trace d'exception, secret, requête SQL, chemin local ou détail interne. Garder les détails uniquement dans des journaux protégés.
- Défense en profondeur : les middleware et en-têtes sont utiles, mais ne remplacent jamais l'autorisation par ressource, la validation des données ou une conception sûre.
- Ne pas prétendre qu'une fonctionnalité est sécurisée sans avoir mis en place et vérifié ses contrôles.

## OWASP Top 10

Utiliser la version publiée la plus récente du Top 10 OWASP comme guide de sensibilisation. Au moment de la rédaction, la version courante est **OWASP Top 10:2025** :

1. A01 Contrôle d'accès défaillant
2. A02 Mauvaise configuration de sécurité
3. A03 Défaillances de la chaîne d'approvisionnement logicielle
4. A04 Défaillances cryptographiques
5. A05 Injection
6. A06 Conception non sécurisée
7. A07 Défaillances d'authentification
8. A08 Défaillances d'intégrité logicielle ou des données
9. A09 Défaillances de journalisation et d'alerte de sécurité
10. A10 Mauvaise gestion des conditions exceptionnelles

Vérifier le site OWASP au démarrage d'une nouvelle phase de sécurité : https://owasp.org/Top10/2025/ .

## API, middleware et configuration HTTP

- HTTPS seulement en production. Configurer TLS au niveau du point d'entrée de confiance ; activer HSTS uniquement sur les domaines HTTPS de production après vérification de la configuration.
- Utiliser une liste explicite d'origines CORS autorisées par environnement. Ne pas combiner origines génériques (`*`) et cookies/identifiants. CORS n'est pas un mécanisme d'authentification.
- Ajouter des en-têtes pertinents pour le navigateur au point d'entrée web : `X-Content-Type-Options: nosniff`, une politique `Content-Security-Policy` adaptée à l'application, `frame-ancestors` ou `X-Frame-Options`, et une `Referrer-Policy` prudente. Ne pas copier aveuglément une politique qui bloque les besoins légitimes de la PWA.
- Pour les réponses sensibles, définir une politique de cache adaptée, souvent `Cache-Control: no-store`. Ne pas mettre en cache des données privées dans le service worker ou le Cache API sans analyse explicite.
- Middleware possibles à mesure que l'API grandit : identifiant de requête, gestion cohérente des erreurs, en-têtes de sécurité, CORS strict et limitation de débit. Garder les middleware simples, ordonnés et documentés. Ne pas y cacher les règles d'autorisation propres à une ressource.
- Limiter la taille des requêtes, les délais, la pagination et les opérations coûteuses. Mettre des limites de débit sur la connexion, la récupération de mot de passe, l'envoi de messages et les endpoints sensibles.
- Ne jamais mettre mot de passe, jeton, clé API ou donnée sensible dans une URL. Ne pas exposer les routes de diagnostic, administration ou métriques sur Internet sans contrôle d'accès.
- N'accepter que les méthodes HTTP nécessaires ; les requêtes GET ne doivent jamais modifier l'état.

## Authentification, sessions et CSRF

- Ne jamais inventer son propre protocole de session, format de jeton ou algorithme cryptographique. Choisir une bibliothèque ou un fournisseur maintenu, après avoir compris le modèle de menace.
- Si l'authentification utilise des cookies automatiquement envoyés par le navigateur, protéger chaque action qui change l'état contre CSRF : jeton CSRF validé côté serveur, cookies `Secure`, `HttpOnly` et `SameSite` approprié, et vérification prudente de `Origin`/Fetch Metadata en défense supplémentaire. SameSite seul n'est pas une protection universelle.
- Ne pas utiliser de GET pour une action qui modifie des données. XSS peut neutraliser de nombreuses protections CSRF : traiter les deux risques.
- Si un jeton Bearer est utilisé dans l'en-tête `Authorization`, ne pas le conserver dans `localStorage` sans analyse du risque XSS ; les mécanismes de stockage et de renouvellement doivent être conçus explicitement.
- Vérifier expiration, audience, émetteur et algorithme attendu des jetons. Ne pas accepter l'algorithme indiqué par un jeton sans liste autorisée. Prévoir révocation/rotation selon le modèle retenu.
- Protéger les tentatives de connexion contre l'automatisation et l'énumération de comptes ; ne pas révéler si une adresse email existe.
- Les comptes ayant des privilèges élevés devraient pouvoir utiliser MFA. Les autorisations sont vérifiées à chaque action et dans chaque service concerné.

## CSRF, XSS et injection

### CSRF

- Appliquer les règles de la section authentification si les navigateurs envoient automatiquement des cookies.
- Vérifier le jeton CSRF côté serveur sur les opérations mutantes. Ne pas considérer un en-tête personnalisé seul ou CORS seul comme une protection suffisante.

### XSS

- Afficher les valeurs fournies par l'utilisateur comme du texte via les mécanismes d'échappement par défaut de React.
- Éviter `dangerouslySetInnerHTML`, `eval`, les scripts construits depuis des données et les manipulations DOM non sûres. Si du HTML enrichi est indispensable, utiliser un assainisseur maintenu avec une politique allowlist définie.
- Valider les URL avant de les utiliser comme liens ou ressources ; éviter les schémas dangereux comme `javascript:`.
- Déployer une CSP adaptée comme protection supplémentaire, sans la considérer comme un substitut à l'encodage/assainissement.

### Injection SQL et autres injections

- Utiliser les requêtes paramétrées et l'ORM SQLAlchemy/SQLModel de manière sûre. Ne jamais concaténer une entrée utilisateur dans une requête SQL.
- Pour les noms de colonnes, tris, tables ou autres éléments SQL qui ne peuvent pas être paramétrés, utiliser une liste blanche explicite de choix autorisés.
- N'exécuter aucun shell, template, expression, LDAP ou langage de requête en interpolant directement une entrée utilisateur.
- Échapper/encoder les données selon leur contexte de sortie ; la validation seule n'est pas une défense contre toutes les injections.

## Données, mots de passe et cryptographie

- En transit : TLS/HTTPS. Pour les appels entre services, authentifier le service appelant et chiffrer les communications en production ; ne pas faire confiance à un identifiant fourni par le client comme identité inter-service.
- Au repos : utiliser le chiffrement du fournisseur d'infrastructure pour les volumes, bases et sauvegardes. Identifier les données particulièrement sensibles ; ajouter un chiffrement applicatif de champs uniquement avec une stratégie de clés et de rotation comprise.
- Les mots de passe ne sont jamais chiffrés de façon réversible et ne sont jamais stockés en clair. Utiliser une fonction dédiée et maintenue de hachage de mots de passe (préférer Argon2id lorsqu'elle est prise en charge), avec sel géré par la bibliothèque. Ne pas concevoir son propre hachage.
- Utiliser des algorithmes et tailles de clés actuels via des bibliothèques maintenues. Ne pas inventer d'algorithme, réutiliser un nonce/IV qui doit être unique, ou intégrer des clés dans le code.
- Séparer les clés des données chiffrées et les gérer dans un gestionnaire de secrets/KMS en production. Documenter propriétaire, rotation, accès et procédure de révocation. Ne pas journaliser les clés ou données en clair.
- Utiliser des valeurs aléatoires cryptographiquement sûres pour les secrets et tokens. Pour les QR codes, préférer un identifiant opaque non prédictible ; ne pas y intégrer nom, email, téléphone ou données personnelles. Vérifier le statut et l'usage unique côté serveur.
- Ne pas stocker les données de carte de paiement ; déléguer le traitement à l'agrégateur et respecter ses exigences de sécurité.

## Microservices et isolation des données

- Chaque service est propriétaire de ses données et de sa base. Aucune clé étrangère ne traverse une frontière de service ; les références externes sont des UUID `_ref` vérifiés par un appel ou un événement de confiance.
- Authentifier les appels service-à-service. Transmettre seulement les informations nécessaires, protéger les secrets d'intégration et appliquer le moindre privilège réseau et base de données.
- Une passerelle API ne suffit pas : chaque service vérifie l'autorisation requise localement, notamment l'accès à l'événement, l'organisateur et le rôle du Middle user.
- Ne jamais faire confiance à `organisateur_ref`, `middle_user_ref`, `tenant_id` ou aux rôles envoyés par le navigateur. Les dériver d'une identité authentifiée et vérifier leur association aux ressources.
- Les consommateurs d'événements doivent vérifier l'origine, le schéma, l'idempotence et les droits associés. Ne pas considérer une file ou un message comme fiable par défaut.
- Pour le check-in, empêcher les doubles utilisations de QR de façon atomique dans la base ; journaliser le résultat et l'identité vérifiée de l'agent.

## Secrets, journaux et dépendances

- Aucun secret, jeton, mot de passe, clé privée ou fichier `.env` réel dans Git. Fournir seulement un fichier d'exemple avec des valeurs fictives. Si un secret est exposé, le révoquer et le renouveler.
- En production, préférer un gestionnaire de secrets aux variables statiques ou fichiers copiés dans l'image.
- Les journaux ne doivent contenir ni mot de passe, cookie, jeton, secret, données de paiement ni données personnelles inutiles. Nettoyer les valeurs utilisateur pour éviter l'injection de lignes de journal.
- Journaliser les événements de sécurité utiles (connexion, changements de rôle, accès sensibles, échecs répétés) avec accès contrôlé, rétention définie et alertes appropriées. Ne pas exposer les journaux aux utilisateurs.
- Garder les dépendances nécessaires uniquement, utiliser des fichiers de verrouillage, mettre à jour régulièrement et examiner les alertes de vulnérabilité et la provenance des paquets.
- Exécuter les services avec des comptes non privilégiés. Ne pas laisser les modes debug, documentation administrative ou identifiants par défaut actifs en production.

## Fichiers, URL et disponibilité

- Restreindre les types, tailles et noms des fichiers téléversés ; ne jamais faire confiance au nom ou au type MIME fourni par le navigateur. Stocker hors du répertoire exécutable et contrôler l'accès au téléchargement.
- Si le serveur récupère une URL fournie par un utilisateur (image, webhook, import), protéger contre SSRF : limiter schémas et destinations, bloquer les plages internes et vérifier les redirections/résolutions DNS.
- Prévoir limites de débit, tailles maximales, pagination, délais, limites de concurrence et opérations idempotentes pour réduire les abus et dénis de service.
- Protéger les sauvegardes comme la base active : chiffrement, permissions minimales, rétention et exercices de restauration.

## Règle de mise en œuvre pour Cursor

À chaque nouvelle fonctionnalité :

1. Expliquer les données sensibles, les rôles et les actions possibles avant de coder.
2. Identifier les risques pertinents de ce fichier et les contrôles à appliquer à cette étape.
3. Faire valider côté serveur les entrées, l'identité et l'autorisation sur la ressource.
4. Expliquer la protection ajoutée et ses limites ; ne pas prétendre qu'une seule middleware résout CSRF, XSS, injection ou contrôle d'accès.
5. Proposer des vérifications ciblées des cas autorisés et refusés, et demander à l'apprenant de les exécuter et comprendre.

Ne pas ajouter toutes les protections dans la première route d'exercice. Commencer par des pratiques sûres dès qu'une surface concernée apparaît et renforcer les contrôles avant chaque mise en production.

## Références OWASP

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- [REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [HTTP Security Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
