from Fastipy import Routes, Request, Reply

import json

routes = Routes(debug=True)

@routes.get("/")
async def home(req: Request, reply: Reply):
  with open("person.json", "r+") as f:
    person = json.load(f)
    f.close()

  _person = []

  for i in person:
    if i["age"] >= int(req.query['age']):
      _person.append(i)

  reply.code(200).json(_person).send()

@routes.post("/person")
async def person(req: Request, reply: Reply):
  with open("person.json", "r+") as f:
    person = json.load(f)
    person.append(req.body.json)
    f.seek(0)
    json.dump(person, f, indent=2)
    f.close()

  reply.send_code(200)

routes.run(host="localhost", port=3000)