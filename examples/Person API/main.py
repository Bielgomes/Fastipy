from fastipy import Fastipy, Request, Reply

import json

app = Fastipy()


@app.hook("preHandler")
def preHandler(req: Request, reply: Reply):
    print(req.method, req.url)


@app.get("/")
async def home(req: Request, reply: Reply):
    with open("person.json", "r+") as f:
        person = json.load(f)
        f.close()

    _person = []

    for i in person:
        if i["age"] >= int(req.query["age"]):
            _person.append(i)

    await reply.code(200).send(_person)


@app.post("/person")
async def person(req: Request, reply: Reply):
    with open("person.json", "r+") as f:
        person = json.load(f)
        person.append(req.body.json)
        f.seek(0)
        json.dump(person, f, indent=2)
        f.close()

    await reply.send_code(200)


@app.on("startup")
def startup():
    print("HTTP server is running on port 3000 🚀")


@app.on("shutdown")
def shutdown():
    print("Server stopped!")
