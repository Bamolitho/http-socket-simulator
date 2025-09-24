# **Architecture client HTTP**



# 1. Classe et méthodes

### `ClientHTTP`

Classe principale qui gère tout le cycle d'une requête HTTP via sockets.

**Méthodes publiques :**

- `__init__()`
   Initialise les paramètres par défaut (timeout, buffer, max redirections).
- `faire_requete(url, sauvegarder_fichier=None, afficher_headers=True, suivre_redirections=True)`
   Fonction principale : envoie une requête GET, suit les redirections, affiche la réponse, sauvegarde le contenu si demandé.

**Méthodes privées (préfixées par `_`) :**

- `_afficher_trace_redirections(redirections_suivies)` : Affiche l’historique des redirections.
- `_parser_url(url)` : Analyse l’URL et retourne `(host, port, path)`.
- `_connecter_serveur(host, port)` : Établit la connexion TCP avec le serveur.
- `_construire_requete_get(host, chemin)` : Construit la requête HTTP GET complète.
- `_envoyer_requete(requete_http)` : Envoie la requête via le socket.
- `_recevoir_reponse()` : Réceptionne et assemble la réponse brute.
- `_parser_reponse_http(reponse_texte, reponse_brute)` : Parse la réponse (status, headers, contenu).
- `_afficher_reponse(reponse, afficher_headers=True)` : Affiche un résumé détaillé de la réponse.
- `_expliquer_code_statut(code)` : Donne une explication lisible du code HTTP.
- `_afficher_apercu_html(contenu_html)` : Analyse un HTML (titre, liens, images…).
- `_afficher_apercu_texte(contenu_texte)` : Prévisualisation des fichiers texte.
- `_afficher_apercu_json(contenu_json)` : Prévisualisation des JSON.
- `_afficher_apercu_binaire(contenu)` : Info sur du contenu binaire.
- `_sauvegarder_contenu(contenu, nom_fichier)` : Sauvegarde dans un fichier.
- `_fermer_connexion()` : Ferme proprement le socket.

------

### Fonctions globales

- `afficher_aide()` : Affiche le guide d’utilisation du client HTTP.
- `main()` : Point d’entrée du programme, parse les arguments, instancie `ClientHTTP`, appelle `faire_requete`.

------

## 2. Diagramme UML ASCII

### Diagramme de classes

```
+-------------------+
|    ClientHTTP     |
+-------------------+
| - socket_client   |
| - timeout_connexion|
| - taille_buffer   |
| - max_redirections|
+-------------------------------+
| + faire_requete() 			|
| - _parser_url()  				|
| - _connecter_serveur() 		|
| - _construire_requete_get() 	|
| - _envoyer_requete() 			|
| - _recevoir_reponse() 		|
| - _parser_reponse_http() 		|
| - _afficher_reponse() 		|
| - _expliquer_code_statut() 	|
| - _afficher_apercu_html()  	|
| - _afficher_apercu_texte() 	|
| - _afficher_apercu_json()  	|
| - _afficher_apercu_binaire() 	|
| - _sauvegarder_contenu() 		|
| - _fermer_connexion() 		|
+-------------------------------+

+-------------------+
|   afficher_aide() |
+-------------------+

+-------------------+
|       main()      |
+-------------------+
```

### Relations (simplifiées)

```
main()
  |
  |---> ClientHTTP.faire_requete()
             |
             |--> _parser_url()
             |--> _connecter_serveur()
             |--> _construire_requete_get()
             |--> _envoyer_requete()
             |--> _recevoir_reponse()
                      |
                      |--> _parser_reponse_http()
             |--> _afficher_reponse()
                     |--> _expliquer_code_statut()
                     |--> _afficher_apercu_html() / texte / json / binaire
             |--> _afficher_trace_redirections()
             |--> _sauvegarder_contenu()
             |--> _fermer_connexion()
```

------

## 3. Scénario d’exécution (exemple)

Commande :

```
python client_http.py httpbin.org/redirect/3 --save final.html
```

Flux d’appels :

```
main()
  -> instancie ClientHTTP
  -> appelle faire_requete("http://httpbin.org/redirect/3", "final.html", True, True)
       -> _parser_url()
       -> _connecter_serveur()
       -> _construire_requete_get()
       -> _envoyer_requete()
       -> _recevoir_reponse()
            -> _parser_reponse_http()
       -> _afficher_reponse()
            -> _expliquer_code_statut()
            -> _afficher_apercu_html/json/etc.
       -> détecte redirection -> boucle à nouveau
       -> après dernière redirection -> _sauvegarder_contenu()
       -> _fermer_connexion()
```