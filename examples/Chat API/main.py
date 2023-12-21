from Fastipy import Routes, Request, Reply

import json
import datetime

routes = Routes(debug=True).cors()

@routes.get("/")
async def index(_, reply: Reply):
  try:
    with open('chat.json', 'r+') as file:
      data = json.load(file)

    reply.json(data).status(200).send()
  except:
    reply.send_status(500)

@routes.get("/chat/:chat_id")
async def index(req: Request, reply: Reply):
  with open('chat.json', 'r+') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.params['chat_id']:
      reply.json(i).status(200).send()
      return
  
  reply.send_status(404)

@routes.post("/chat")
async def index(req: Request, reply: Reply):
  with open('chat.json', 'r') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.body.json['id']:
      reply.send_status(409)
      return

  chat = {}
  chat['id'] = req.body.json['id']
  chat['messages'] = []

  data.append(chat)

  with open('chat.json', 'w') as file:
    json.dump(data, file)

  reply.send_status(200)

@routes.post("/chat/:chat_id")
async def index(req: Request, reply: Reply):
  with open('chat.json', 'r') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.params['chat_id']:
      message = {}
      message['content'] = req.body.json['content']
      message['datetime'] = str(datetime.datetime.now())

      i['messages'].append(message)

      with open('chat.json', 'w') as file:
        json.dump(data, file)
      return
    
  reply.send_status(404)
    
routes.run(application="Chat API", host="localhost", port=3000)