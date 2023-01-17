from PyForgeAPI import Routes, Request, Response

import json

routes = Routes()

@routes.get("/")
def home(req: Request, res: Response):
  with open("person.json", "r+") as f:
    person = json.load(f)
    f.close()

  _person = []

  for i in person:
    if i["age"] >= int(req.form['age']):
      _person.append(i)

  res.json(_person).send()

@routes.post("/person")
def person(req: Request, res: Response):
  with open("person.json", "r+") as f:
    person = json.load(f)
    person.append(req.body.json)
    f.seek(0)
    json.dump(person, f, indent=2)
    f.close()

  res.sendStatus(200)

routes.run()