# Architecture serveur HTTP

## 1. Classe et méthodes

### `ServeurHTTP`

Classe principale qui gère le serveur HTTP/1.1 complet avec sockets.

**Méthodes publiques :**

- `__init__(host='localhost', port=8080, document_root='www')` Initialise les paramètres du serveur (adresse, port, répertoire racine, redirections).
- `demarrer()` Fonction principale : crée le socket serveur, écoute les connexions, lance les threads clients.
- `arreter()` Arrête proprement le serveur et ferme les ressources.

**Méthodes privées (préfixées par `_`) :**

- `_creer_fichier_index()` : Génère un fichier index.html par défaut avec formulaires de test.
- `_creer_pages_erreur()` : Crée les pages d'erreur personnalisées (403.html, 500.html).
- `_charger_redirections()` : Charge la configuration des redirections depuis un fichier JSON.
- `_traiter_client(socket_client, adresse_client)` : Thread principal de traitement d'un client.
- `_parser_requete(requete_brute)` : Parse une requête HTTP complète (méthode, path, headers, body).
- `_traiter_get(socket_client, chemin, headers, client_ip)` : Traite les requêtes GET.
- `_traiter_post(socket_client, chemin, headers, body, client_ip)` : Traite les requêtes POST.
- `_envoyer_liste_repertoire(socket_client, chemin_repertoire, chemin_url, client_ip)` : Génère un listing HTML des fichiers.
- `_construire_chemin_fichier(chemin_url)` : Convertit un chemin URL en chemin système sécurisé.
- `_envoyer_fichier(socket_client, chemin_fichier, headers, client_ip, request_info)` : Envoie un fichier avec gestion cache.
- `_envoyer_304_not_modified(socket_client)` : Envoie une réponse 304 Not Modified.
- `_envoyer_redirection(socket_client, nouvelle_url, code_statut=301)` : Envoie une redirection 301/302.
- `_envoyer_erreur_404(socket_client, chemin_demande)` : Page d'erreur 404 avec design moderne.
- `_envoyer_erreur_400(socket_client)` : Page d'erreur 400 Bad Request.
- `_envoyer_erreur_403(socket_client)` : Page d'erreur 403 Forbidden (utilise fichier personnalisé).
- `_envoyer_erreur_405(socket_client, methode)` : Page d'erreur 405 Method Not Allowed.
- `_envoyer_erreur_500(socket_client)` : Page d'erreur 500 Internal Server Error (utilise fichier personnalisé).
- `_envoyer_erreur_personnalisee(socket_client, code_statut, phrase_statut, contenu_html)` : Fonction générique d'envoi d'erreur.
- `_construire_headers_reponse(code_statut, phrase_statut, type_contenu, taille_contenu, last_modified=None)` : Construit les headers HTTP/1.1.
- `_obtenir_type_mime(chemin_fichier)` : Détermine le type MIME d'un fichier (20+ extensions supportées).
- `_log_request(client_ip, request_info, status_code, response_size)` : Logging au format Apache Common Log.

------

### Fonctions globales

- `main()` : Point d'entrée du programme, parse les arguments, instancie `ServeurHTTP`, appelle `demarrer()`.

------

## 2. Diagramme UML ASCII

### Diagramme de classes

```
+-------------------+
|    ServeurHTTP    |
+-------------------+
| - host            |
| - port            |
| - document_root   |
| - socket_serveur  |
| - en_fonctionnement|
| - log_file        |
| - redirections    |
+-----------------------------------------------------------+
| + demarrer()                                              |
| + arreter()                                               |
| - _creer_fichier_index()                                  |
| - _creer_pages_erreur()                                   |
| - _charger_redirections()                                 |
| - _traiter_client()                                       |
| - _parser_requete()                                       |
| - _traiter_get()                                          |
| - _traiter_post()                                         |
| - _envoyer_liste_repertoire()                             |
| - _construire_chemin_fichier()                            |
| - _envoyer_fichier()                                      |
| - _envoyer_304_not_modified()                             |
| - _envoyer_redirection()                                  |
| - _envoyer_erreur_404/400/403/405/500()                   |
| - _envoyer_erreur_personnalisee()                         |
| - _construire_headers_reponse()                           |
| - _obtenir_type_mime()                                    |
| - _log_request()                                          |
+-----------------------------------------------------------+

+-------------------+
|       main()      |
+-------------------+
```

### Architecture multi-thread

```
ServeurHTTP (thread principal)
    |
    |-- Socket d'écoute (bind + listen)
    |
    |-- Boucle d'acceptation
         |
         |-- Client 1 --> Thread 1 --> _traiter_client()
         |-- Client 2 --> Thread 2 --> _traiter_client()
         |-- Client 3 --> Thread 3 --> _traiter_client()
         |-- ...
         |-- Client N --> Thread N --> _traiter_client()
```

------

## 3. Relations et flux d'appels

### Initialisation du serveur

```
main()
  |
  |---> ServeurHTTP.__init__()
               |
               |--> _creer_fichier_index()
               |--> _creer_pages_erreur()
               |--> _charger_redirections()
  |
  |---> ServeurHTTP.demarrer()
               |
               |--> socket.socket() + bind() + listen()
               |--> Boucle accept()
                       |
                       |--> Thread(_traiter_client) pour chaque connexion
```

