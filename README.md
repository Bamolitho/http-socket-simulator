# Implémentation HTTP avec Sockets Python

## Objectifs 

Ce projet implémente le protocole HTTP (basé sur la RFC 2616) en **Python pur** avec des **sockets TCP/IP**, sans utiliser de frameworks web (Flask, Django, etc.).

### Concepts étudiés :
- **Protocole HTTP** : Structure des requêtes et réponses HTTP
- **Sockets TCP/IP** : Communication réseau bas niveau
- **Parsing de protocoles texte** : Analyse et construction des messages HTTP
- **Architecture client-serveur** : Interaction entre client et serveur
- **Gestion des erreurs réseau** : Timeouts, connexions fermées, etc.

## Structure du projet

```
http-socket-simulator/
├── server_http.py     # Serveur HTTP avec sockets
├── structure_serveur.md
├── guide_utilisation_serveur.md
├
├── client_http.py     # Client HTTP avec sockets  
├── structure_client.md
├── guide_utilisation_client.md
├
├── README.md          
├── requirements.txt  # Les librairies Python utilisés, aucune installation nécessaire
├── logs/ 			  # Dossier pour sauvegarder les logs serveur (crée automatiquement)
└── www/              # Répertoire des fichiers web (créé automatiquement)
    └── index.html    # Page d'accueil par défaut
    
 # Note : Voir les guides d'utilisation pour compléter cette structure
```

## Installation et lancement

### Prérequis
- Python 3.6+ (aucune dépendance externe)
- Système d'exploitation : Windows, Linux, macOS

### Installation
```bash
# 1. Télécharger ou cloner le projet
git clone <url-du-projet>
cd http-socket-simulator

# 2. Vérifier Python
python3 --version

# 3. (Optionnel) Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 4. Installer les dépendances (aucune dans ce cas)
pip install -r requirements.txt
```



## Utilisation

### 1. Démarrer le serveur HTTP

```bash
# Démarrage basique (port 8080 par défaut)
python server_http.py

# Spécifier un port personnalisé
python server_http.py 9000

# Spécifier port et répertoire web
python server_http.py 8080 public_html
```

**Sortie attendue :**

```
============================================================
SERVEUR HTTP PYTHON - IMPLÉMENTATION SOCKET
============================================================
Configuration :
  • Adresse     : localhost
  • Port        : 8080 
  • Répertoire  : www/
  • URL         : http://localhost:8080
============================================================
[INFO] Fichier index.html créé dans www/
[INFO] Création de la socket TCP...
[INFO] Liaison à l'adresse localhost:8080...
[INFO] Serveur HTTP démarré sur http://localhost:8080
[INFO] Répertoire racine : /path/to/project/www
[INFO] Appuyez sur Ctrl+C pour arrêter le serveur
```

### 2. Utiliser le client HTTP

```bash
# Requête basique vers un site web
python client_http.py http://example.com/

# Requête vers le serveur local
python client_http.py localhost:8080

# Sauvegarder la réponse dans un fichier
python client_http.py http://example.com/ --save page.html

# Requête sans afficher tous les headers
python client_http.py localhost:8080 --no-headers

# Voir l'aide complète
python client_http.py --help
```



## Scénario de test complet

### Étape 1 : Démarrer le serveur
```bash
# Terminal 1
python server_http.py
```

### Étape 2 : Tester avec le client Python
```bash
# Terminal 2 - Test de la page d'accueil
python client_http.py localhost:8080

# Test d'une page inexistante (404)
python client_http.py localhost:8080/fichier-inexistant.html

# Test avec sauvegarde
python client_http.py localhost:8080/index.html --save test_local.html
```

### Étape 3 : Tester avec un navigateur web
Ouvrir dans votre navigateur :
- http://localhost:8080
- http://localhost:8080/index.html  
- http://localhost:8080/page-404.html (pour voir l'erreur 404)

### Étape 4 : Tester avec curl
```bash
# Requête GET basique
curl -v http://localhost:8080/

# Requête HEAD (headers seulement)
curl -I http://localhost:8080/

# Test 404
curl -v http://localhost:8080/inexistant.html
```

### Étape 5 : Tester avec telnet (manuel)
```bash
# Se connecter au serveur
telnet localhost 8080

# Puis taper manuellement la requête HTTP :
GET / HTTP/1.1
Host: localhost

# (Appuyer sur Entrée deux fois)
```

## Format des messages HTTP implémentés

### Requête HTTP (Client → Serveur)
```
GET /index.html HTTP/1.0\r\n
Host: localhost\r\n
User-Agent: Client-HTTP-Python/1.0\r\n
Accept: text/html,text/plain,*/*\r\n
Connection: close\r\n
\r\n
```

### Réponse HTTP (Serveur → Client)
```
HTTP/1.0 200 OK\r\n
Date: Mon, 15 Jan 2025 14:30:00 GMT\r\n
Server: ServeurHTTP-Python/1.0\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 1234\r\n
Connection: close\r\n
\r\n
<!DOCTYPE html>
<html>...
```



## Fonctionnalités implémentées

### Serveur HTTP (`server_http.py`)

✅ **Socket TCP/IP** : Écoute sur un port configurable  
✅ **Multi-threading** : Gestion de plusieurs clients simultanés  
✅ **Parsing requêtes** : Analyse des requêtes HTTP GET  
✅ **Serving de fichiers** : Service de fichiers statiques  
✅ **Gestion d'erreurs** : Codes 400, 404, 405, 500  
✅ **Headers HTTP** : Date, Server, Content-Type, Content-Length  
✅ **Types MIME** : Détection automatique (.html, .css, .js, .jpg, etc.)  
✅ **Sécurité basique** : Protection contre directory traversal  
✅ **Logs détaillés** : Affichage de toutes les requêtes

