# Fastipy

<div>
  <img src="https://media.discordapp.net/attachments/887158781832749086/1187385388571037778/fastipy-extended.png">
</div>

## What is it and what is it for

[Fastipy](https://pypi.org/project/Fastipy/) is a fast, very simple to use and understand open source python library for developing RESTful APIs.

## Installation

```bash
pip install Fastipy
```

## Examples

### Example for GET Route with Query Params and debug mode

```python
from Fastipy import Routes, Request, Reply

# Debug mode is False by default
routes = Routes(debug=True)

@routes.get('/')
async def home(req: Request, reply: Reply):
  # Get query params age
  age = req.query['age']
  # Recovery all persons from database with this age
  reply.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").status(200).send()

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for GET Route with Params, CORS and multiple methods

```python
from Fastipy import Routes, Request, Reply

routes = Routes().cors()

@routes.get('/user/:id')
@routes.post('/user/:id')
async def getUser(req: Request, reply: ReplyReply):
  # get users from database
  for i in users:
    if i["id"] == req.params["id"]:
      reply.json(i).send()
      return
  reply.send_status(404)

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for POST Route with Body

```python
from Fastipy import Routes, Request, Reply

routes = Routes()

@routes.post('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Save user in database
  reply.text("Created").status(201).send()

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for PUT Route with Body

```python
from Fastipy import Routes, Request, Reply

routes = Routes()

@routes.put('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Update user in database
  reply.html('<h1>Created</h1>').status(201).send()

routes.run(application="Person API", host="localhost", port=3000)
```

## Using modules

```py
# chat.py
from Fastipy import Request, Reply, Module

chat = Module('chat', '/chat')

@chat.get('/')
async def index(req: Request, reply: Reply):
  reply.send_status(200)

@chat.get('/chat')
async def test(req: Request, reply: Reply):
  reply.send_status(200)
```

```py
# message.py
from Fastipy import Request, Reply, Module

message = Module('message', '/message')

@message.get('/')
async def index(req: Request, reply: Reply):
  reply.send_status(200)

@message.get('/message')
async def test(req: Request, reply: Reply):
  reply.send_status(200)
```

```py
# main.py
from Fastipy import Routes

from message import message
from chat import chat

routes = Routes(debug=True).cors()

routes.bind(message)
routes.bind(chat)

routes.run(host='localhost')
```

## See more examples in [examples](https://github.com/Bielgomes/Fastipy/tree/main/examples) folder

# Change Log

## Development Version 1.4.1

### ToDo

- [ ] Automatic Docs Page
- [ ] Add template engine
- [ ] Add integration to test libraries
- [ ] Finish automatic reload in development mode
- [ ] Add mail module
- [ ] Add support to plugins
- [ ] Add support to middlewares
- [ ] Add support to hooks

### Added

- [x] Automatic reload in development mode (EXPERIMENTAL)
- [x] Request method PATCH
- [x] More security in CORS
- [x] JSON Database module

### Changed

- [X] Better params and query params recovery in routes
- [X] Improved route logging
- [X] Refactor structure of project
- [X] Refactor Routes class

# Contributors

<a href="https://github.com/Bielgomes/Fastipy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Bielgomes/Fastipy"/>
</a>

## How to Contributing

Open pull request 😎
