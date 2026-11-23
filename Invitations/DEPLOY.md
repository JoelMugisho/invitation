# Déploiement — mugi.eraste.tech (Nginx du serveur)

Le site tourne dans Docker sur `127.0.0.1:8000`. **Nginx du serveur** gère le domaine et le HTTPS. Ce n'est pas une certification de sécurité production.

## 1. DNS

- type **A** : `mugi.eraste.tech` → IP publique du serveur

## 2. Fichier `.env` (vrais réglages)

Sur le serveur, le fichier `Invitations/.env` contient les vraies valeurs (jamais dans git, jamais dans `.env.example`).

Vérifier au minimum :

- `ALLOWED_HOSTS=mugi.eraste.tech,127.0.0.1,localhost`
- `CSRF_TRUSTED_ORIGINS=https://mugi.eraste.tech`
- `USE_X_FORWARDED_HOST=1`
- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY` longue et aléatoire
- mots de passe Postgres forts

## 3. Lancer l'app

```bash
cd Invitations
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
curl -s http://127.0.0.1:8000/health
```

Attendu : `{"status":"ok","service":"invitations"}`.

## 4. Nginx

1. Copier `deploy/nginx-mugi.eraste.tech.conf` vers `/etc/nginx/sites-available/mugi.eraste.tech`
2. Activer le site (`sites-enabled`)
3. Décommenter / brancher les chemins SSL (Certbot ou certificats existants)
4. `nginx -t && systemctl reload nginx`
5. Certificat si besoin : `certbot --nginx -d mugi.eraste.tech`

Nginx doit transmettre `Host`, `X-Forwarded-Proto` et `X-Forwarded-For` (déjà dans le fichier d'exemple).

## 5. Mises à jour

```bash
cd Invitations
git pull
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

## 6. Hors scope

- Pas de `migrate` Django pour l'instant
- Pas d'authentification utilisateurs
- Coordonnées du pied de page = exemples de maquette