### Client HTTP (`client_http.py`)

✅ **Connexion TCP** : Établissement de connexion avec timeout  
✅ **Construction requêtes** : Formatage HTTP/1.0 correct  
✅ **Parsing réponses** : Analyse complète des réponses HTTP  
✅ **Gestion codes statut** : Explication des codes 200, 404, 500, etc.  
✅ **Affichage intelligent** : Aperçu HTML, JSON, texte  
✅ **Sauvegarde fichiers** : Export du contenu reçu  
✅ **Support URLs** : Parsing d'URLs complètes avec ports  
✅ **Gestion d'erreurs** : Timeouts, erreurs réseau, DNS



## Exemples de sorties

### Serveur HTTP - Requête reçue
```
[CONNEXION] Nouveau client : 127.0.0.1:54321
[REQUÊTE] Reçue de 127.0.0.1:
──────────────────────────────────────────────────
GET /index.html HTTP/1.0
──────────────────────────────────────────────────
[RÉPONSE] 200 OK - Fichier envoyé : index.html (1245 octets)
[CONNEXION] Connexion fermée avec 127.0.0.1
```

### Client HTTP - Réponse analysée
```
============================================================
RÉPONSE HTTP REÇUE
============================================================
Statut    : 200 OK (SUCCÈS)
Version   : HTTP/1.0
Taille    : 1456 octets
Explication : OK - La requête a réussi

HEADERS PRINCIPAUX :
────────────────────────────────────────
Server          : ServeurHTTP-Python/1.0
Content-Type    : text/html; charset=utf-8
Content-Length  : 1245
Date            : Mon, 15 Jan 2025 14:30:00 GMT

CONTENU :
────────────────────────────────────────
Taille du contenu : 1245 octets
Type de contenu   : text/html; charset=utf-8

APERÇU HTML :
──────────────────────────────
Titre : Serveur HTTP Python
Liens trouvés     : 3
Images trouvées   : 0
Paragraphes       : 4
============================================================
```

## Tests et débogage

### Tests unitaires manuels

#### Test 1 : Requête GET réussie
```bash
python client_http.py localhost:8080
# Attendu : Code 200, contenu HTML affiché
```

#### Test 2 : Erreur 404
```bash
python client_http.py localhost:8080/inexistant.html
# Attendu : Code 404, page d'erreur HTML
```

#### Test 3 : Sauvegarde de fichier
```bash
python client_http.py localhost:8080 --save test.html
ls -la test.html
# Attendu : Fichier créé avec le contenu HTML
```

#### Test 4 : Test avec un vrai site web
```bash
python client_http.py http://httpbin.org/get
# Attendu : Réponse JSON avec informations de la requête
```

### Débogage commun

**Problème** : `[Errno 98] Address already in use`  
**Solution** : 
```bash
# Arrêter le processus utilisant le port
sudo netstat -tlnp | grep :8080
kill -9 <PID>
# ou changer de port
python server_http.py 9000
```

**Problème** : `Connection refused`  
**Solution** : Vérifier que le serveur est démarré sur le bon port

**Problème** : `Name or service not known`  
**Solution** : Vérifier la résolution DNS ou utiliser une IP

## Extensions possibles

### Fonctionnalités avancées à implémenter :
- **HTTP/1.1** : Keep-alive, chunked encoding
- **Méthodes supplémentaires** : POST, PUT, DELETE
- **HTTPS/SSL** : Chiffrement TLS
- **Authentification** : Basic Auth, cookies de session
- **Compression** : gzip, deflate
- **Cache** : Headers If-Modified-Since, ETag
- **Virtual hosts** : Plusieurs domaines sur un serveur
- **CGI** : Exécution de scripts dynamiques

### Optimisations :
- **Pool de threads** : Limite du nombre de clients
- **Asynchrone** : asyncio au lieu de threading
- **Logging** : Module logging au lieu de print
- **Configuration** : Fichier de configuration JSON/YAML

## Analyse du code

### Points clés du serveur :
1. **Création socket** : `socket.socket(AF_INET, SOCK_STREAM)`
2. **Binding** : `socket.bind((host, port))`  
3. **Écoute** : `socket.listen(5)`
4. **Acceptation** : `socket.accept()` en boucle
5. **Threading** : `threading.Thread` pour chaque client
6. **Parsing HTTP** : Analyse de la première ligne de requête
7. **Headers RFC** : Format strict selon la spécification

### Points clés du client :
1. **Résolution DNS** : `socket.gethostbyname(hostname)`
2. **Connexion** : `socket.connect((host, port))`
3. **Envoi requête** : Construction manuelle des headers HTTP
4. **Réception** : Boucle `recv()` jusqu'à fermeture connexion
5. **Parsing réponse** : Séparation headers/contenu avec `\r\n\r\n`
6. **Analyse contenu** : Détection HTML, JSON, etc.

## Références

- **RFC 2616** - HTTP/1.1 : https://tools.ietf.org/html/rfc2616
- **RFC 2616** : https://www.rfc-editor.org/info/rfc2616
- **RFC 1945** - HTTP/1.0 : https://tools.ietf.org/html/rfc1945  
- **Python Socket** : https://docs.python.org/3/library/socket.html
- **HTTP Status Codes** : https://httpstatuses.com/
- **MIME Types** : https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
- ![IA PARTAGÉE](./Images/IA_Partagée.png)



---

**Date** : 2025  
**Licence** : Éducatif libre