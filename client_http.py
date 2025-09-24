#!/usr/bin/env python3
# RFC 2616 : https://www.rfc-editor.org/info/rfc2616

"""
HTTP Client implemented with Python sockets
Based on RFC 2616 (HTTP/1.1) 

This client:
1. Connects to an HTTP server via TCP
2. Sends an HTTP GET request formatted according to RFC
3. Receives and parses the HTTP response
4. Automatically follows redirections (3xx status codes)
5. Displays response information (status code, headers, content)
6. Saves content to file if requested

Date: September 2025
"""

import socket
import sys
import os
import re
from urllib.parse import urlparse, urljoin
from datetime import datetime


class ClientHTTP:
    """
    Main HTTP client class
    Handles server connection and request/response exchange
    """
    
    def __init__(self):
        """
        Initialize the HTTP client
        """
        self.socket_client = None
        self.timeout_connexion = 10  # Timeout in seconds
        self.taille_buffer = 4096    # Receive buffer size
        self.max_redirections = 5    # Maximum number of redirections to follow (for 3xx status code)
    
    def faire_requete(self, url, sauvegarder_fichier=None, afficher_headers=True, suivre_redirections=True):
        """
        Perform an HTTP GET request to a URL with automatic redirection support
        
        Args:
            url (str): Complete URL (ex: http://example.com/page.html)
            sauvegarder_fichier (str): Save file name (optional)
            afficher_headers (bool): Display response headers
            suivre_redirections (bool): Automatically follow redirections
            
        Returns:
            dict: Dictionary containing the HTTP response
        """
        print(f"{'=' * 60}")
        print(f"[INFO] HTTP CLIENT REQUEST")
        print(f"{'=' * 60}")
        print(f"Target URL: {url}")
        print(f"{'=' * 60}")
        
        # Track redirections
        redirections_suivies = []
        url_courante = url
        
        for tentative in range(self.max_redirections + 1):
            print(f"\n[INFO] Request attempt {tentative + 1}")
            if tentative > 0:
                print(f"[INFO] Following redirection to: {url_courante}")
            
            # Step 1: Parse URL to extract components
            composants_url = self._parser_url(url_courante)
            if not composants_url:
                return None
            
            host, port, chemin = composants_url
            print(f"[INFO] Connecting to {host}:{port}")
            print(f"[INFO] Requested path: {chemin}")
            
            try:
                # Step 2: Establish TCP connection with server
                if not self._connecter_serveur(host, port):
                    return None
                
                # Step 3: Build and send HTTP request
                requete_http = self._construire_requete_get(host, chemin)
                if not self._envoyer_requete(requete_http):
                    return None
                
                # Step 4: Receive and parse HTTP response
                reponse = self._recevoir_reponse()
                if not reponse:
                    return None
                
                # Step 5: Display response information
                self._afficher_reponse(reponse, afficher_headers)
                
                # Step 6: Check for redirection
                code_statut = reponse['code_statut']
                
                # Add current response to redirection trace
                redirections_suivies.append({
                    'url': url_courante,
                    'code': code_statut,
                    'phrase': reponse['phrase_statut']
                })
                
                # Handle redirections (3xx status codes)
                if suivre_redirections and 300 <= code_statut < 400 and code_statut != 304:
                    location = reponse['headers'].get('location')
                    
                    if not location:
                        print(f"[WARNING] Redirection code {code_statut} but no Location header found")
                        break
                    
                    if tentative >= self.max_redirections:
                        print(f"[WARNING] Maximum redirections ({self.max_redirections}) reached")
                        print(f"[WARNING] Stopping redirection chain")
                        break
                    
                    # Handle relative and absolute URLs
                    if location.startswith('http'):
                        # Absolute URL
                        url_courante = location
                    else:
                        # Relative URL - combine with current URL
                        url_courante = urljoin(url_courante, location)
                    
                    print(f"[INFO] Redirection detected: {code_statut} -> {location}")
                    
                    # Close current connection before following redirection
                    self._fermer_connexion()
                    continue
                
                # No redirection needed or final response reached
                break
                
            except Exception as e:
                print(f"[ERROR] Error during request: {e}")
                return None
            finally:
                # Close connection properly
                self._fermer_connexion()
        
        # Display redirection trace if any redirections occurred
        if len(redirections_suivies) > 1:
            self._afficher_trace_redirections(redirections_suivies)
        
        # Step 7: Save content if requested
        if sauvegarder_fichier and reponse and reponse.get('contenu'):
            self._sauvegarder_contenu(reponse['contenu'], sauvegarder_fichier)
        
        return reponse
    
    def _afficher_trace_redirections(self, redirections_suivies):
        """
        Display the redirection trace showing the path followed
        
        Args:
            redirections_suivies (list): List of redirection steps
        """
        print(f"\n{'=' * 60}")
        print(f"[INFO] REDIRECTION TRACE")
        print(f"{'=' * 60}")
        
        for i, etape in enumerate(redirections_suivies):
            if i == len(redirections_suivies) - 1:
                # Final response
                print(f"Step {i+1}: {etape['code']} {etape['phrase']} [FINAL]")
                print(f"         {etape['url']}")
            else:
                # Redirection step
                print(f"Step {i+1}: {etape['code']} {etape['phrase']} [REDIRECT]")
                print(f"         {etape['url']}")
        
        print(f"[INFO] Total redirections followed: {len(redirections_suivies) - 1}")
        print(f"{'=' * 60}")
    
    def _parser_url(self, url):
        """
        Parse a URL to extract host, port and path
        
        Args:
            url (str): URL to parse (ex: http://example.com:8080/page.html)
            
        Returns:
            tuple: (host, port, path) or None if error
        """
        try:
            # Use urlparse to decompose URL
            url_parsed = urlparse(url)
            
            # Check scheme (protocol)
            if url_parsed.scheme not in ['http', 'https']:
                if not url_parsed.scheme:
                    # If no scheme, assume http://
                    url = 'http://' + url
                    url_parsed = urlparse(url)
                else:
                    print(f"[ERROR] Unsupported scheme: {url_parsed.scheme}")
                    print(f"[INFO] Only http and https are supported")
                    return None
            
            # HTTPS is not implemented in this educational version (requires SSL/TLS)
            if url_parsed.scheme == 'https':
                print(f"[WARNING] HTTPS detected - this client only supports HTTP")
                print(f"[INFO] Attempting simple HTTP connection on port 443...")
            
            # Extract hostname
            host = url_parsed.hostname
            if not host:
                print(f"[ERROR] Missing hostname in URL")
                return None
            
            # Determine port
            port = url_parsed.port
            if port is None:
                # Default port according to scheme
                port = 443 if url_parsed.scheme == 'https' else 80
            
            # Extract path
            chemin = url_parsed.path
            if not chemin:
                chemin = '/'  # Default path
            
            # Add query string if present
            if url_parsed.query:
                chemin += '?' + url_parsed.query
            
            return host, port, chemin
            
        except Exception as e:
            print(f"[ERROR] Cannot parse URL '{url}': {e}")
            return None
    
    def _connecter_serveur(self, host, port):
        """
        Establish a TCP connection with the server
        
        Args:
            host (str): Hostname or IP address
            port (int): Connection port
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Step 1: Create TCP/IP socket
            print(f"[INFO] Creating TCP socket...")
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Step 2: Configure timeout
            self.socket_client.settimeout(self.timeout_connexion)
            
            # Step 3: Resolve hostname to IP address
            print(f"[INFO] DNS resolution for {host}...")
            try:
                adresse_ip = socket.gethostbyname(host)
                print(f"[INFO] {host} -> {adresse_ip}")
            except socket.gaierror as e:
                print(f"[ERROR] Cannot resolve {host}: {e}")
                return False
            
            # Step 4: Connect to server
            print(f"[INFO] Connecting to {host}:{port}...")
            self.socket_client.connect((host, port))
            print(f"[SUCCESS] Connection established with {host}:{port}")
            
            return True
            
        except socket.timeout:
            print(f"[ERROR] Connection timeout after {self.timeout_connexion}s")
            return False
        except socket.error as e:
            print(f"[ERROR] Connection error: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during connection: {e}")
            return False
    
    def _construire_requete_get(self, host, chemin):
        """
        Build an HTTP GET request according to RFC 2616 (HTTP/1.1)
        
        Request format:
        GET /path HTTP/1.1\r\n
        Host: hostname\r\n
        User-Agent: Client-HTTP-Python/1.1\r\n
        Connection: close\r\n
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n
        Accept-Language: en-US,en;q=0.5\r\n
        Accept-Encoding: identity\r\n
        \r\n
        
        Args:
            host (str): Hostname for Host header
            chemin (str): Path of requested resource
            
        Returns:
            str: Formatted HTTP request
        """
        # Request line
        ligne_requete = f"GET {chemin} HTTP/1.1\r\n"
        
        # Required and useful headers for HTTP/1.1
        headers = ""
        headers += f"Host: {host}\r\n"  # Host header is mandatory in HTTP/1.1
        headers += f"User-Agent: Client-HTTP-Python/1.1\r\n"
        headers += f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        headers += f"Accept-Language: en-US,en;q=0.5\r\n"
        headers += f"Accept-Encoding: identity\r\n"  # No compression for simplicity
        headers += f"Connection: close\r\n"  # Close connection after response
        headers += f"Cache-Control: no-cache\r\n"  # Avoid cached responses
        
        # Empty line required to terminate headers
        fin_headers = "\r\n"
        
        # Build complete request
        requete_complete = ligne_requete + headers + fin_headers
        
        return requete_complete
    
    def _envoyer_requete(self, requete_http):
        """
        Send the HTTP request to the server
        
        Args:
            requete_http (str): Complete HTTP request to send
            
        Returns:
            bool: True if send successful, False otherwise
        """
        try:
            print(f"[INFO] Sending HTTP request...")
            print(f"{'-' * 50}")
            print(f"REQUEST SENT:")
            print(f"{'-' * 50}")
            # Display request replacing \r\n with visible line breaks
            requete_affichage = requete_http.replace('\r\n', '\\r\\n\n')
            print(requete_affichage)
            print(f"{'-' * 50}")
            
            # Encode and send request
            donnees_requete = requete_http.encode('utf-8')
            octets_envoyes = self.socket_client.send(donnees_requete)
            
            print(f"[SUCCESS] Request sent ({octets_envoyes} bytes)")
            return True
            
        except socket.error as e:
            print(f"[ERROR] Send error: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during send: {e}")
            return False
    
    def _recevoir_reponse(self):
        """
        Receive and parse the HTTP response from server
        
        Returns:
            dict: Dictionary containing response elements:
                  - version: HTTP version
                  - code_statut: Status code (200, 404, etc.)
                  - phrase_statut: Status phrase ("OK", "Not Found", etc.)
                  - headers: Headers dictionary
                  - contenu: Response body
                  - contenu_brut: Complete raw response
        """
        try:
            print(f"[INFO] Receiving HTTP response...")
            
            # Receive complete response from server
            reponse_brute = b""
            while True:
                try:
                    chunk = self.socket_client.recv(self.taille_buffer)
                    if not chunk:
                        break  # Connection closed by server
                    reponse_brute += chunk
                    
                    # Check if we received end of headers (double CRLF)
                    if b'\r\n\r\n' in reponse_brute:
                        # Continue receiving until connection closes
                        # or we received all content according to Content-Length
                        pass
                    
                except socket.timeout:
                    print(f"[WARNING] Timeout during reception")
                    break
                except socket.error as e:
                    print(f"[WARNING] Socket error during reception: {e}")
                    break
            
            if not reponse_brute:
                print(f"[ERROR] No response received from server")
                return None
            
            print(f"[SUCCESS] Response received ({len(reponse_brute)} bytes)")
            
            # Decode response (handling encoding errors)
            try:
                reponse_texte = reponse_brute.decode('utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 if UTF-8 fails
                try:
                    reponse_texte = reponse_brute.decode('latin-1')
                except UnicodeDecodeError:
                    print(f"[ERROR] Cannot decode response")
                    return None
            
            # Parse HTTP response
            return self._parser_reponse_http(reponse_texte, reponse_brute)
            
        except Exception as e:
            print(f"[ERROR] Error during reception: {e}")
            return None
    
    def _parser_reponse_http(self, reponse_texte, reponse_brute):
        """
        Parse an HTTP response to extract all components
        
        Args:
            reponse_texte (str): Decoded text response
            reponse_brute (bytes): Raw response in bytes
            
        Returns:
            dict: HTTP response components
        """
        try:
            # Separate headers and content
            if '\r\n\r\n' in reponse_texte:
                partie_headers, contenu = reponse_texte.split('\r\n\r\n', 1)
            else:
                # Fallback if no double CRLF
                lignes = reponse_texte.split('\n')
                partie_headers = lignes[0] if lignes else ""
                contenu = ""
            
            # Parse status line (first line)
            lignes_headers = partie_headers.split('\r\n')
            if not lignes_headers:
                print(f"[ERROR] Malformed HTTP response")
                return None
            
            ligne_statut = lignes_headers[0]
            
            # Extract version, status code and reason phrase
            # Format: HTTP/1.1 200 OK
            parties_statut = ligne_statut.split(' ', 2)
            if len(parties_statut) < 3:
                print(f"[ERROR] Malformed status line: {ligne_statut}")
                return None
            
            version = parties_statut[0]
            try:
                code_statut = int(parties_statut[1])
            except ValueError:
                print(f"[ERROR] Invalid status code: {parties_statut[1]}")
                return None
            
            phrase_statut = parties_statut[2]
            
            # Parse headers
            headers = {}
            for ligne_header in lignes_headers[1:]:
                if ':' in ligne_header:
                    nom, valeur = ligne_header.split(':', 1)
                    headers[nom.strip().lower()] = valeur.strip()
            
            # Build response dictionary
            reponse = {
                'version': version,
                'code_statut': code_statut,
                'phrase_statut': phrase_statut,
                'headers': headers,
                'contenu': contenu,
                'contenu_brut': reponse_brute,
                'taille_totale': len(reponse_brute)
            }
            
            return reponse
            
        except Exception as e:
            print(f"[ERROR] Error parsing response: {e}")
            return None
    
    def _afficher_reponse(self, reponse, afficher_headers=True):
        """
        Display HTTP response information in structured format
        
        Args:
            reponse (dict): Dictionary containing HTTP response
            afficher_headers (bool): Display detailed headers
        """
        print(f"\n{'=' * 60}")
        print(f"[INFO] HTTP RESPONSE RECEIVED")
        print(f"{'=' * 60}")
        
        # Basic information
        code = reponse['code_statut']
        phrase = reponse['phrase_statut']
        version = reponse['version']
        
        # Determine status and type according to status code
        if 200 <= code < 300:
            status_type = "[SUCCESS]"
        elif 300 <= code < 400:
            status_type = "[REDIRECT]"
        elif 400 <= code < 500:
            status_type = "[CLIENT_ERROR]"
        elif 500 <= code < 600:
            status_type = "[SERVER_ERROR]"
        else:
            status_type = "[UNKNOWN]"
        
        print(f"Status    : {status_type} {code} {phrase}")
        print(f"Version   : {version}")
        print(f"Size      : {reponse['taille_totale']} bytes")
        
        # Display status code explanation
        self._expliquer_code_statut(code)
        
        # Important headers
        headers = reponse['headers']
        if headers:
            print(f"\n[INFO] MAIN HEADERS:")
            print(f"{'-' * 40}")
            
            headers_importants = [
                'server', 'content-type', 'content-length', 
                'date', 'last-modified', 'location', 'set-cookie',
                'cache-control', 'expires', 'etag'
            ]
            
            for nom_header in headers_importants:
                if nom_header in headers:
                    valeur = headers[nom_header]
                    nom_affiche = nom_header.replace('-', ' ').title()
                    print(f"{nom_affiche:<15} : {valeur}")
            
            # Display all headers if requested
            if afficher_headers and len(headers) > len([h for h in headers_importants if h in headers]):
                print(f"\n[INFO] ALL HEADERS:")
                print(f"{'-' * 40}")
                for nom, valeur in sorted(headers.items()):
                    if nom not in headers_importants:
                        nom_affiche = nom.replace('-', ' ').title()
                        print(f"{nom_affiche:<20} : {valeur}")
        
        # Content information
        contenu = reponse['contenu']
        if contenu:
            print(f"\n[INFO] CONTENT:")
            print(f"{'-' * 40}")
            print(f"Content size      : {len(contenu.encode('utf-8'))} bytes")
            
            # Determine content type
            type_contenu = headers.get('content-type', 'unknown')
            print(f"Content type      : {type_contenu}")
            
            # Content preview according to type
            if 'text/html' in type_contenu:
                self._afficher_apercu_html(contenu)
            elif 'text/plain' in type_contenu:
                self._afficher_apercu_texte(contenu)
            elif 'application/json' in type_contenu:
                self._afficher_apercu_json(contenu)
            else:
                self._afficher_apercu_binaire(contenu)
        else:
            print(f"\n[INFO] CONTENT: No content received")
        
        print(f"{'=' * 60}")
    
    def _expliquer_code_statut(self, code):
        """
        Display explanation of HTTP status code
        
        Args:
            code (int): HTTP status code
        """
        explications = {
            200: "OK - Request succeeded",
            201: "Created - Resource created successfully",
            204: "No Content - Request succeeded with no content to return",
            301: "Moved Permanently - Resource permanently moved",
            302: "Found - Resource temporarily moved",
            303: "See Other - Redirect with GET method",
            304: "Not Modified - Resource not modified since last request",
            307: "Temporary Redirect - Temporary redirect preserving method",
            308: "Permanent Redirect - Permanent redirect preserving method",
            400: "Bad Request - Malformed request",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Access forbidden to this resource",
            404: "Not Found - Resource not found on server",
            405: "Method Not Allowed - HTTP method not allowed",
            500: "Internal Server Error - Internal server error",
            501: "Not Implemented - Functionality not implemented",
            502: "Bad Gateway - Gateway error",
            503: "Service Unavailable - Service temporarily unavailable"
        }
        
        if code in explications:
            print(f"Explanation : {explications[code]}")
        else:
            print(f"Explanation : HTTP status code {code}")
    
    def _afficher_apercu_html(self, contenu_html):
        """
        Display intelligent preview of HTML content
        """
        print(f"\n[INFO] HTML PREVIEW:")
        print(f"{'-' * 30}")
        
        # Extract title if present
        match_titre = re.search(r'<title[^>]*>(.*?)</title>', contenu_html, re.IGNORECASE | re.DOTALL)
        if match_titre:
            titre = match_titre.group(1).strip()
            print(f"Title : {titre}")
        
        # Count some elements
        nb_liens = len(re.findall(r'<a\s+[^>]*href', contenu_html, re.IGNORECASE))
        nb_images = len(re.findall(r'<img\s+[^>]*src', contenu_html, re.IGNORECASE))
        nb_paragraphes = len(re.findall(r'<p[^>]*>', contenu_html, re.IGNORECASE))
        
        print(f"Links found       : {nb_liens}")
        print(f"Images found      : {nb_images}")
        print(f"Paragraphs        : {nb_paragraphes}")
        
        # Content preview (first 200 characters without tags)
        texte_brut = re.sub(r'<[^>]+>', '', contenu_html)
        texte_brut = ' '.join(texte_brut.split())  # Clean whitespace
        
        if len(texte_brut) > 200:
            apercu = texte_brut[:200] + "..."
        else:
            apercu = texte_brut
        
        if apercu.strip():
            print(f"\nExtracted text:")
            print(f'"{apercu}"')
    
    def _afficher_apercu_texte(self, contenu_texte):
        """
        Display preview of text content
        """
        print(f"\n[INFO] TEXT PREVIEW:")
        print(f"{'-' * 30}")
        
        lignes = contenu_texte.split('\n')
        print(f"Number of lines : {len(lignes)}")
        
        # Display first 5 lines
        for i, ligne in enumerate(lignes[:5]):
            if ligne.strip():
                print(f"{i+1:2d}: {ligne[:80]}")
        
        if len(lignes) > 5:
            print(f"... ({len(lignes) - 5} additional lines)")
    
    def _afficher_apercu_json(self, contenu_json):
        """
        Display preview of JSON content
        """
        print(f"\n[INFO] JSON PREVIEW:")
        print(f"{'-' * 30}")
        
        try:
            import json
            data = json.loads(contenu_json)
            
            if isinstance(data, dict):
                print(f"Type : JSON Object ({len(data)} keys)")
                print(f"Keys : {list(data.keys())[:10]}")  # First 10 keys
            elif isinstance(data, list):
                print(f"Type : JSON Array ({len(data)} elements)")
            else:
                print(f"Type : Simple JSON value")
                
        except:
            print(f"Malformed JSON - displaying as text")
            print(f"Beginning : {contenu_json[:100]}...")
    
    def _afficher_apercu_binaire(self, contenu):
        """
        Display information about binary content
        """
        print(f"\n[INFO] BINARY/OTHER CONTENT:")
        print(f"{'-' * 30}")
        print(f"Cannot display preview of this content type")
        print(f"Use save option to examine the file")
    
    def _sauvegarder_contenu(self, contenu, nom_fichier):
        """
        Save received content to a file
        
        Args:
            contenu (str): Content to save
            nom_fichier (str): Destination file name
        """
        try:
            # Create output directory if it doesn't exist
            repertoire = os.path.dirname(nom_fichier)
            if repertoire and not os.path.exists(repertoire):
                os.makedirs(repertoire)
            
            # Determine write mode according to content type
            if isinstance(contenu, bytes):
                mode = 'wb'
                donnees = contenu
            else:
                mode = 'w'
                donnees = contenu
                
            # Save file
            with open(nom_fichier, mode, encoding='utf-8' if mode == 'w' else None) as f:
                f.write(donnees)
            
            taille = os.path.getsize(nom_fichier)
            print(f"[SUCCESS] Content saved: {nom_fichier} ({taille} bytes)")
            
        except Exception as e:
            print(f"[ERROR] Cannot save {nom_fichier}: {e}")
    
    def _fermer_connexion(self):
        """
        Close socket connection properly
        """
        if self.socket_client:
            try:
                self.socket_client.close()
                print(f"[INFO] Connection closed")
            except:
                pass
            finally:
                self.socket_client = None


def afficher_aide():
    """
    Display usage help for the HTTP client
    """
    print(f"{'=' * 70}")
    print(f"[INFO] PYTHON HTTP CLIENT - HELP")
    print(f"{'=' * 70}")
    print(f"Usage:")
    print(f"  python client_http.py <URL> [options]")
    print(f"")
    print(f"Arguments:")
    print(f"  URL                    URL to download (ex: http://example.com/)")
    print(f"")
    print(f"Options:")
    print(f"  --save FILE            Save content to a file")
    print(f"  --no-headers           Don't display detailed headers")
    print(f"  --no-redirect          Don't follow redirections automatically")
    print(f"  --help, -h             Display this help")
    print(f"")
    print(f"Examples:")
    print(f"  python client_http.py http://httpbin.org/get")
    print(f"  python client_http.py http://example.com/ --save page.html")
    print(f"  python client_http.py localhost:8080/index.html")
    print(f"  python client_http.py google.com --save google.html --no-headers")
    print(f"  python client_http.py httpbin.org/redirect/3")
    print(f"  python client_http.py httpbin.org/redirect/3 --no-redirect")
    print(f"")
    print(f"Tests with local server:")
    print(f"  python client_http.py localhost:8080")
    print(f"  python client_http.py localhost:8080/index.html")
    print(f"  python client_http.py 127.0.0.1:8080/nonexistent-file.html")
    print(f"{'=' * 70}")


def main():
    """
    Main function - Program entry point
    """
    # Check arguments
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        afficher_aide()
        return
    
    # Parse command line arguments
    url = sys.argv[1]

    # If no scheme is detected, add "http://"
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    fichier_sauvegarde = None
    afficher_headers = True
    suivre_redirections = True
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--save' and i + 1 < len(sys.argv):
            fichier_sauvegarde = sys.argv[i + 1]
            i += 2
        elif arg == '--no-headers':
            afficher_headers = False
            i += 1
        elif arg == '--no-redirect':
            suivre_redirections = False
            i += 1
        else:
            print(f"[ERROR] Unknown argument: {arg}")
            print(f"Use --help to see help")
            return
    
    # Add timestamp to filename if no extension
    if fichier_sauvegarde and not os.path.splitext(fichier_sauvegarde)[1]:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fichier_sauvegarde = f"{fichier_sauvegarde}_{timestamp}.html"
    
    # Create and use HTTP client
    client = ClientHTTP()
    
    try:
        print(f"[INFO] Starting Python HTTP Client")
        reponse = client.faire_requete(
            url=url,
            sauvegarder_fichier=fichier_sauvegarde,
            afficher_headers=afficher_headers,
            suivre_redirections=suivre_redirections
        )
        
        if reponse:
            code = reponse['code_statut']
            if 200 <= code < 300:
                print(f"\n[SUCCESS] HTTP request successful!")
            else:
                print(f"\n[WARNING] HTTP request completed with status code {code}")
        else:
            print(f"\n[FAILED] HTTP request failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""
TEST EXAMPLES:

1. Basic tests:
   python client_http.py http://httpbin.org/get
   python client_http.py http://example.com/
   python client_http.py google.com

2. Tests with file saving:
   python client_http.py http://httpbin.org/html --save test.html
   python client_http.py http://example.com/ --save example.html

3. Tests with local server:
   python client_http.py localhost:8080
   python client_http.py localhost:8080/index.html
   python client_http.py 127.0.0.1:8080/404

4. Redirection tests:
   python client_http.py httpbin.org/redirect/3
   python client_http.py httpbin.org/redirect/5
   python client_http.py httpbin.org/relative-redirect/2
   python client_http.py httpbin.org/absolute-redirect/3
   python client_http.py httpbin.org/redirect-to?url=http://example.com

5. Redirection tests without following:
   python client_http.py httpbin.org/redirect/3 --no-redirect
   python client_http.py httpbin.org/status/302 --no-redirect

6. Tests with different status codes:
   python client_http.py httpbin.org/status/404
   python client_http.py httpbin.org/status/500
   python client_http.py httpbin.org/status/301

7. Tests without detailed headers:
   python client_http.py http://httpbin.org/get --no-headers

8. Performance tests (with time):
   time python client_http.py http://httpbin.org/delay/2

9. Tests with complex URLs:
   python client_http.py "httpbin.org/get?param1=value1&param2=value2"

10. Complete redirection chain test:
    python client_http.py httpbin.org/redirect/3 --save final_page.html

Expected behavior with /redirect/3:
Step 1: 302 Found [REDIRECT] - httpbin.org/redirect/3
Step 2: 302 Found [REDIRECT] - httpbin.org/relative-redirect/2  
Step 3: 302 Found [REDIRECT] - httpbin.org/relative-redirect/1
Step 4: 200 OK [FINAL] - httpbin.org/get
Total redirections followed: 3
"""