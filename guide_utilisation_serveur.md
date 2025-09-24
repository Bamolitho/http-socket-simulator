# Guide complet d'utilisation - Serveur HTTP Python

## Table des matières

1. [Installation et prérequis](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#installation-et-prérequis)
2. [Syntaxe de base](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#syntaxe-de-base)
3. [Configuration et options](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#configuration-et-options)
4. [Démarrage du serveur](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#démarrage-du-serveur)
5. [Structure des fichiers](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#structure-des-fichiers)
6. [Tests basiques](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#tests-basiques)
7. [Fonctionnalités avancées](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#fonctionnalités-avancées)
8. [Gestion des redirections](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#gestion-des-redirections)
9. [Requêtes POST](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#requêtes-post)
10. [Cache et optimisation](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#cache-et-optimisation)
11. [Logging et monitoring](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#logging-et-monitoring)
12. [Dépannage](https://claude.ai/chat/f8ad5d53-aa47-484c-b48a-16f88311a04f#dépannage)

------

## Installation et prérequis

### Prérequis système

- **Python 3.6+** (testé avec Python 3.8+)
- Aucune dépendance externe requise (utilise uniquement la bibliothèque standard)
- Ports disponibles (par défaut 8080)
- Permissions d'écriture pour les logs et fichiers

### Installation

```bash
# Télécharger le fichier
wget https://example.com/server_http.py
# ou
curl -O https://example.com/server_http.py

# Rendre exécutable
chmod +x server_http.py
```

------

## Syntaxe de base

### Commande minimale

```bash
python server_http.py
```

### Syntaxe complète

```bash
python server_http.py [PORT] [DOCUMENT_ROOT]
```

------

## Configuration et options

| Paramètre       | Description                        | Valeur par défaut | Exemple       |
| --------------- | ---------------------------------- | ----------------- | ------------- |
| `PORT`          | Port d'écoute du serveur           | `8080`            | `9000`        |
| `DOCUMENT_ROOT` | Répertoire racine des fichiers web | `www`             | `public_html` |

### Exemples de configuration

```bash
# Port par défaut, répertoire par défaut
python server_http.py

# Port personnalisé
python server_http.py 9000

# Port et répertoire personnalisés
python server_http.py 8080 public_html
```

------

## Démarrage du serveur

### 1. Démarrage simple

```bash
python server_http.py
```

**Sortie attendue** :

```
============================================================
[INFO] PYTHON HTTP/1.1 SERVER - SOCKET IMPLEMENTATION
============================================================
Configuration:
  • Address     : localhost
  • Port        : 8080
  • Directory   : www/
  • URL         : http://localhost:8080
  • Protocol    : HTTP/1.1
  • Features    : GET/POST, Redirections, Cache, Logging
============================================================
[INFO] Creating TCP socket...
[INFO] Binding to address localhost:8080...
[INFO] HTTP server started on http://localhost:8080
[INFO] Document root: /path/to/www
[INFO] Log file: server_access.log
[INFO] Press Ctrl+C to stop the server
```

### 2. Arrêt du serveur

- **Ctrl+C** : Arrêt propre du serveur
- Ferme toutes les connexions actives
- Sauvegarde les logs en cours

------

## Structure des fichiers

### Arborescence générée automatiquement

```
.
├── server_http.py          # Script principal
├── server_access.log       # Logs d'accès
├── redirections.json       # Configuration des redirections (optionnel)
├── logs/                   # Répertoire des logs
└── www/                    # Répertoire web racine
    ├── index.html         # Page d'accueil générée automatiquement
    ├── errors/            # Pages d'erreur personnalisées
    │   ├── 403.html       # Page d'erreur 403 Forbidden
    │   └── 500.html       # Page d'erreur 500 Internal Server Error
    └── files/             # Répertoire d'exemple pour tests
        ├── test.txt       # Fichier texte d'exemple
        ├── data.json      # Fichier JSON d'exemple
        └── cache-test.html # Page pour tests de cache
```

### Fichiers créés automatiquement

Le serveur crée automatiquement :

- **index.html** : Page d'accueil avec formulaires de test
- **errors/403.html** : Page d'erreur 403 personnalisée
- **errors/500.html** : Page d'erreur 500 personnalisée
- **files/** : Répertoire avec fichiers d'exemple

------

## Tests basiques

### 1. Tests avec navigateur web

#### Page d'accueil

```
http://localhost:8080/
```

**Affiche** : Page d'accueil avec liens de test et formulaire POST

#### Fichier spécifique

```
http://localhost:8080/index.html
```

#### Test 404

```
http://localhost:8080/fichier-inexistant.html
```

**Résultat** : Page d'erreur 404 avec design moderne

### 2. Tests avec cURL

#### Requête GET basique

```bash
curl -v http://localhost:8080/
```

#### Headers détaillés

```bash
curl -I http://localhost:8080/
```

**Affiche** : Headers HTTP/1.1 complets

#### Test de méthode non supportée

```bash
curl -X PUT http://localhost:8080/
```

**Résultat** : Erreur 405 Method Not Allowed

### 3. Tests avec telnet

```bash
telnet localhost 8080
```

Puis saisir :

```
GET / HTTP/1.1
Host: localhost

[ligne vide]
```

------

## Fonctionnalités avancées

### 1. Types MIME supportés

Le serveur reconnaît automatiquement 20+ types de fichiers :

| Extension     | Type MIME                   | Description       |
| ------------- | --------------------------- | ----------------- |
| `.html, .htm` | `text/html; charset=utf-8`  | Pages web         |
| `.css`        | `text/css`                  | Feuilles de style |
| `.js`         | `application/javascript`    | JavaScript        |
| `.json`       | `application/json`          | Données JSON      |
| `.txt`        | `text/plain; charset=utf-8` | Texte brut        |
| `.jpg, .jpeg` | `image/jpeg`                | Images JPEG       |
| `.png`        | `image/png`                 | Images PNG        |
| `.pdf`        | `application/pdf`           | Documents PDF     |
| `.mp3`        | `audio/mpeg`                | Audio MP3         |
| `.mp4`        | `video/mp4`                 | Vidéo MP4         |
| `.csv`        | `text/csv`                  | Données CSV       |
| `.xml`        | `application/xml`           | Documents XML     |

### 2. Listing de répertoires

Si un répertoire ne contient pas d'index.html :

```bash
curl http://localhost:8080/files/
```

**Génère** :

- Table HTML avec nom, type, taille, date de modification
- Liens cliquables vers fichiers et sous-répertoires
- Navigation avec lien parent (..)
- Tri intelligent (répertoires puis fichiers)

### 3. Gestion de la sécurité

#### Protection directory traversal

```bash
curl http://localhost:8080/../../../etc/passwd
```

**Résultat** : Erreur 403 Forbidden (accès bloqué)

#### Pages d'erreur personnalisées

- **403** : Charge `www/errors/403.html` si disponible
- **500** : Charge `www/errors/500.html` si disponible
- Fallback vers contenu généré si fichiers absents

------

## Gestion des redirections

### 1. Configuration des redirections

Le serveur supporte les redirections 301 (permanentes) configurées dans le code :

```python
self.redirections = {
    '/redirect-test': '/index.html',
    '/old-page.html': '/index.html',
    '/moved.html': '/files/test.txt'
}
```

### 2. Tests de redirections

#### Redirection simple

```bash
curl -v http://localhost:8080/redirect-test
```

**Comportement** :

- Retourne **301 Moved Permanently**
- Header `Location: /index.html`
- Page HTML avec meta-refresh automatique

#### Suivre les redirections

```bash
curl -L http://localhost:8080/redirect-test
```

**Résultat** : Suit automatiquement la redirection

### 3. Configuration avancée

Créer un fichier `redirections.json` :

```json
{
    "/ancien-site": "/nouveau-site.html",
    "/produit-123": "/catalogue/produit-123.html",
    "/contact": "/pages/contact.html"
}
```

------

## Requêtes POST

### 1. Formulaire de test intégré

La page d'accueil contient un formulaire de test :

```html
<form action="/form-handler" method="POST">
    <input type="text" name="name" value="John Doe">
    <input type="email" name="email" value="john@example.com">
    <textarea name="message">Test message</textarea>
    <button type="submit">Send POST Request</button>
</form>
```

### 2. Tests avec cURL

#### POST avec données de formulaire

```bash
curl -X POST -d "name=John&email=test@example.com&message=Hello" http://localhost:8080/form-handler
```

#### POST avec Content-Type spécifique

```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "param1=value1&param2=value2" \
  http://localhost:8080/form-handler
```

### 3. Réponse POST

Le serveur génère une page de confirmation contenant :

- Informations de la requête (chemin, méthode, headers)
- Données brutes reçues
- Données parsées du formulaire
- Taille du contenu

------

## Cache et optimisation

### 1. Headers de cache

Le serveur envoie automatiquement :

- **Last-Modified** : Date de dernière modification du fichier

- Cache-Control

   : Directives de cache selon le type de contenu

  - HTML : `no-cache, must-revalidate`
  - Autres : `public, max-age=3600` (cache 1 heure)

### 2. Support 304 Not Modified

#### Test de cache avec cURL

```bash
# Première requête (récupère Last-Modified)
curl -I http://localhost:8080/files/test.txt

# Deuxième requête avec If-Modified-Since
curl -H "If-Modified-Since: Thu, 01 Jan 2020 00:00:00 GMT" http://localhost:8080/files/test.txt
```

#### Test avec fichier récent

```bash
curl -H "If-Modified-Since: $(date -R)" http://localhost:8080/files/test.txt
```

**Résultat** : Retourne **304 Not Modified** si fichier non modifié

### 3. Optimisation des performances

- **Multi-threading** : Chaque client traité dans un thread séparé
- **Connection: close** : Évite les connexions persistantes pour simplifier
- **Buffer optimisé** : Lecture efficace des fichiers volumineux

------

## Logging et monitoring

### 1. Format des logs

Format Apache Common Log :

```
127.0.0.1 - - [21/Sep/2025:14:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234
```

Composants :

- **IP client** : Adresse du client
- **Timestamp** : Date/heure GMT
- **Requête** : Méthode + URL
- **Status** : Code de réponse HTTP
- **Taille** : Octets envoyés

### 2. Exemples de logs

```bash
tail -f server_access.log
```

**Sortie typique** :

```
127.0.0.1 - - [21/Sep/2025:14:30:45 +0000] "GET / HTTP/1.1" 200 3245
127.0.0.1 - - [21/Sep/2025:14:30:46 +0000] "GET /files/ HTTP/1.1" 200 1856
127.0.0.1 - - [21/Sep/2025:14:30:47 +0000] "GET /inexistant.html HTTP/1.1" 404 892
127.0.0.1 - - [21/Sep/2025:14:30:48 +0000] "POST /form-handler HTTP/1.1" 200 2134
127.0.0.1 - - [21/Sep/2025:14:30:49 +0000] "GET /redirect-test HTTP/1.1" 301 645
```

### 3. Monitoring en temps réel

#### Statistiques simples

```bash
# Compter les requêtes par heure
grep "$(date '+%d/%b/%Y:%H')" server_access.log | wc -l

# Top 10 des pages les plus demandées
awk '{print $7}' server_access.log | sort | uniq -c | sort -rn | head -10

# Codes d'erreur
awk '{print $9}' server_access.log | grep -E '^[45][0-9][0-9]' | sort | uniq -c
```

------

## Dépannage

### 1. Erreurs de démarrage

#### Port déjà utilisé

```
[ERROR] Error starting server: [Errno 98] Address already in use
```

**Solutions** :

- Changer de port : `python server_http.py 9000`
- Tuer le processus utilisant le port : `lsof -ti:8080 | xargs kill`
- Attendre que le port se libère

#### Permissions insuffisantes

```
[ERROR] Error starting server: [Errno 13] Permission denied
```

**Solutions** :

- Utiliser un port > 1024
- Exécuter avec sudo (non recommandé)
- Vérifier les permissions du répertoire

### 2. Erreurs de fichiers

#### Répertoire www inexistant

```
[INFO] index.html file created in www/
[INFO] Error pages created in www/errors/
```

**Résultat** : Le serveur crée automatiquement la structure

#### Fichier de log non accessible

```
[WARNING] Could not write to log file: [Errno 13] Permission denied
```

**Solution** : Vérifier les permissions d'écriture du répertoire courant

### 3. Erreurs de connexion

#### Timeout client

Le serveur ferme automatiquement les connexions inactives

#### Trop de connexions simultanées

Le serveur limite à 5 connexions en attente (paramètre `listen(5)`)

### 4. Debug et logs

#### Mode verbose (sortie console)

Les logs sont automatiquement affichés sur la console :

```
[CONNECTION] New client: 127.0.0.1:52341
[REQUEST] Received from 127.0.0.1:
--------------------------------------------------
GET /index.html HTTP/1.1
--------------------------------------------------
[RESPONSE] 200 OK - File sent: index.html (3245 bytes)
[CONNECTION] Connection closed with 127.0.0.1
```

#### Analyser les erreurs

```bash
# Erreurs dans les logs
grep "ERROR\|WARNING" server_access.log

# Codes d'erreur HTTP
grep -E "40[0-9]|50[0-9]" server_access.log
```

------

## Tests de charge et performance

### 1. Tests simples

#### Requêtes simultanées

```bash
for i in {1..10}; do
    curl http://localhost:8080/ &
done
wait
```

#### Mesure de performance

```bash
time curl http://localhost:8080/
```

### 2. Tests avec ab (Apache Bench)

```bash
# 100 requêtes, 10 simultanées
ab -n 100 -c 10 http://localhost:8080/

# Test de charge sur une page spécifique
ab -n 1000 -c 50 http://localhost:8080/files/
```

### 3. Scripts de test automatique

#### Test de fonctionnalités

```bash
#!/bin/bash
# test_server.sh

echo "=== Test du serveur HTTP ==="

# Test page d'accueil
curl -s http://localhost:8080/ > /dev/null && echo "[OK] Page d'accueil"

# Test 404
curl -s http://localhost:8080/inexistant.html | grep -q "404" && echo "[OK] Erreur 404"

# Test redirection
curl -s -I http://localhost:8080/redirect-test | grep -q "301" && echo "[OK] Redirection"

# Test POST
curl -s -X POST -d "test=data" http://localhost:8080/form-handler > /dev/null && echo "[OK] POST"

# Test listing répertoire
curl -s http://localhost:8080/files/ | grep -q "Index of" && echo "[OK] Directory listing"

echo "Tests terminés"
```

#### Test de robustesse

```bash
#!/bin/bash
# robustness_test.sh

# Tests normaux
curl -s http://localhost:8080/ > /dev/null
curl -s http://localhost:8080/files/ > /dev/null

# Tests d'erreur (doivent échouer proprement)
curl -s http://localhost:8080/inexistant.html > /dev/null
curl -s -X DELETE http://localhost:8080/ > /dev/null

# Test de sécurité
curl -s http://localhost:8080/../../../etc/passwd > /dev/null

echo "Tests de robustesse terminés"
```

------

## Configuration avancée

### 1. Modification des paramètres

Pour personnaliser le serveur, modifier les variables dans `main()` :

```python
HOST = '0.0.0.0'      # Écouter sur toutes les interfaces
PORT = 80             # Port HTTP standard (nécessite sudo)
DOCUMENT_ROOT = '/var/www/html'  # Répertoire système
```

### 2. Ajout de nouvelles redirections

Modifier le dictionnaire dans `_charger_redirections()` :

```python
self.redirections = {
    '/api/v1': '/api/v2',
    '/admin': '/login',
    '/docs': '/documentation.html'
}
```

### 3. Types MIME personnalisés

Ajouter des extensions dans `_obtenir_type_mime()` :

```python
types_mime = {
    # ... types existants ...
    '.webp': 'image/webp',
    '.woff2': 'font/woff2',
    '.md': 'text/markdown'
}
```

Ce guide couvre tous les aspects d'utilisation et de configuration du serveur HTTP Python. Le serveur est conçu pour être simple à utiliser tout en offrant des fonctionnalités professionnelles.