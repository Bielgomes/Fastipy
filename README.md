# PyForgeAPI

<div>
  <img src="https://media.discordapp.net/attachments/1044673680145383485/1064406961455648789/PyForgeAPI_Logo.png" width="250px" height="100px">
</div>

## What is it and what is it for

[PyForgeAPI](https://pypi.org/project/PyForgeAPI/) is a fast, very simple to use and understand open source python library for developing RESTful APIs.

## Installation

```bash
pip install PyForgeAPI
```

## Exemples

### Exemple for GET Route with Query Params and debug mode

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

### Exemple for GET Route with Params, CORS and multiple methods

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
  res.sendStatus(404)

routes.run(application="Person API", host="localhost", port=3000)
```

### Exemple for POST Route with Body

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

### Exemple for PUT Route with Body

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

## See more exemples in [exemples](https://github.com/luisviniciuslv/PyForgeAPI/tree/main/examples) folder

## ToDo

- [ ] Response support send files 
- [ ] Docs Page automatic
- [ ] Error page automatic
- [ ] Support html pages
- [ ] Automatic reload
- [ ] Better error handling

## Added

- [x] Support for `async` functions
- [x] Routes with multiple methods
- [x] CORS configuration

## Fixed

- [x] Previously it was possible to send more than one response

# Contributors

<a href="https://github.com/luisviniciuslv/PyForgeAPI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=luisviniciuslv/PyForgeAPI"/>
</a>

## How to Contributing

Open pull request 😎
