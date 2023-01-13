from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
  def __init__(self, routes):
    self.routes = routes
  
  def start(self, method):
    for route in self.routes[method]:
      if route['path'] == self.path:
        response = route['function']()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, World!')

  def do_GET(self):
    self.start('GET')
    
  def do_POST(self):
    self.start('POST')

  def do_PUT(self):
    self.start('PUT')

  def do_DELETE(self):
    self.start('DELETE')

  def run(self, application, port):
    print('''
    
   ▄███████▄ ▄██   ▄           ▄█    █▄       ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████    ▄████████ 
  ███    ███ ███   ██▄        ███    ███     ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███   ███    ███ 
  ███    ███ ███▄▄▄███        ███    ███     ███    █▀    ███    ███ ███   ███   ███   ███    █▀    ███    █▀  
  ███    ███ ▀▀▀▀▀▀███       ▄███▄▄▄▄███▄▄  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███   ███   ███  ▄███▄▄▄       ███        
▀█████████▀  ▄██   ███      ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███   ███   ███ ▀▀███▀▀▀     ▀███████████ 
  ███        ███   ███        ███    ███     ███    █▄  ▀███████████ ███   ███   ███   ███    █▄           ███ 
  ███        ███   ███        ███    ███     ███    ███   ███    ███ ███   ███   ███   ███    ███    ▄█    ███ 
 ▄████▀       ▀█████▀         ███    █▀      ██████████   ███    ███  ▀█   ███   █▀    ██████████  ▄████████▀  
                                                          ███    ███                                                                                                                                         
''')
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, self)

    print(f'PyHermes Server Running')
    print(f'Application {application} is running on Port {port}')

    print(f'Open http://localhost:{port} in your browser')

    httpd.serve_forever()