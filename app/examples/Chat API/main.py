from PyForgeAPI import Routes, Request, Response

import json
import datetime

routes = Routes(debug=True).cors()

@routes.get("/")
async def index(req: Request, res: Response):
  try:
    with open('chat.json', 'r+') as file:
      data = json.load(file)

    res.json(data).status(200).send()
  except:
    res.send_status(500)

@routes.get("/chat/:chat_id")
async def index(req: Request, res: Response):
  with open('chat.json', 'r+') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.params['chat_id']:
      res.json(i).status(200).send()
      return
  
  res.send_status(404)

@routes.post("/chat")
async def index(req: Request, res: Response):
  with open('chat.json', 'r') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.body.json['id']:
      res.send_status(409)
      return

  chat = {}
  chat['id'] = req.body.json['id']
  chat['messages'] = []

  data.append(chat)

  with open('chat.json', 'w') as file:
    json.dump(data, file)

  res.send_status(200)

@routes.post("/chat/:chat_id")
async def index(req: Request, res: Response):
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
    
  res.send_status(404)
    
routes.run(application="Chat API", host="localhost", port=3000)