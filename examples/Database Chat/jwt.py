from fastipy import FastipyInstance, Request

def JWTPlugin(app: FastipyInstance, options: dict):
  secret = options.get('secret', 'secret')

  @app.hook('preHandler')
  def preHandler(req: Request, _):
    if req.headers['Authorization']:
      token = req.headers['Authorization'].split(' ')[1]
      app.decorate_request('token', token)
      print(secret)
  
  app.name('JWT Auth Plugin')