### Traitement d'une requête cliente

```
_traiter_client()
  |
  |--> recv() + decode()
  |--> _parser_requete()
  |--> Vérification redirections
  |
  |--> Si GET:
  |     |--> _traiter_get()
  |           |--> _construire_chemin_fichier()
  |           |--> Si répertoire: _envoyer_liste_repertoire()
  |           |--> Si fichier existe: _envoyer_fichier()
  |           |                        |--> Vérification If-Modified-Since
  |           |                        |--> Si non modifié: _envoyer_304_not_modified()
  |           |                        |--> Sinon: _construire_headers_reponse() + envoi
  |           |--> Si fichier absent: _envoyer_erreur_404()
  |
  |--> Si POST:
  |     |--> _traiter_post()
  |           |--> Parse form data
  |           |--> Génère page de confirmation
  |           |--> _construire_headers_reponse() + envoi
  |
  |--> Autres méthodes: _envoyer_erreur_405()
  |
  |--> _log_request() (dans tous les cas)
  |--> socket.close()
```

### Gestion des erreurs

```
Erreur détectée
  |
  |--> 400: _envoyer_erreur_400() --> contenu HTML inline
  |--> 403: _envoyer_erreur_403() --> charge www/errors/403.html ou fallback
  |--> 404: _envoyer_erreur_404() --> contenu HTML généré avec chemin
  |--> 405: _envoyer_erreur_405() --> contenu HTML + header Allow
  |--> 500: _envoyer_erreur_500() --> charge www/errors/500.html ou fallback
  |
  |--> _envoyer_erreur_personnalisee()
         |--> _construire_headers_reponse()
         |--> socket.send()
```

------

## 4. Scénario d'exécution (exemple)

### Commande :

```bash
python server_http.py 8080
```

### Flux d'initialisation :

```
main()
  -> Parse arguments (port=8080)
  -> ServeurHTTP(host='localhost', port=8080, document_root='www')
       -> _creer_fichier_index() (si www/ n'existe pas)
       -> _creer_pages_erreur() (crée www/errors/403.html, 500.html)
       -> _charger_redirections() (charge config redirections)
  -> demarrer()
       -> socket.socket(AF_INET, SOCK_STREAM)
       -> setsockopt(SO_REUSEADDR)
       -> bind(('localhost', 8080))
       -> listen(5)
       -> Affichage "[INFO] HTTP server started on http://localhost:8080"
       -> Boucle while True: accept()
```

### Requête cliente :

```
Client: GET /files/ HTTP/1.1

accept() -> nouvelle connexion
  -> Thread(_traiter_client)
       -> recv() -> "GET /files/ HTTP/1.1\r\nHost: localhost:8080\r\n..."
       -> _parser_requete() -> methode='GET', chemin='/files/', headers={...}
       -> Pas de redirection trouvée
       -> _traiter_get()
            -> _construire_chemin_fichier('/files/') -> 'www/files/'
            -> os.path.exists() et os.path.isdir() -> True
            -> Pas d'index.html dans le répertoire
            -> _envoyer_liste_repertoire()
                 -> os.listdir('www/files/')
                 -> Génération HTML avec tableau
                 -> _construire_headers_reponse(200, "OK", "text/html", ...)
                 -> socket.send(headers + contenu)
            -> _log_request('127.0.0.1', 'GET /files/', 200, 2048)
       -> socket.close()
```

### Requête POST :

```
Client: POST /form-handler avec données form

Thread(_traiter_client)
  -> _parser_requete() -> methode='POST', body='name=John&email=test@...'
  -> _traiter_post()
       -> Détection Content-Type: application/x-www-form-urlencoded
       -> urllib.parse.parse_qs(body) -> {'name': 'John', 'email': 'test@...'}
       -> Génération page HTML de confirmation avec données reçues
       -> _construire_headers_reponse(200, "OK", ...)
       -> socket.send()
       -> _log_request()
```

------

## 5. Fonctionnalités avancées

### Redirections (301/302)

```
self.redirections = {
    '/redirect-test': '/index.html',
    '/old-page.html': '/index.html'
}

Si chemin in redirections:
  -> _envoyer_redirection(nouvelle_url, 301)
       -> Headers: "Location: /index.html"
       -> Contenu HTML avec meta-refresh
```

### Cache (304 Not Modified)

```
Headers client: "If-Modified-Since: Thu, 01 Jan 2020 00:00:00 GMT"

_envoyer_fichier():
  -> os.stat(fichier) -> dernière modification
  -> parsedate_to_datetime(if_modified_since)
  -> Si fichier <= date_client:
       -> _envoyer_304_not_modified()
  -> Sinon: envoi normal avec Last-Modified
```

### Logging Apache

```
Format: IP - - [timestamp] "request" status size
Exemple: 127.0.0.1 - - [21/Sep/2025:14:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234

_log_request():
  -> datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
  -> open('server_access.log', 'a')
  -> write(log_entry)
```

### Types MIME étendus

```
_obtenir_type_mime():
  -> mimetypes.guess_type(fichier) (priorité)
  -> Fallback dictionary avec 20+ extensions:
     - .mp4 -> video/mp4
     - .csv -> text/csv  
     - .docx -> application/vnd.openxml...
     - défaut -> application/octet-stream
```