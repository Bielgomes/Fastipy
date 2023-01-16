from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  password = req.form['password']

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()

@routes.post('/')
def home(req: Request, res: Response):
  password = req.body.json['password']

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()

@routes.get('/data/store/:number')
def home(req: Request, res: Response):
  res.sendStatus(200)

@routes.get('/data/store/:number/asd')
def home(req: Request, res: Response):
  res.sendStatus(200)

@routes.get('/data/store/:number/asd/:number2')
def home(req: Request, res: Response):
  res.sendStatus(200)

@routes.get('/data/store/:number/asd/:number3/a')
def home(req: Request, res: Response):
  res.sendStatus(200)
  
@routes.get('/data/store/:number/asd/:number3/asd')
def home(req: Request, res: Response):
  res.sendStatus(200)

routes.run(application="Codify API", host="0.0.0.0", port=7777)
