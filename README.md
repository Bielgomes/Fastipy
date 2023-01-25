# PyForgeAPI

<div>
  <img src="https://media.discordapp.net/attachments/1044673680145383485/1064406961455648789/PyForgeAPI_Logo.png#vitrinedev" width="250px" height="100px">
</div>

## What is it and what is it for

[PyForgeAPI](https://pypi.org/project/PyForgeAPI/) is a fast, very simple to use and understand open source python library for developing RESTful APIs.

## Installation

```bash
pip install PyForgeAPI
```

## Examples

### Example for GET Route with Query Params and debug mode

```python
from PyForgeAPI import Routes, Response, Request

# Debug mode is False by default
routes = Routes(debug=True)

@routes.get('/')
async def home(req: Request, res: Response):
  # Get query params age
  age = req.query['age']
  # Recovery all persons from database with this age
  res.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").status(200).send()

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for GET Route with Params, CORS and multiple methods

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes().cors()

@routes.get('/user/:id')
@routes.post('/user/:id')
async def getUser(req: Request, res: Response):
  # get users from database
  for i in users:
    if i["id"] == req.params["id"]:
      res.json(i).send()
      return
  res.send_status(404)

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for POST Route with Body

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes()

@routes.post('/user')
async def createUser(req: Request, res: Response):
  user = req.body.json
  # Save user in database
  res.text("Created").status(201).send()

routes.run(application="Person API", host="localhost", port=3000)
```

### Example for PUT Route with Body

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes()

@routes.put('/user')
async def createUser(req: Request, res: Response):
  user = req.body.json
  # Update user in database
  res.html('<h1>Created</h1>').status(201).send()

routes.run(application="Person API", host="localhost", port=3000)
```

## Using modules

```py
# chat.py
from classes.response import Response
from classes.request import Request
from decorators.module import Module

chat = Module('chat', '/chat')

@chat.get('/')
async def index(req: Request, res: Response):
  res.send_status(200)

@chat.get('/chat')
async def test(req: Request, res: Response):
  res.send_status(200)
```

```py
# message.py
from classes.response import Response
from classes.request import Request
from decorators.module import Module

message = Module('message', '/message')

@message.get('/')
async def index(req: Request, res: Response):
  res.send_status(200)

@message.get('/message')
async def test(req: Request, res: Response):
  res.send_status(200)
```

```py
# main.py
from decorators.routes import Routes

from message import message
from chat import chat

routes = Routes(debug=True).cors()

routes.bind(message)
routes.bind(chat)

routes.run(host='localhost')
```

## See more examples in [examples](https://github.com/luisviniciuslv/PyForgeAPI/tree/main/examples) folder

# Change Log

## Version [1.3.4](https://pypi.org/project/PyForgeAPI/1.3.4/)

### ToDo

- [ ] Automatic docs Page
- [ ] Automatic reload

### Added

- [x] Modules (Routes in multiple files)
- [x] Better error handling
- [x] Error page on debug mode

# Contributors

<a href="https://github.com/luisviniciuslv/PyForgeAPI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=luisviniciuslv/PyForgeAPI"/>
</a>

## How to Contributing

Open pull request 😎
