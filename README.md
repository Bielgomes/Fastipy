# Fastipy

<div>
  <img src="https://media.discordapp.net/attachments/887158781832749086/1187385388571037778/fastipy-extended.png">
</div>

## What is it and what is it for

[Fastipy](https://pypi.org/project/Fastipy/) is a fast, very simple to use and understand open source python library for developing RESTful APIs.

## Installation

```bash
pip install fastipy
```

## Examples

### Example for GET Route with Query Params and debug mode

```python
from fastipy import Fastipy, Request, Reply

# Debug mode is False by default
app = Fastipy(debug=True)

# Routes can be async or sync functions
@app.get('/')
def home(req: Request, reply: Reply):
  # Get query params age
  age = req.query['age']
  # Recovery all persons from database with this age
  reply.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").code(200).send()

app.run(application="Person API", host="localhost", port=3000)
```

### Example for GET Route with Params, CORS and multiple methods

```python
from fastipy import Fastipy, Request, Reply

app = Fastipy().cors()

@app.get('/user/:id')
@app.post('/user/:id')
async def getUser(req: Request, reply: Reply):
  # get users from database
  for i in users:
    if i["id"] == req.params["id"]:
      reply.json(i).send()
      return
  reply.send_code(404)

app.run(application="Person API", host="localhost", port=3000)
```

### Example for POST Route with Body

```python
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.post('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Save user in database
  reply.text("Created").code(201).send()

app.run(application="Person API", host="localhost", port=3000)
```

### Example for PUT Route with Body

```python
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.put('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Update user in database
  reply.html('<h1>Created</h1>').code(201).send()

app.run(application="Person API", host="localhost", port=3000)
```

## Creating plugins

```py
# chat.py
from fastipy import FastipyInstance, Reply, Module

# Plugins can be asynchronous or synchronized functions
# plugins have the main instance as a parameter, which means they can use all of Fastipy's functions
def chatRoutes(app: FastipyInstance):
  @app.get('/')
  async def index(req: Request, reply: Reply):
    reply.send_code(200)

  @app.get('/chat')
  async def test(req: Request, reply: Reply):
    reply.send_code(200)
```

```py
# message.py
from fastipy import FastipyInstance, Reply, Module

async def messageRoutes(app: FastipyInstance):
  @message.get('/')
  async def index(req: Request, reply: Reply):
    reply.send_code(200)

  @message.get('/message')
  async def test(req: Request, reply: Reply):
    reply.send_code(200)
```

```py
# main.py
from fastipy import Fastipy

from message import messageRoutes
from chat import chatRoutes

app = Fastipy(debug=True).cors()

app.register(messageRoutes, {'prefix': '/message'})
app.register(chatRoutes, {'prefix': '/chat'})

app.run(host='localhost')
```

## Hooks

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

# Hooks does not support asynchronism
# The onRequest hook is called before executing a route handler
@app.hook('onRequest')
def onRequest(req: Request, reply: Reply):
  print('onRequest hook')

# The onResponse hook is called when the reply sends a response
@app.hook('onResponse')
def onResponse(req: Request, reply: Reply):
  print('onResponse hook')

# The onError hook is called when an error occurs
@app.hook('onError')
def onError(req: Request, reply: Reply, error):
  print('onError hook')

# A hook will only be linked to a route if its declaration precedes the route
# The order of hooks of the same type is important
@app.get('/')
async def index(req: Request, reply: Reply):
  reply.send_code(200)

app.run(host='localhost')
```

## See more examples in [examples](https://github.com/Bielgomes/Fastipy/tree/main/examples) folder

# Change Log

## Development Version 1.5.0

### ToDo

- [ ] Automatic Docs page generator (EXPERIMENTAL)
- [ ] Add template engine
- [ ] Add integration to test libraries
- [ ] Finish automatic reload in development mode
- [ ] Add mail module
- [ ] Add support to middlewares
- [ ] Increase performance using multiprocessing and multithreading (EXPERIMENTAL)
- [ ] Add more server configurations

### Added

- [x] Automatic reload in development mode (EXPERIMENTAL)
- [x] Request method PATCH
- [x] More security in CORS
- [x] JSON Database module
- [x] Add support to hooks (onRequest, onResponse, onError)
- [x] Add support to plugins
- [x] Add decorators to routes (decorator, ReplyDecorator, RequestDecorator)

### Changed

- [x] Better params and query params recovery in routes
- [x] Improved route logging
- [x] Refactor structure of project
- [x] Refactor Routes class
- [x] Routes handler can be a sync function
- [x] Better route search algorithm and structure
- [x] It is now possible to add specific hooks to a route

# Contributors

<a href="https://github.com/Bielgomes/Fastipy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Bielgomes/Fastipy"/>
</a>

## How to Contributing

Open pull request 😎
