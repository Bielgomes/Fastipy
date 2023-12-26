from Fastipy import Fastipy, Request, Reply

import json

app = Fastipy(debug=True)

@app.get("/")
async def home(req: Request, reply: Reply):
  with open("person.json", "r+") as f:
    person = json.load(f)
    f.close()

  _person = []

  for i in person:
    if i["age"] >= int(req.query['age']):
      _person.append(i)

  return reply.code(200).json(_person).send()

@app.post("/person")
async def person(req: Request, reply: Reply):
  with open("person.json", "r+") as f:
    person = json.load(f)
    person.append(req.body.json)
    f.seek(0)
    json.dump(person, f, indent=2)
    f.close()

  return reply.send_code(200)

app.run(application="Person API", port=3000)