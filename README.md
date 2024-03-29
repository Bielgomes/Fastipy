# Fastipy

<div>
  <img src="https://media.discordapp.net/attachments/887158781832749086/1187385388571037778/fastipy-extended.png">
</div>

## What is it and what is it for

[Fastipy](https://pypi.org/project/Fastipy/) is a fast and easy-to-use open source Python library for developing RESTful APIs.

Powered by **[uvicorn](https://www.uvicorn.org/)**

## Installation

```bash
pip install fastipy
```

## Examples

### Example for GET Route with Query Params and debug mode

```python
from fastipy import Fastipy, Request, Reply

# Debug mode is False by default
app = Fastipy()

# Routes can be async or sync functions, but reply send functions are async
# The handler returns the default HTTP status code 200
@app.get('/')
def home(req: Request, reply: Reply):
  # Get query params age
  age = req.query['age']
  # Example: Recovery all persons from database with this age and print the html
  print("<h1>Listing all persons</h1><ul><li>A Person</li></ul>")
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
      await reply.json(i).send()
      return
  await reply.send_code(404)
```

### Example for POST Route with Body

```python
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.post('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Save user in database
  await reply.text("Created").code(201).send()
```

### Example for PUT Route with Body

```python
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.put('/user')
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Update user in database
  await reply.html('<h1>Created</h1>').code(201).send()
```

### See more examples in **[examples](https://github.com/Bielgomes/Fastipy/tree/main/examples)** folder

## Creating plugins

```py
# chat.py
from fastipy import FastipyInstance, Reply

# Plugins can be asynchronous or synchronized functions
# Plugins have the main instance as a parameter, which means they can use all of Fastipy's functions
def chatRoutes(app: FastipyInstance, options: dict):
  @app.get('/')
  async def index(req: Request, reply: Reply):
    await reply.send_code(200)

  @app.get('/chat')
  async def test(req: Request, reply: Reply):
    await reply.send_code(200)
```

```py
# message.py
from fastipy import FastipyInstance, Reply

async def messageRoutes(app: FastipyInstance, options: dict):
  @message.get('/')
  async def index(req: Request, reply: Reply):
    await reply.send_code(200)

  @message.get('/message')
  async def test(req: Request, reply: Reply):
    await reply.send_code(200)

  app.name('custom plugin name')
```

```py
# main.py
from fastipy import Fastipy

from message import messageRoutes
from chat import chatRoutes

app = Fastipy().cors()

app.register(messageRoutes, {'prefix': '/message'})
app.register(chatRoutes, {'prefix': '/chat'})
```

## Hooks

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

# The preHandler hook is called before the request handler
@app.hook('preHandler')
def preHandler(req: Request, reply: Reply):
  print('onRequest hook')

# The onRequest hook is called when the request is handled
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
  await reply.send_code(200)
```

## Running

Run Fastipy application in development is easy

```py
import uvicorn

if __name__ == "__main__":
  # main:app indicates the FILE:VARIABLE

  # The file is the main file where Fastipy() is instantiated
  # The variable is the name of the variable that contains the instance of Fastipy()

  # You can find more configurations here https://www.uvicorn.org/

  config = uvicorn.Config('main:app', log_level='debug', port=3000)
  server = uvicorn.Server(config)
  server.run()
```

# Application Deploy

For production deployment, please refer to this **[uvicorn guide](https://www.uvicorn.org/deployment/)**.

# Change Log

## Version 1.5.0

### Added

- [x] Request method PATCH
- [x] More security in CORS
- [x] JSON Database module
- [x] Add support to hooks (onRequest, onResponse, onError)
- [x] Add support to plugins
- [x] Add decorators to routes (decorator, decorate_request, decorate_reply)
- [x] Add support to middlewares
- [x] Add support for lifespan events (startup, shutdown)
- [x] New preHandler hook
- [x] Add stream file support
- [x] Automatic OPTIONS method response for routes
- [x] Custom global error handler

### Changed

- [x] Better params and query params recovery in routes
- [x] Improved route logging
- [x] Refactor structure of project
- [x] Refactor Routes class
- [x] Routes handler can be a sync function
- [x] Better route search algorithm and structure
- [x] It is now possible to add specific hooks and middlewares to a route
- [x] Implementation of uvicorn HTTP web server
- [x] Better error handler

# Contributors

<a href="https://github.com/Bielgomes/Fastipy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Bielgomes/Fastipy"/>
</a>

## How to Contributing

Open pull request 😎
