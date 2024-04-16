# Fastipy

<div>
  <img src="https://i.imgur.com/KCi8IUS.png">
</div>

## What is it and what is it for

[Fastipy](https://pypi.org/project/Fastipy/) is a fast and easy-to-use open source Python library for developing RESTful APIs.

Powered by **[uvicorn](https://www.uvicorn.org/)**

## Installation

```bash
pip install fastipy
```

## Examples

### Example for GET Route with Query Params

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

# Routes can be async or sync functions, but reply send functions are async
# The handler returns the default HTTP status code 200
@app.get("/")
def home(req: Request, _):
  # Get query params age
  age = req.query["age"]
  # Example: Recovery all persons from database with this age and print the html
  print("<h1>Retrieving all persons</h1><ul><li>A Person</li></ul>")
```

### Example for GET Route with Params, CORS and multiple methods

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy().cors()

@app.get("/user/:id")
@app.post("/user/:id")
async def getUser(req: Request, reply: Reply):
  # get users from database
  for i in users:
    if i["id"] == req.params["id"]:
      # All response functions are asynchronous
      return await reply.send(i)

  await reply.send_code(404)
```

### Example for POST Route with Body

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.post("/user")
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Save user in database
  await reply.code(201).send("Created")
```

### Example for PUT Route with Body

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.put("/user")
async def createUser(req: Request, reply: Reply):
  user = req.body.json
  # Update user in database
  await reply.type("text/html").code(201).send("<h1>Created</h1>")
```

### Example for GET Route with file stream

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

@app.get("/stream")
async def streamFile(_, reply: Reply):
  # It could be an asynchronous generator
  def generator():
    with open("file.txt") as f:
        for line in f:
            yield line

  await reply.send(generator())
```

### Adding custom serializer to Reply send

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

app.add_serializer(
    validation=lambda data: isinstance(data, str),
    serializer=lambda data: ("application/json", json.dumps({"error": data})),
)

@app.get("/")
async def customSerializer(_, reply: Reply):
    await reply.code(404).send("Field not found")
```

### Running

Running Fastipy application in development is easy

```py
import uvicorn

if __name__ == "__main__":
  # main:app indicates the FILE:VARIABLE

  # The file is the main file where Fastipy() is instantiated
  # The variable is the name of the variable that contains the instance of Fastipy()

  # You can find more configurations here https://www.uvicorn.org/

  # set reload to True for automatic reloading!
  uvicorn.run("main:app", log_level="debug", port=8000, reload=True, loop="asyncio")
```

### See more examples in **[examples](https://github.com/Bielgomes/Fastipy/tree/main/examples)** folder

## Creating plugins

```py
# chat.py
from fastipy import FastipyInstance, Reply

# Plugins can be asynchronous or synchronized functions
# Plugins have access to the main instance, which means they can use all of Fastipy's functions
def chatRoutes(app: FastipyInstance, options: dict):
  @app.get("/")
  async def index(_, reply: Reply):
    await reply.send_code(200)

  @app.get("/chat")
  async def test(_, reply: Reply):
    await reply.send_code(200)
```

```py
# message.py
from fastipy import FastipyInstance, Reply

async def messageRoutes(app: FastipyInstance, options: dict):
  @message.get("/")
  async def index(_, reply: Reply):
    await reply.send_code(200)

  @message.get("/message")
  async def test(_, reply: Reply):
    await reply.send_code(200)

  app.name("custom plugin name")
```

```py
# main.py
from fastipy import Fastipy

from message import messageRoutes
from chat import chatRoutes

app = Fastipy().cors()

app.register(messageRoutes, {"prefix": "/message"})
app.register(chatRoutes, {"prefix": "/chat"})
```

## Hooks

```py
from fastipy import Fastipy, Request, Reply

app = Fastipy()

# The preHandler hook is called before the request handler
@app.hook("preHandler")
def preHandler(req: Request, reply: Reply):
  print("onRequest hook")

# The onRequest hook is called when the request is handled
@app.hook("onRequest")
def onRequest(req: Request, reply: Reply):
  print("onRequest hook")

# The onResponse hook is called when the reply sends a response
@app.hook("onResponse")
def onResponse(req: Request, reply: Reply):
  print("onResponse hook")

# The onError hook is called when an error occurs
@app.hook("onError")
def onError(error: Exception, req: Request, reply: Reply):
  print(f"onError hook exception: {error}")

# A hook will only be linked to a route if its declaration precedes the route
# The order of hooks of the same type is important
@app.get("/")
async def index(_, reply: Reply):
  await reply.send_code(200)
```

## End to End tests

```py
# See more in https://www.starlette.io/testclient/
from fastipy import TestClient
from main import app

client = TestClient(app)

response = client.post("/")
assert response.status_code == 200
assert response.text == "Hello World"
```

# Application Deploy

For production deployment, please refer to this **[uvicorn guide](https://www.uvicorn.org/deployment/)**.

# Change Log

## Development Version 1.5.2

### Todo

### Added

- [x] Added Fastipy config.
- [x] Added Plugin timeout configuration.
- [x] Added typing for options in print routes function.
- [x] Added types to request handler functions parameters.
- [x] Added the option to automatically create folders when saving files

### Changed

- [x] Renaming the fastipy base exception to the fastipy exception to make it easier to handle.
- [x] Fixed problem in the error handler for python 3.11.
- [x] Fixed the function of saving files securely, to save them in the correct path.
- [x] Loading text and json from body files on demand.

# Contributors

<a href="https://github.com/Bielgomes/Fastipy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Bielgomes/Fastipy"/>
</a>

## How to Contributing

Open pull request
