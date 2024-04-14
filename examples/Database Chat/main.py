from fastipy import Fastipy, Request, Reply, Database
from jwt import JWTPlugin

app = Fastipy().cors()

# This database is a JSON file
# Note: This is not a good practice for production, use a database like MongoDB or PostgreSQL.
db = Database()

# This plugin is a Fake JWT authentication plugin
# All routes before this plugin will be protected
app.register(
    JWTPlugin,
    {
        "secret": "f12s2hj4f5fr5",
    },
)


@app.get("/")
async def index(_, reply: Reply):
    await reply.code(200).send(db.select("chat"))


@app.get("/chat/:chat_id")
async def index(req: Request, reply: Reply):
    await reply.code(200).send(db.find_by_id("chat", req.params["chat_id"]))


@app.post("/chat")
async def index(req: Request, reply: Reply):
    if db.find_by_id("chat", req.body.json["id"]):
        await reply.code(409).send({"error": "Chat with this id already exists"})
        return

    db.insert("chat", req.body.json)
    await reply.send_code(200)


@app.post("/chat/:chat_id")
async def index(req: Request, reply: Reply):
    if not db.find_by_id("chat", req.params["chat_id"]):
        await reply.send_code(404)
        return

    db.update("chat", req.params["chat_id"], req.body.json)
    await reply.send_code(200)


@app.delete("/chat/:chat_id")
async def index(req: Request, reply: Reply):
    if not db.find_by_id("chat", req.params["chat_id"]):
        await reply.send_code(404)
        return

    db.delete("chat", req.params["chat_id"])
    await reply.send_code(200)
