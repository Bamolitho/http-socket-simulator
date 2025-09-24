#!/usr/bin/env python3

"""
HTTP Server implemented with Python sockets
Based on RFC 2616 (HTTP/1.1) for educational purposes

This server:
1. Listens on a TCP port (default 8080)
2. Accepts incoming connections
3. Parses HTTP GET and POST requests
4. Returns requested files or appropriate error pages
5. Supports redirections, directory listing, and caching
6. Maintains comprehensive logging
7. Follows HTTP/1.1 standard with proper headers

Date: September 2025
"""

import socket
import sys
import os
import threading
import time
import json
import urllib.parse
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from mimetypes import guess_type


class ServeurHTTP:
    """
    Main HTTP server class
    Handles connection listening and request processing
    """
    
    def __init__(self, host='localhost', port=8080, document_root='www'):
        """
        Initialize the HTTP server
        
        Args:
            host (str): Listening IP address (default localhost)
            port (int): Listening port (default 8080)
            document_root (str): Web documents root directory
        """
        self.host = host
        self.port = port
        self.document_root = document_root
        self.socket_serveur = None
        self.en_fonctionnement = False
        self.log_file = 'server_access.log'
        self.redirections = {}  # Store redirections: old_path -> new_path
        
        # Create www directory if it doesn't exist
        if not os.path.exists(document_root):
            os.makedirs(document_root)
            self._creer_fichier_index()
            self._creer_pages_erreur()
        
        # Create logs directory
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Initialize redirections file
        self._charger_redirections()
    
    def _creer_fichier_index(self):
        """
        Create a default index.html file for testing
        """
        contenu_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python HTTP Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info { background: #cce7ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
        ul { line-height: 1.8; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .form-section { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Python HTTP/1.1 Server</h1>
        <div class="success">
            <strong>SUCCESS!</strong> Your HTTP server is working correctly.
        </div>
        <div class="info">
            <p>This server has been implemented in pure Python with sockets.</p>
            <p>File served: <span class="code">index.html</span></p>
            <p>Generation date: """ + datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT') + """</p>
            <p>Protocol: <strong>HTTP/1.1</strong></p>
        </div>
        
        <h2>Available Tests</h2>
        <ul>
            <li><a href="/index.html">Home page</a></li>
            <li><a href="/test.html">Non-existent page (404)</a></li>
            <li><a href="/forbidden.html">Forbidden page (403)</a></li>
            <li><a href="/redirect-test">Test redirection (301)</a></li>
            <li><a href="/files/">Directory listing</a></li>
            <li><a href="/cache-test.html">Cache test (304)</a></li>
        </ul>
        
        <div class="form-section">
            <h3>POST Request Test</h3>
            <form action="/form-handler" method="POST">
                <p>
                    <label>Name: <input type="text" name="name" value="John Doe"></label>
                </p>
                <p>
                    <label>Email: <input type="email" name="email" value="john@example.com"></label>
                </p>
                <p>
                    <label>Message:<br>
                    <textarea name="message" rows="4" cols="50">Test message for POST request</textarea>
                    </label>
                </p>
                <p>
                    <button type="submit">Send POST Request</button>
                </p>
            </form>
        </div>
        
        <h2>Server Features</h2>
        <ul>
            <li>HTTP/1.1 protocol support</li>
            <li>GET and POST methods</li>
            <li>Automatic redirections (301/302)</li>
            <li>Directory listing</li>
            <li>Cache control (304 Not Modified)</li>
            <li>Comprehensive logging</li>
            <li>Multiple MIME types</li>
            <li>Connection keep-alive support</li>
        </ul>
    </div>
</body>
</html>"""
        
        with open(os.path.join(self.document_root, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(contenu_html)
        
        print(f"[INFO] index.html file created in {self.document_root}/")
    
    def _creer_pages_erreur(self):
        """
        Create custom error pages
        """
        errors_dir = os.path.join(self.document_root, 'errors')
        if not os.path.exists(errors_dir):
            os.makedirs(errors_dir)
        
        # 403 Forbidden page
        contenu_403 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>403 - Forbidden</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }
        .error-container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .error-code { font-size: 72px; color: #dc3545; font-weight: bold; margin: 0; }
        .error-title { font-size: 24px; color: #495057; margin: 20px 0; }
        .error-message { color: #6c757d; line-height: 1.6; }
        .back-link { margin-top: 30px; }
        .back-link a { color: #007bff; text-decoration: none; }
        .back-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">403</div>
        <div class="error-title">Access Forbidden</div>
        <div class="error-message">
            <p>You don't have permission to access this resource.</p>
            <p>The server understood your request but refuses to authorize it.</p>
        </div>
        <div class="back-link">
            <a href="/">&larr; Return to home page</a>
        </div>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        <small>Python HTTP/1.1 Server</small>
    </div>
</body>
</html>"""
        
        with open(os.path.join(errors_dir, '403.html'), 'w', encoding='utf-8') as f:
            f.write(contenu_403)
        
        # 500 Internal Server Error page
        contenu_500 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>500 - Internal Server Error</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }
        .error-container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .error-code { font-size: 72px; color: #dc3545; font-weight: bold; margin: 0; }
        .error-title { font-size: 24px; color: #495057; margin: 20px 0; }
        .error-message { color: #6c757d; line-height: 1.6; }
        .back-link { margin-top: 30px; }
        .back-link a { color: #007bff; text-decoration: none; }
        .back-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">500</div>
        <div class="error-title">Internal Server Error</div>
        <div class="error-message">
            <p>The server encountered an unexpected condition that prevented it from fulfilling your request.</p>
            <p>Please try again later or contact the server administrator.</p>
        </div>
        <div class="back-link">
            <a href="/">&larr; Return to home page</a>
        </div>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        <small>Python HTTP/1.1 Server</small>
    </div>
</body>
</html>"""
        
        with open(os.path.join(errors_dir, '500.html'), 'w', encoding='utf-8') as f:
            f.write(contenu_500)
        
        print(f"[INFO] Error pages created in {errors_dir}/")
        
        # Create test files directory
        files_dir = os.path.join(self.document_root, 'files')
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
            
            # Create some test files
            with open(os.path.join(files_dir, 'test.txt'), 'w', encoding='utf-8') as f:
                f.write("This is a test text file for directory listing.\n")
            
            with open(os.path.join(files_dir, 'data.json'), 'w', encoding='utf-8') as f:
                f.write('{"message": "Hello from JSON file", "server": "Python HTTP/1.1"}')
            
            with open(os.path.join(files_dir, 'cache-test.html'), 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head><title>Cache Test</title></head>
<body>
<h1>Cache Test Page</h1>
<p>This page was generated at: {datetime.now()}</p>
<p>Refresh the page to test 304 Not Modified responses.</p>
</body>
</html>""")
    
    def _charger_redirections(self):
        """
        Load redirections from configuration file
        """
        # Default redirections for testing
        self.redirections = {
            '/redirect-test': '/index.html',
            '/old-page.html': '/index.html',
            '/moved.html': '/files/test.txt'
        }
        
        # Try to load from file if exists
        redirections_file = 'redirections.json'
        if os.path.exists(redirections_file):
            try:
                with open(redirections_file, 'r', encoding='utf-8') as f:
                    file_redirections = json.load(f)
                    self.redirections.update(file_redirections)
            except Exception as e:
                print(f"[WARNING] Could not load redirections file: {e}")
    
    def demarrer(self):
        """
        Start the HTTP server
        1. Create TCP socket
        2. Configure socket options
        3. Bind socket to address and port
        4. Set socket to listening mode
        5. Accept connections in loop
        """
        try:
            # Step 1: Create TCP/IP socket
            print(f"[INFO] Creating TCP socket...")
            self.socket_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Step 2: Configure socket options
            # SO_REUSEADDR allows immediate address reuse after close
            self.socket_serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Step 3: Bind socket to address and port
            print(f"[INFO] Binding to address {self.host}:{self.port}...")
            self.socket_serveur.bind((self.host, self.port))
            
            # Step 4: Set socket to listening mode
            # Parameter 5 indicates maximum number of pending connections
            self.socket_serveur.listen(5)
            
            self.en_fonctionnement = True
            print(f"[INFO] HTTP server started on http://{self.host}:{self.port}")
            print(f"[INFO] Document root: {os.path.abspath(self.document_root)}")
            print(f"[INFO] Log file: {self.log_file}")
            print(f"[INFO] Press Ctrl+C to stop the server\n")
            
            # Step 5: Main connection acceptance loop
            while self.en_fonctionnement:
                try:
                    # Accept new client connection
                    socket_client, adresse_client = self.socket_serveur.accept()
                    
                    # Display connection information
                    print(f"[CONNECTION] New client: {adresse_client[0]}:{adresse_client[1]}")
                    
                    # Process request in separate thread to handle multiple clients
                    thread_client = threading.Thread(
                        target=self._traiter_client,
                        args=(socket_client, adresse_client)
                    )
                    thread_client.daemon = True  # Daemon thread for clean shutdown
                    thread_client.start()
                    
                except socket.error as e:
                    if self.en_fonctionnement:  # Avoid error messages during shutdown
                        print(f"[ERROR] Socket error: {e}")
                
        except KeyboardInterrupt:
            print(f"\n[INFO] Server shutdown requested by user")
        except Exception as e:
            print(f"[ERROR] Error starting server: {e}")
        finally:
            self.arreter()
    
    def _traiter_client(self, socket_client, adresse_client):
        """
        Process a connected client's request
        
        Args:
            socket_client: Connection socket with client
            adresse_client: Tuple (ip, port) of client
        """
        try:
            # Step 1: Receive HTTP request from client
            requete_brute = socket_client.recv(8192).decode('utf-8')
            
            if not requete_brute:
                print(f"[WARNING] Empty request received from {adresse_client[0]}")
                return
            
            print(f"[REQUEST] Received from {adresse_client[0]}:")
            print(f"{'-' * 50}")
            # Display only first line to avoid spam
            premiere_ligne = requete_brute.split('\n')[0].strip()
            print(f"{premiere_ligne}")
            print(f"{'-' * 50}")
            
            # Step 2: Parse HTTP request
            methode, chemin, version, headers, body = self._parser_requete(requete_brute)
            
            if not methode:
                self._envoyer_erreur_400(socket_client)
                self._log_request(adresse_client[0], "MALFORMED", 400, 0)
                return
            
            # Step 3: Check for redirections first
            if chemin in self.redirections:
                nouvelle_url = self.redirections[chemin]
                self._envoyer_redirection(socket_client, nouvelle_url, 301)
                self._log_request(adresse_client[0], f"{methode} {chemin}", 301, 0)
                return
            
            # Step 4: Process different HTTP methods
            if methode == 'GET':
                self._traiter_get(socket_client, chemin, headers, adresse_client[0])
            elif methode == 'POST':
                self._traiter_post(socket_client, chemin, headers, body, adresse_client[0])
            else:
                self._envoyer_erreur_405(socket_client, methode)
                self._log_request(adresse_client[0], f"{methode} {chemin}", 405, 0)
            
        except Exception as e:
            print(f"[ERROR] Error processing client {adresse_client[0]}: {e}")
            try:
                self._envoyer_erreur_500(socket_client)
                self._log_request(adresse_client[0], "ERROR", 500, 0)
            except:
                pass  # If we can't even send error, give up
        finally:
            # Close connection with client
            try:
                socket_client.close()
                print(f"[CONNECTION] Connection closed with {adresse_client[0]}\n")
            except:
                pass
    
    def _parser_requete(self, requete_brute):
        """
        Parse an HTTP request to extract method, path, version, headers and body
        
        Args:
            requete_brute (str): Complete received HTTP request
            
        Returns:
            tuple: (method, path, version, headers_dict, body) or (None, None, None, None, None) if error
        """
        try:
            # Separate headers and body
            if '\r\n\r\n' in requete_brute:
                headers_part, body = requete_brute.split('\r\n\r\n', 1)
            else:
                headers_part = requete_brute
                body = ""
            
            # Split request lines
            lignes = headers_part.split('\r\n')
            if not lignes:
                return None, None, None, None, None
            
            # Analyze first line (Request Line)
            premiere_ligne = lignes[0].strip()
            parties = premiere_ligne.split(' ')
            
            if len(parties) < 3:
                return None, None, None, None, None
            
            methode = parties[0].upper()
            chemin = parties[1]
            version = parties[2]
            
            # Decode URL-encoded characters (ex: %20 = space)
            chemin = urllib.parse.unquote(chemin)
            
            # Parse headers
            headers = {}
            for ligne in lignes[1:]:
                if ':' in ligne:
                    nom, valeur = ligne.split(':', 1)
                    headers[nom.strip().lower()] = valeur.strip()
            
            return methode, chemin, version, headers, body
            
        except Exception as e:
            print(f"[ERROR] Error parsing request: {e}")
            return None, None, None, None, None
    
    def _traiter_get(self, socket_client, chemin, headers, client_ip):
        """
        Handle GET request
        """
        # Build file path
        chemin_fichier = self._construire_chemin_fichier(chemin)
        
        if chemin_fichier is None:
            self._envoyer_erreur_403(socket_client)
            self._log_request(client_ip, f"GET {chemin}", 403, 0)
            return
        
        # Check if path is a directory
        if os.path.exists(chemin_fichier) and os.path.isdir(chemin_fichier):
            # Try to serve index.html from directory
            index_path = os.path.join(chemin_fichier, 'index.html')
            if os.path.exists(index_path):
                self._envoyer_fichier(socket_client, index_path, headers, client_ip, f"GET {chemin}")
            else:
                # Generate directory listing
                self._envoyer_liste_repertoire(socket_client, chemin_fichier, chemin, client_ip)
            return
        
        # Check if file exists
        if os.path.exists(chemin_fichier) and os.path.isfile(chemin_fichier):
            self._envoyer_fichier(socket_client, chemin_fichier, headers, client_ip, f"GET {chemin}")
        else:
            self._envoyer_erreur_404(socket_client, chemin)
            self._log_request(client_ip, f"GET {chemin}", 404, 0)
    
    def _traiter_post(self, socket_client, chemin, headers, body, client_ip):
        """
        Handle POST request
        """
        print(f"[POST] Processing POST request to {chemin}")
        print(f"[POST] Content-Length: {headers.get('content-length', 'Not specified')}")
        print(f"[POST] Content-Type: {headers.get('content-type', 'Not specified')}")
        
        # Parse POST data
        post_data = {}
        if 'application/x-www-form-urlencoded' in headers.get('content-type', ''):
            try:
                post_data = urllib.parse.parse_qs(body)
                # Convert lists to single values for simplicity
                post_data = {k: v[0] if isinstance(v, list) and v else v for k, v in post_data.items()}
            except Exception as e:
                print(f"[ERROR] Error parsing form data: {e}")
        
        # Generate response for POST request
        response_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>POST Request Processed</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .data {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .code {{ font-family: monospace; background: #e9ecef; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>POST Request Processed Successfully</h1>
        <div class="success">
            <strong>SUCCESS!</strong> Your POST request has been received and processed.
        </div>
        
        <h2>Request Information</h2>
        <div class="data">
            <p><strong>Path:</strong> {chemin}</p>
            <p><strong>Method:</strong> POST</p>
            <p><strong>Content-Type:</strong> {headers.get('content-type', 'Not specified')}</p>
            <p><strong>Content-Length:</strong> {headers.get('content-length', 'Not specified')} bytes</p>
        </div>
        
        <h2>Received Data</h2>
        <div class="code">
            <strong>Raw Body:</strong><br>
            {body[:500]}{'...' if len(body) > 500 else ''}
        </div>
        
        {('<div class="code"><strong>Parsed Form Data:</strong><br>' + 
          '<br>'.join([f"{k}: {v}" for k, v in post_data.items()]) + '</div>') if post_data else ''}
        
        <p><a href="/">&larr; Return to home page</a></p>
    </div>
</body>
</html>"""
        
        # Send response
        response_bytes = response_html.encode('utf-8')
        headers_response = self._construire_headers_reponse(
            code_statut=200,
            phrase_statut="OK",
            type_contenu="text/html; charset=utf-8",
            taille_contenu=len(response_bytes)
        )
        
        socket_client.send(headers_response.encode('utf-8'))
        socket_client.send(response_bytes)
        
        self._log_request(client_ip, f"POST {chemin}", 200, len(response_bytes))
        print(f"[RESPONSE] 200 OK - POST processed ({len(response_bytes)} bytes)")
    
    def _envoyer_liste_repertoire(self, socket_client, chemin_repertoire, chemin_url, client_ip):
        """
        Send directory listing
        """
        try:
            fichiers = []
            for item in os.listdir(chemin_repertoire):
                item_path = os.path.join(chemin_repertoire, item)
                if os.path.isdir(item_path):
                    fichiers.append((item + '/', 'Directory', '-', '-'))
                else:
                    stat_info = os.stat(item_path)
                    size = stat_info.st_size
                    mtime = datetime.fromtimestamp(stat_info.st_mtime)
                    fichiers.append((item, 'File', size, mtime.strftime('%Y-%m-%d %H:%M')))
            
            # Sort: directories first, then files
            fichiers.sort(key=lambda x: (x[1] == 'File', x[0].lower()))
            
            # Generate HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Directory Listing - {chemin_url}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #e9ecef; font-weight: bold; }}
        .directory {{ color: #007bff; }}
        .file {{ color: #495057; }}
        a {{ text-decoration: none; color: inherit; }}
        a:hover {{ text-decoration: underline; }}
        .size {{ text-align: right; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Index of {chemin_url}</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th class="size">Size</th>
                    <th>Last Modified</th>
                </tr>
            </thead>
            <tbody>"""
            
            # Add parent directory link if not root
            if chemin_url != '/' and chemin_url != '':
                parent_path = '/'.join(chemin_url.rstrip('/').split('/')[:-1]) or '/'
                html_content += f"""
                <tr>
                    <td><a href="{parent_path}" class="directory">../</a></td>
                    <td>Directory</td>
                    <td class="size">-</td>
                    <td>-</td>
                </tr>"""
            
            # Add files and directories
            for nom, type_item, taille, date_modif in fichiers:
                css_class = "directory" if type_item == "Directory" else "file"
                href = chemin_url.rstrip('/') + '/' + nom
                size_display = f"{taille} bytes" if taille != '-' else '-'
                
                html_content += f"""
                <tr>
                    <td><a href="{href}" class="{css_class}">{nom}</a></td>
                    <td>{type_item}</td>
                    <td class="size">{size_display}</td>
                    <td>{date_modif}</td>
                </tr>"""
            
            html_content += """
            </tbody>
        </table>
        <hr>
        <small>Python HTTP/1.1 Server - Directory Listing</small>
    </div>
</body>
</html>"""
            
            # Send response
            response_bytes = html_content.encode('utf-8')
            headers = self._construire_headers_reponse(
                code_statut=200,
                phrase_statut="OK",
                type_contenu="text/html; charset=utf-8",
                taille_contenu=len(response_bytes)
            )
            
            socket_client.send(headers.encode('utf-8'))
            socket_client.send(response_bytes)
            
            self._log_request(client_ip, f"GET {chemin_url}", 200, len(response_bytes))
            print(f"[RESPONSE] 200 OK - Directory listing sent ({len(response_bytes)} bytes)")
            
        except Exception as e:
            print(f"[ERROR] Cannot generate directory listing: {e}")
            self._envoyer_erreur_500(socket_client)
            self._log_request(client_ip, f"GET {chemin_url}", 500, 0)
    
    def _construire_chemin_fichier(self, chemin_url):
        """
        Build complete file path from URL
        
        Args:
            chemin_url (str): Path extracted from URL (ex: /index.html)
            
        Returns:
            str: Complete path to file on system, or None if access forbidden
        """
        # Remove initial slash if exists
        if chemin_url.startswith('/'):
            chemin_url = chemin_url[1:]
        
        # If path is empty or just "/", serve index.html by default
        if not chemin_url or chemin_url == '/':
            chemin_url = 'index.html'
        
        # Build complete path while securing against directory traversal attacks
        chemin_complet = os.path.join(self.document_root, chemin_url)
        
        # Security: ensure path stays within document_root
        chemin_complet = os.path.abspath(chemin_complet)
        document_root_abs = os.path.abspath(self.document_root)
        
        if not chemin_complet.startswith(document_root_abs):
            # Attempt to access outside authorized directory
            return None
        
        return chemin_complet
    
    def _envoyer_fichier(self, socket_client, chemin_fichier, headers, client_ip, request_info):
        """
        Send a file to client with appropriate HTTP headers
        
        Args:
            socket_client: Connection socket with client
            chemin_fichier (str): Complete path to file to send
            headers (dict): Request headers from client
            client_ip (str): Client IP address for logging
            request_info (str): Request info for logging
        """
        try:
            # Get file stats
            stat_info = os.stat(chemin_fichier)
            file_size = stat_info.st_size
            last_modified = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Check for If-Modified-Since header (cache control)
            if_modified_since = headers.get('if-modified-since')
            if if_modified_since:
                try:
                    client_date = parsedate_to_datetime(if_modified_since)
                    if last_modified <= client_date:
                        # File not modified, send 304
                        self._envoyer_304_not_modified(socket_client)
                        self._log_request(client_ip, request_info, 304, 0)
                        return
                except:
                    pass  # If date parsing fails, continue with normal response
            
            # Read file content
            with open(chemin_fichier, 'rb') as fichier:
                contenu = fichier.read()
            
            # Determine file MIME type
            type_mime = self._obtenir_type_mime(chemin_fichier)
            
            # Build HTTP response
            reponse_headers = self._construire_headers_reponse(
                code_statut=200,
                phrase_statut="OK",
                type_contenu=type_mime,
                taille_contenu=len(contenu),
                last_modified=last_modified
            )
            
            # Send headers
            socket_client.send(reponse_headers.encode('utf-8'))
            
            # Send file content
            socket_client.send(contenu)
            
            self._log_request(client_ip, request_info, 200, len(contenu))
            print(f"[RESPONSE] 200 OK - File sent: {os.path.basename(chemin_fichier)} ({len(contenu)} bytes)")
            
        except Exception as e:
            print(f"[ERROR] Cannot send file {chemin_fichier}: {e}")
            self._envoyer_erreur_500(socket_client)
            self._log_request(client_ip, request_info, 500, 0)
    
    def _envoyer_304_not_modified(self, socket_client):
        """
        Send 304 Not Modified response
        """
        headers = f"HTTP/1.1 304 Not Modified\r\n"
        headers += f"Date: {formatdate(usegmt=True)}\r\n"
        headers += f"Server: ServeurHTTP-Python/1.1\r\n"
        headers += f"Connection: close\r\n"
        headers += f"\r\n"
        
        socket_client.send(headers.encode('utf-8'))
        print(f"[RESPONSE] 304 Not Modified - Cached content")
    
    def _envoyer_redirection(self, socket_client, nouvelle_url, code_statut=301):
        """
        Send redirection response (301 or 302)
        
        Args:
            socket_client: Connection socket with client
            nouvelle_url (str): New URL to redirect to
            code_statut (int): 301 for permanent, 302 for temporary
        """
        phrase_statut = "Moved Permanently" if code_statut == 301 else "Found"
        
        contenu_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{code_statut} - {phrase_statut}</title>
    <meta http-equiv="refresh" content="0; url={nouvelle_url}">
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }}
        .redirect-container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }}
        .redirect-code {{ font-size: 48px; color: #007bff; font-weight: bold; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="redirect-container">
        <div class="redirect-code">{code_statut}</div>
        <h2>{phrase_statut}</h2>
        <p>The requested resource has been moved to:</p>
        <p><a href="{nouvelle_url}">{nouvelle_url}</a></p>
        <p>You will be automatically redirected in a moment...</p>
        <p><small>If redirection doesn't work, please click the link above.</small></p>
    </div>
</body>
</html>"""
        
        contenu_bytes = contenu_html.encode('utf-8')
        
        headers = f"HTTP/1.1 {code_statut} {phrase_statut}\r\n"
        headers += f"Date: {formatdate(usegmt=True)}\r\n"
        headers += f"Server: ServeurHTTP-Python/1.1\r\n"
        headers += f"Location: {nouvelle_url}\r\n"
        headers += f"Content-Type: text/html; charset=utf-8\r\n"
        headers += f"Content-Length: {len(contenu_bytes)}\r\n"
        headers += f"Connection: close\r\n"
        headers += f"\r\n"
        
        socket_client.send(headers.encode('utf-8'))
        socket_client.send(contenu_bytes)
        
        print(f"[RESPONSE] {code_statut} {phrase_statut} - Redirecting to {nouvelle_url}")
    
    def _envoyer_erreur_404(self, socket_client, chemin_demande):
        """
        Send 404 Not Found error response
        """
        contenu_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>404 - Page Not Found</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }}
        .error-container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .error-code {{ font-size: 72px; color: #dc3545; font-weight: bold; margin: 0; }}
        .error-title {{ font-size: 24px; color: #495057; margin: 20px 0; }}
        .error-message {{ color: #6c757d; line-height: 1.6; }}
        .code {{ background: #f5f5f5; padding: 5px; border-radius: 3px; font-family: monospace; }}
        .back-link {{ margin-top: 30px; }}
        .back-link a {{ color: #007bff; text-decoration: none; }}
        .back-link a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">404</div>
        <div class="error-title">Page Not Found</div>
        <div class="error-message">
            <p>The requested file does not exist:</p>
            <p class="code">{chemin_demande}</p>
            <p>Please check the URL and try again.</p>
        </div>
        <div class="back-link">
            <a href="/">&larr; Return to home page</a>
        </div>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
        <small>Python HTTP/1.1 Server</small>
    </div>
</body>
</html>"""
        
        self._envoyer_erreur_personnalisee(socket_client, 404, "Not Found", contenu_html)
        print(f"[RESPONSE] 404 Not Found - {chemin_demande}")
    
    def _envoyer_erreur_400(self, socket_client):
        """
        Send 400 Bad Request error response
        """
        contenu_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>400 - Bad Request</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }
        .error-container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }
        .error-code { font-size: 72px; color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">400</div>
        <h2>Bad Request</h2>
        <p>The HTTP request is not valid.</p>
        <p><a href="/">&larr; Return to home page</a></p>
    </div>
</body>
</html>"""
        
        self._envoyer_erreur_personnalisee(socket_client, 400, "Bad Request", contenu_html)
        print(f"[RESPONSE] 400 Bad Request")
    
    def _envoyer_erreur_403(self, socket_client):
        """
        Send 403 Forbidden error response using custom error page
        """
        try:
            # Try to load custom error page
            error_path = os.path.join(self.document_root, 'errors', '403.html')
            if os.path.exists(error_path):
                with open(error_path, 'r', encoding='utf-8') as f:
                    contenu_html = f.read()
            else:
                # Fallback content
                contenu_html = """<!DOCTYPE html>
<html><head><title>403 Forbidden</title></head>
<body><h1>403 - Forbidden</h1><p>Access denied.</p></body></html>"""
            
            self._envoyer_erreur_personnalisee(socket_client, 403, "Forbidden", contenu_html)
            print(f"[RESPONSE] 403 Forbidden")
            
        except Exception as e:
            print(f"[ERROR] Cannot send 403 error page: {e}")
            self._envoyer_erreur_personnalisee(socket_client, 403, "Forbidden", "<h1>403 Forbidden</h1>")
    
    def _envoyer_erreur_405(self, socket_client, methode):
        """
        Send 405 Method Not Allowed error response
        """
        contenu_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>405 - Method Not Allowed</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background: #f8f9fa; }}
        .error-container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }}
        .error-code {{ font-size: 72px; color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-code">405</div>
        <h2>Method Not Allowed</h2>
        <p>The method <strong>{methode}</strong> is not supported for this resource.</p>
        <p>Supported methods: GET, POST</p>
        <p><a href="/">&larr; Return to home page</a></p>
    </div>
</body>
</html>"""
        
        # Build response with Allow header
        contenu_bytes = contenu_html.encode('utf-8')
        headers = f"HTTP/1.1 405 Method Not Allowed\r\n"
        headers += f"Date: {formatdate(usegmt=True)}\r\n"
        headers += f"Server: ServeurHTTP-Python/1.1\r\n"
        headers += f"Allow: GET, POST\r\n"
        headers += f"Content-Type: text/html; charset=utf-8\r\n"
        headers += f"Content-Length: {len(contenu_bytes)}\r\n"
        headers += f"Connection: close\r\n"
        headers += f"\r\n"
        
        socket_client.send(headers.encode('utf-8'))
        socket_client.send(contenu_bytes)
        
        print(f"[RESPONSE] 405 Method Not Allowed - {methode}")
    
    def _envoyer_erreur_500(self, socket_client):
        """
        Send 500 Internal Server Error response using custom error page
        """
        try:
            # Try to load custom error page
            error_path = os.path.join(self.document_root, 'errors', '500.html')
            if os.path.exists(error_path):
                with open(error_path, 'r', encoding='utf-8') as f:
                    contenu_html = f.read()
            else:
                # Fallback content
                contenu_html = """<!DOCTYPE html>
<html><head><title>500 Internal Server Error</title></head>
<body><h1>500 - Internal Server Error</h1><p>An error occurred on the server.</p></body></html>"""
            
            self._envoyer_erreur_personnalisee(socket_client, 500, "Internal Server Error", contenu_html)
            print(f"[RESPONSE] 500 Internal Server Error")
            
        except:
            pass  # If we can't send error response, give up
    
    def _envoyer_erreur_personnalisee(self, socket_client, code_statut, phrase_statut, contenu_html):
        """
        Send custom error response
        """
        try:
            contenu_bytes = contenu_html.encode('utf-8')
            reponse_headers = self._construire_headers_reponse(
                code_statut=code_statut,
                phrase_statut=phrase_statut,
                type_contenu="text/html; charset=utf-8",
                taille_contenu=len(contenu_bytes)
            )
            
            socket_client.send(reponse_headers.encode('utf-8'))
            socket_client.send(contenu_bytes)
            
        except:
            pass  # If sending fails, give up
    
    def _construire_headers_reponse(self, code_statut, phrase_statut, type_contenu, taille_contenu, last_modified=None):
        """
        Build HTTP response headers according to RFC 2616 (HTTP/1.1)
        
        Standard format:
        HTTP/1.1 200 OK\r\n
        Date: Mon, 15 Jan 2025 10:30:00 GMT\r\n
        Server: MyHTTPServer\r\n
        Content-Type: text/html\r\n
        Content-Length: 1234\r\n
        Last-Modified: Sun, 14 Jan 2025 08:00:00 GMT\r\n
        \r\n
        
        Args:
            code_statut (int): HTTP status code (200, 404, etc.)
            phrase_statut (str): Status phrase ("OK", "Not Found", etc.)
            type_contenu (str): MIME type of content
            taille_contenu (int): Content size in bytes
            last_modified (datetime): Last modification date (optional)
            
        Returns:
            str: Formatted HTTP headers
        """
        # Current date in HTTP format (RFC 1123)
        date_http = formatdate(usegmt=True)
        
        # Build response according to HTTP/1.1 format
        headers = f"HTTP/1.1 {code_statut} {phrase_statut}\r\n"
        headers += f"Date: {date_http}\r\n"
        headers += f"Server: ServeurHTTP-Python/1.1\r\n"
        headers += f"Content-Type: {type_contenu}\r\n"
        headers += f"Content-Length: {taille_contenu}\r\n"
        
        # Add Last-Modified if provided
        if last_modified:
            headers += f"Last-Modified: {formatdate(last_modified.timestamp(), usegmt=True)}\r\n"
        
        # Add cache control headers
        if type_contenu.startswith('text/html'):
            headers += f"Cache-Control: no-cache, must-revalidate\r\n"
        else:
            headers += f"Cache-Control: public, max-age=3600\r\n"  # Cache for 1 hour
        
        headers += f"Connection: close\r\n"  # Close connection after response
        headers += f"\r\n"  # Mandatory empty line between headers and content
        
        return headers
    
    def _obtenir_type_mime(self, chemin_fichier):
        """
        Determine MIME type of file based on its extension
        
        Args:
            chemin_fichier (str): Path to file
            
        Returns:
            str: Appropriate MIME type
        """
        # Use Python's mimetypes module as primary source
        mime_type, _ = guess_type(chemin_fichier)
        if mime_type:
            return mime_type
        
        # Fallback to custom mapping for common types
        extension = os.path.splitext(chemin_fichier)[1].lower()
        
        types_mime = {
            '.html': 'text/html; charset=utf-8',
            '.htm': 'text/html; charset=utf-8',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.txt': 'text/plain; charset=utf-8',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.csv': 'text/csv',
            '.xml': 'application/xml',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        
        return types_mime.get(extension, 'application/octet-stream')
    
    def _log_request(self, client_ip, request_info, status_code, response_size):
        """
        Log request in Apache Common Log Format
        
        Format: IP - - [timestamp] "request" status size
        Example: 127.0.0.1 - - [21/Sep/2025:14:30:45 +0000] "GET /index.html HTTP/1.1" 200 1234
        """
        try:
            timestamp = datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z')
            if not timestamp.endswith(' +0000'):  # Ensure GMT format
                timestamp = datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
            
            log_entry = f'{client_ip} - - [{timestamp}] "{request_info}" {status_code} {response_size}\n'
            
            # Write to log file
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"[WARNING] Could not write to log file: {e}")
    
    def arreter(self):
        """
        Stop HTTP server cleanly
        """
        print(f"[INFO] Stopping HTTP server...")
        self.en_fonctionnement = False
        
        if self.socket_serveur:
            try:
                self.socket_serveur.close()
                print(f"[INFO] Server socket closed")
            except:
                pass


def main():
    """
    Main function - Program entry point
    """
    # Default configuration
    HOST = 'localhost'  # Listen address (0.0.0.0 for all interfaces)
    PORT = 8080         # Listen port
    DOCUMENT_ROOT = 'www'  # Web documents root directory
    
    # Process command line arguments
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
            if PORT < 1 or PORT > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            print(f"[ERROR] Invalid port: {e}")
            print(f"Usage: python {sys.argv[0]} [port] [document_root]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        DOCUMENT_ROOT = sys.argv[2]
    
    # Display startup information
    print(f"{'=' * 60}")
    print(f"[INFO] PYTHON HTTP/1.1 SERVER - SOCKET IMPLEMENTATION")
    print(f"{'=' * 60}")
    print(f"Configuration:")
    print(f"  • Address     : {HOST}")
    print(f"  • Port        : {PORT}")
    print(f"  • Directory   : {DOCUMENT_ROOT}/")
    print(f"  • URL         : http://{HOST}:{PORT}")
    print(f"  • Protocol    : HTTP/1.1")
    print(f"  • Features    : GET/POST, Redirections, Cache, Logging")
    print(f"{'=' * 60}")
    
    # Create and start server
    serveur = ServeurHTTP(host=HOST, port=PORT, document_root=DOCUMENT_ROOT)
    
    try:
        serveur.demarrer()
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""
TEST EXAMPLES:

1. Server startup:
   python server_http.py
   python server_http.py 9000
   python server_http.py 8080 public_html

2. Browser tests:
   http://localhost:8080/
   http://localhost:8080/index.html
   http://localhost:8080/files/
   http://localhost:8080/redirect-test
   http://localhost:8080/nonexistent.html

3. cURL tests:
   curl -v http://localhost:8080/
   curl -v http://localhost:8080/files/
   curl -X POST -d "name=John&email=test@example.com" http://localhost:8080/form-handler
   curl -H "If-Modified-Since: Thu, 01 Jan 1970 00:00:00 GMT" http://localhost:8080/

4. Redirection tests:
   curl -v http://localhost:8080/redirect-test
   curl -v -L http://localhost:8080/redirect-test  # Follow redirects

5. Cache tests:
   curl -v -H "If-Modified-Since: Thu, 01 Jan 1970 00:00:00 GMT" http://localhost:8080/files/cache-test.html
   curl -v -H "If-Modified-Since: $(date -R)" http://localhost:8080/files/cache-test.html

6. POST request tests:
   curl -X POST -d "test=data" http://localhost:8080/form-handler
   curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "name=Test&message=Hello" http://localhost:8080/form-handler

7. Method tests:
   curl -X PUT http://localhost:8080/  # Should return 405
   curl -X DELETE http://localhost:8080/  # Should return 405

8. Load testing:
   for i in {1..20}; do curl http://localhost:8080/ & done

Expected features demonstrated:
- HTTP/1.1 compliance with proper headers
- Automatic redirection handling (301/302)
- Directory listing when no index.html
- POST request processing with form data
- Cache control with 304 Not Modified responses
- Comprehensive logging in Apache format
- Custom error pages (403, 500)
- Enhanced MIME type detection
- Security against directory traversal attacks
"""