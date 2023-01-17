from PyForgeAPI import Routes, Request, Response
routes = Routes(debug=False)

@routes.get('/')
def index(request: Request, response: Response):
  response.text('Hello world').send()
  
routes.run(port=1234)