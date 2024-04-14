from fastipy import Fastipy, Request, Reply

import json
import datetime

app = Fastipy().cors()


@app.get("/")
async def index(_, reply: Reply):
    try:
        with open("chat.json", "r+") as file:
            data = json.load(file)

        await reply.code(200).send(data)
    except:
        await reply.send_code(500)


@app.get("/chat/:chat_id")
async def index(req: Request, reply: Reply):
    with open("chat.json", "r+") as file:
        data = json.load(file)

    for i in data:
        if i["id"] == req.params["chat_id"]:
            await reply.code(200).send(i)
            return

    await reply.send_code(404)


@app.post("/chat")
async def index(req: Request, reply: Reply):
    with open("chat.json", "r") as file:
        data = json.load(file)

    for i in data:
        if i["id"] == req.body.json["id"]:
            await reply.send_code(409)
            return

    chat = {}
    chat["id"] = req.body.json["id"]
    chat["messages"] = []

    data.append(chat)

    with open("chat.json", "w") as file:
        json.dump(data, file)

    await reply.send_code(200)


@app.post("/chat/:chat_id")
async def index(req: Request, reply: Reply):
    with open("chat.json", "r") as file:
        data = json.load(file)

    for i in data:
        if i["id"] == req.params["chat_id"]:
            message = {}
            message["content"] = req.body.json["content"]
            message["datetime"] = str(datetime.datetime.now())

            i["messages"].append(message)

            with open("chat.json", "w") as file:
                json.dump(data, file)
            return

    await reply.send_code(404)
