from decorators.Routes import Routes

routes = Routes()

@routes.get('/')
def home():
  print("GET")

@routes.get('/home')
def home():
  print("GET")

@routes.delete('/home')
def home():
  print("DELETE")

@routes.put('/home')
def home():
  print("PUT")

routes.run(port=7777)