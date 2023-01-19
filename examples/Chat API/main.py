from PyForgeAPI import Routes, Request, Response

import json
import datetime

routes = Routes(debug=True)

@routes.get("/")
def index(req: Request, res: Response):
  try:
    with open('chat.json', 'r+') as file:
      data = json.load(file)

    res.json(data).status(200).send()
  except:
    res.sendStatus(500)

@routes.get("/chat/:chat_id")
def index(req: Request, res: Response):
  with open('chat.json', 'r+') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.params['chat_id']:
      res.json(i).status(200).send()
      return
  
  res.sendStatus(404)

@routes.post("/chat")
def index(req: Request, res: Response):
  with open('chat.json', 'r') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.body.json['id']:
      res.sendStatus(409)
      return

  chat = req.body.json
  chat['messages'] = []

  data.append(chat)

  with open('chat.json', 'w') as file:
    json.dump(data, file)

  res.sendStatus(200)

@routes.post("/chat/:chat_id")
def index(req: Request, res: Response):
  with open('chat.json', 'r') as file:
    data = json.load(file)

  for i in data:
    if i['id'] == req.params['chat_id']:
      message = req.body.json
      message['datetime'] = str(datetime.datetime.now())

      i['messages'].append(req.body.json)

      with open('chat.json', 'w') as file:
        json.dump(data, file)

      return
    
  res.sendStatus(404)
    
routes.run(application="Chat API", host="localhost", port=3000)