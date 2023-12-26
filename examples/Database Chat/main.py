from fastipy import Fastipy, Request, Reply, Database

app = Fastipy(debug=True).cors()

# This database is a JSON file
# Note: This is not a good practice, use a database like MongoDB or PostgreSQL
# Use this only for development
db = Database()

@app.get("/")
async def index(_, reply: Reply):
  return reply.json(db.select('chat')).code(200).send()

@app.get("/chat/:chat_id")
async def index(req: Request, reply: Reply):
  return reply.json(db.find_by_id('chat', req.params['chat_id'])).code(200).send()

@app.post("/chat")
async def index(req: Request, reply: Reply):
  if db.find_by_id('chat', req.body.json['id']):
    return reply.code(409).json({'error': 'Chat with this id already exists'}).send()

  db.insert('chat', req.body.json)
  return reply.send_code(200)

@app.post("/chat/:chat_id")
async def index(req: Request, reply: Reply):
  if not db.find_by_id('chat', req.params['chat_id']):
    return reply.send_code(404)

  db.update('chat', req.params['chat_id'], req.body.json)
  return reply.send_code(200)

@app.delete("/chat/:chat_id")
async def index(req: Request, reply: Reply):
  if not db.find_by_id('chat', req.params['chat_id']):
    return reply.send_code(404)

  db.delete('chat', req.params['chat_id'])
  return reply.send_code(200)

app.run(application="Database chat", port=3000)