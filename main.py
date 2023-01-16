from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  # Get form params age
  #age = req.form['age']
  # Recovery all persons from database with this age
  res.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").status(200).send()

@routes.get('/user/:id')
def getUser(req: Request, res: Response):
  users =["#users from database"]
  for i in users:
    if i["id"] == req.form["id"]:
      return res.json(i).send()
  return res.sendStatus(404)

@routes.post('/user')
def createUser(req: Request, res: Response):
  user = req.body.json
  # Save user in database
  res.sendStatus( 201 )

@routes.put('/user')
def createUser(req: Request, res: Response):
  user = req.body.json
  # Update user in database
  res.sendStatus( 201 )

routes.run(application="Person API", port=1395)
