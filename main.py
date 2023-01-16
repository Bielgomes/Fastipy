from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  password = req.params['password']
  print(password)

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()

@routes.post('/')
def home(req: Request, res: Response):
  password = req.body.json['password']
  print(password)

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()

@routes.get('/user/data')
def user(req: Request, res: Response):
  return res.json({"name": "Lucas"}).status(200).send()

routes.run(application="Codify API", host="0.0.0.0", port=7777)
