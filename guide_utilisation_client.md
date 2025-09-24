# Guide complet d'utilisation - Client HTTP Python

## Table des matières
1. [Installation et prérequis](#installation-et-prérequis)
2. [Syntaxe de base](#syntaxe-de-base)
3. [Options disponibles](#options-disponibles)
4. [Exemples pratiques](#exemples-pratiques)
5. [Tests de redirections](#tests-de-redirections)
6. [Tests avec serveur local](#tests-avec-serveur-local)
7. [Gestion des erreurs](#gestion-des-erreurs)
8. [Formats de sortie](#formats-de-sortie)
9. [Cas d'utilisation avancés](#cas-dutilisation-avancés)
10. [Dépannage](#dépannage)

---

## Installation et prérequis

### Prérequis système
- **Python 3.6+** (testé avec Python 3.8+)
- Aucune dépendance externe requise (utilise uniquement la bibliothèque standard)
- Accès réseau pour les requêtes externes

### Installation
```bash
# Télécharger le fichier
wget https://example.com/client_http.py
# ou
curl -O https://example.com/client_http.py

# Rendre exécutable
chmod +x client_http.py
```

---

## Syntaxe de base

### Commande minimale
```bash
python client_http.py <URL>
```

### Syntaxe complète
```bash
python client_http.py <URL> [--save FILE] [--no-headers] [--no-redirect] [--help]
```

---

## Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `URL` | URL cible (obligatoire) | `http://example.com` |
| `--save FILE` | Sauvegarder le contenu dans un fichier | `--save page.html` |
| `--no-headers` | Masquer les headers détaillés | `--no-headers` |
| `--no-redirect` | Ne pas suivre les redirections | `--no-redirect` |
| `--help, -h` | Afficher l'aide | `--help` |

### Détails des options

#### Format des URLs acceptées
- **Avec protocole** : `http://example.com`, `https://example.com`
- **Sans protocole** : `example.com` (assume http://)
- **Avec port** : `localhost:8080`, `example.com:443`
- **Avec chemin** : `example.com/page.html`
- **Avec paramètres** : `example.com/search?q=test&lang=fr`

#### Option `--save`
- Crée automatiquement les répertoires si nécessaire
- Ajoute un timestamp si aucune extension fournie
- Détecte automatiquement le type de contenu

---

## Exemples pratiques

### 1. Tests basiques

#### Requête simple
```bash
python client_http.py http://example.com
```
**Résultat attendu** : Affiche la réponse HTTP avec headers et contenu

#### Test avec domaine sans protocole
```bash
python client_http.py google.com
```
**Résultat** : Ajoute automatiquement `http://`

#### Test avec port personnalisé
```bash
python client_http.py localhost:8080
```

### 2. Sauvegarde de contenu

#### Sauvegarder une page web
```bash
python client_http.py http://example.com --save example.html
```

#### Sauvegarder avec nom automatique
```bash
python client_http.py http://httpbin.org/html --save page
```
**Résultat** : Crée `page_20240921_143052.html`

#### Sauvegarder dans un répertoire
```bash
python client_http.py http://example.com --save downloads/example.html
```
**Note** : Crée le répertoire `downloads/` automatiquement

### 3. Tests avec différents types de contenu

#### Page HTML
```bash
python client_http.py http://httpbin.org/html
```
**Affiche** : Titre, nombre de liens, images, aperçu du texte

#### Données JSON
```bash
python client_http.py http://httpbin.org/json
```
**Affiche** : Structure JSON, clés principales

#### Texte brut
```bash
python client_http.py http://httpbin.org/robots.txt
```
**Affiche** : Aperçu des premières lignes

---

## Tests de redirections

### 1. Redirection simple
```bash
python client_http.py httpbin.org/redirect/1
```
**Comportement** :
```
Step 1: 302 Found [REDIRECT] - httpbin.org/redirect/1
Step 2: 200 OK [FINAL] - httpbin.org/get
Total redirections followed: 1
```

### 2. Chaîne de redirections
```bash
python client_http.py httpbin.org/redirect/3
```
**Comportement** :
```
Step 1: 302 Found [REDIRECT] - httpbin.org/redirect/3
Step 2: 302 Found [REDIRECT] - httpbin.org/relative-redirect/2
Step 3: 302 Found [REDIRECT] - httpbin.org/relative-redirect/1
Step 4: 200 OK [FINAL] - httpbin.org/get
Total redirections followed: 3
```

### 3. Redirection sans suivi
```bash
python client_http.py httpbin.org/redirect/3 --no-redirect
```
**Comportement** : S'arrête à la première réponse 302

### 4. Types de redirections testables

#### Redirection relative
```bash
python client_http.py httpbin.org/relative-redirect/2
```

#### Redirection absolue
```bash
python client_http.py httpbin.org/absolute-redirect/2
```

#### Redirection vers URL externe
```bash
python client_http.py httpbin.org/redirect-to?url=http://example.com
```

#### Test de limite de redirections
```bash
python client_http.py httpbin.org/redirect/10
```
**Résultat** : S'arrête après 5 redirections (limite par défaut)

---

## Tests avec serveur local

### 1. Démarrer un serveur local (pour tester)
```bash
# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080

# Ou avec un serveur web quelconque sur le port 8080
```

### 2. Tests avec le serveur local

#### Page d'accueil
```bash
python client_http.py localhost:8080
```

#### Fichier spécifique
```bash
python client_http.py localhost:8080/index.html
```

#### Fichier inexistant (test 404)
```bash
python client_http.py localhost:8080/nonexistent.html
```

#### Avec IP au lieu du nom d'hôte
```bash
python client_http.py 127.0.0.1:8080
```

---

## Gestion des erreurs

### 1. Codes de statut courants

#### Succès (2xx)
```bash
python client_http.py httpbin.org/status/200  # OK
python client_http.py httpbin.org/status/201  # Created
python client_http.py httpbin.org/status/204  # No Content
```

#### Redirections (3xx)
```bash
python client_http.py httpbin.org/status/301  # Moved Permanently
python client_http.py httpbin.org/status/302  # Found
python client_http.py httpbin.org/status/304  # Not Modified
```

#### Erreurs client (4xx)
```bash
python client_http.py httpbin.org/status/400  # Bad Request
python client_http.py httpbin.org/status/401  # Unauthorized
python client_http.py httpbin.org/status/404  # Not Found
```

#### Erreurs serveur (5xx)
```bash
python client_http.py httpbin.org/status/500  # Internal Server Error
python client_http.py httpbin.org/status/503  # Service Unavailable
```

### 2. Gestion des timeouts
```bash
python client_http.py httpbin.org/delay/2   # Délai de 2 secondes
python client_http.py httpbin.org/delay/15  # Risque de timeout
```

### 3. Tests de domaines invalides
```bash
python client_http.py http://domaine-inexistant.test
# Résultat: [ERROR] Cannot resolve domaine-inexistant.test
```

---

## Formats de sortie

### 1. Sortie standard

#### En-tête de requête
```
============================================================
[INFO] HTTP CLIENT REQUEST
============================================================
Target URL: http://example.com
============================================================
```

#### Informations de connexion
```
[INFO] Request attempt 1
[INFO] Connecting to example.com:80
[INFO] Requested path: /
[INFO] Creating TCP socket...
[INFO] DNS resolution for example.com...
[INFO] example.com -> 93.184.216.34
[INFO] Connecting to example.com:80...
[SUCCESS] Connection established with example.com:80
```

#### Requête envoyée
```
--------------------------------------------------
REQUEST SENT:
--------------------------------------------------
GET / HTTP/1.1\r\n
Host: example.com\r\n
User-Agent: Client-HTTP-Python/1.1\r\n
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n
Accept-Language: en-US,en;q=0.5\r\n
Accept-Encoding: identity\r\n
Connection: close\r\n
Cache-Control: no-cache\r\n
\r\n
--------------------------------------------------
```

#### Réponse reçue
```
============================================================
[INFO] HTTP RESPONSE RECEIVED
============================================================
Status    : [SUCCESS] 200 OK
Version   : HTTP/1.1
Size      : 1256 bytes
Explanation : OK - Request succeeded
```

### 2. Headers principaux
```
[INFO] MAIN HEADERS:
----------------------------------------
Server          : ECS (dcb/7EA3)
Content-Type    : text/html; charset=UTF-8
Content-Length  : 1256
Date            : Sun, 21 Sep 2025 14:30:45 GMT
Last-Modified   : Thu, 17 Oct 2019 07:18:26 GMT
```

### 3. Aperçu du contenu selon le type

#### HTML
```
[INFO] HTML PREVIEW:
------------------------------
Title : Example Domain
Links found       : 1
Images found      : 0  
Paragraphs        : 2

Extracted text:
"Example Domain This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination..."
```

#### JSON
```
[INFO] JSON PREVIEW:
------------------------------
Type : JSON Object (4 keys)
Keys : ['args', 'headers', 'origin', 'url']
```

#### Texte
```
[INFO] TEXT PREVIEW:
------------------------------
Number of lines : 15
 1: User-agent: *
 2: Disallow: /deny
 3: 
 4: User-agent: Googlebot
 5: Disallow:
... (10 additional lines)
```

---

## Cas d'utilisation avancés

### 1. Tests de performance

#### Mesurer le temps de réponse
```bash
time python client_http.py http://httpbin.org/get
```

#### Test avec délai artificiel
```bash
python client_http.py httpbin.org/delay/5
```

### 2. Tests de headers spéciaux

#### Tester la compression (non supportée)
```bash
python client_http.py httpbin.org/gzip
```

#### Tester les cookies
```bash
python client_http.py httpbin.org/cookies/set/session/abc123
```

#### Tester l'authentification
```bash
python client_http.py httpbin.org/basic-auth/user/pass
```

### 3. URLs avec paramètres complexes
```bash
# URL avec paramètres GET
python client_http.py "httpbin.org/get?param1=value1&param2=value with spaces"

# URL avec caractères spéciaux (encoder manuellement)
python client_http.py "httpbin.org/get?query=test%20search"
```

### 4. Tests de contenu volumineux
```bash
# Télécharger une image
python client_http.py httpbin.org/image/png --save image.png

# Télécharger du HTML volumineux
python client_http.py httpbin.org/html --save large.html
```

### 5. Chaînage de commandes
```bash
# Tester plusieurs URLs en séquence
python client_http.py httpbin.org/status/200 && \
python client_http.py httpbin.org/status/404 && \
python client_http.py httpbin.org/redirect/2
```

---

## Dépannage

### 1. Erreurs courantes

#### "Cannot resolve hostname"
```bash
python client_http.py http://domaine-inexistant.example
# [ERROR] Cannot resolve domaine-inexistant.example: [Errno -2] Name or service not known
```
**Solution** : Vérifier l'orthographe du domaine et la connectivité réseau

#### "Connection timeout"
```bash
python client_http.py http://192.168.1.999:8080
# [ERROR] Connection timeout after 10s
```
**Solution** : Vérifier que le serveur est accessible et le port ouvert

#### "Connection refused"
```bash
python client_http.py http://localhost:9999
# [ERROR] Connection error: [Errno 111] Connection refused
```
**Solution** : Vérifier qu'un serveur écoute sur ce port

### 2. Problèmes de parsing

#### URL malformée
```bash
python client_http.py "://malformed-url"
# [ERROR] Cannot parse URL '://malformed-url'
```
**Solution** : Utiliser une URL valide avec protocole

#### Réponse malformée
```bash
# Si le serveur envoie une réponse non-standard
# [ERROR] Malformed HTTP response
```
**Solution** : Tester avec un serveur HTTP standard

### 3. Problèmes de redirection

#### Boucle de redirection
```bash
# Certains serveurs mal configurés peuvent créer des boucles
# [WARNING] Maximum redirections (5) reached
```
**Solution** : Utiliser `--no-redirect` pour voir la première réponse

#### Redirection vers HTTPS
```bash
python client_http.py http://github.com
# Peut rediriger vers HTTPS (non supporté par ce client)
```
**Solution** : Utiliser directement l'URL HTTPS si elle est connue

### 4. Problèmes de sauvegarde

#### Permissions insuffisantes
```bash
python client_http.py http://example.com --save /root/page.html
# [ERROR] Cannot save /root/page.html: [Errno 13] Permission denied
```
**Solution** : Utiliser un répertoire accessible en écriture

#### Espace disque insuffisant
```bash
# [ERROR] Cannot save large_file.html: [Errno 28] No space left on device
```
**Solution** : Libérer de l'espace disque

### 5. Debug et logs

#### Activer le mode verbose (modification manuelle du code)
Modifier la variable `timeout_connexion` pour ajuster les timeouts :
```python
self.timeout_connexion = 30  # Augmenter à 30 secondes
```

#### Capturer la sortie pour analyse
```bash
python client_http.py http://example.com > output.log 2>&1
```

#### Test avec différents User-Agents
Modifier le header User-Agent dans `_construire_requete_get()` :
```python
headers += f"User-Agent: Mozilla/5.0 (compatible; TestBot/1.0)\r\n"
```

---

## Scripts utiles pour les tests

### 1. Script de test automatique
```bash
#!/bin/bash
# test_client.sh

echo "=== Tests basiques ==="
python client_http.py http://httpbin.org/get
python client_http.py http://example.com

echo "=== Tests de redirections ==="
python client_http.py httpbin.org/redirect/1
python client_http.py httpbin.org/redirect/3

echo "=== Tests d'erreurs ==="
python client_http.py httpbin.org/status/404
python client_http.py httpbin.org/status/500

echo "Tests terminés"
```

### 2. Test de performance
```bash
#!/bin/bash
# performance_test.sh

echo "Test de performance - 10 requêtes"
for i in {1..10}; do
    echo "Requête $i:"
    time python client_http.py http://httpbin.org/get > /dev/null
done
```

### 3. Test de robustesse
```bash
#!/bin/bash
# robustness_test.sh

# URLs valides
python client_http.py http://httpbin.org/get
python client_http.py google.com
python client_http.py localhost:8080

# URLs invalides (doivent échouer proprement)
python client_http.py http://domaine-inexistant.test
python client_http.py http://192.168.999.999
python client_http.py "://url-malformée"
```

Ce guide couvre tous les aspects d'utilisation du client HTTP. Pour des tests plus spécifiques, vous pouvez adapter les exemples selon vos besoins.