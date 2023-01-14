from pyhermes import Routes

routes = Routes()

@routes.get('/')
def home():
  print("Esse")

@routes.get('/home')
def home():
  print("GET")

@routes.delete('/home')
def home():
  print("DELETE")

@routes.put('/home')
def home():
  print("PUT")

routes.run(application="CodeFreelas API", port=7777, debug=True)