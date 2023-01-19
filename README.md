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

### Exemple for GET Route with Query Params

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  # Get query params age
  age = req.query['age']
  # Recovery all persons from database with this age
  res.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").status(200).send()

routes.run(application="Person API", port=1395)
```

### Exemple for GET Route with Params

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes()

@routes.get('/user/:id')
def getUser(req: Request, res: Response):
  users =["#users from database"]
  for i in users:
    if i["id"] == req.params["id"]:
      return res.json(i).send()
  return res.sendStatus(404)

routes.run(application="Person API", port=1395)
```

### Exemple for POST Route with Body

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes()

@routes.post('/user')
def createUser(req: Request, res: Response):
  user = req.body.json
  # Save user in database
  res.sendStatus( 201 )

routes.run(application="Person API", port=1395)
```

### Exemple for PUT Route with Body

```python
from PyForgeAPI import Routes, Response, Request

routes = Routes()

@routes.put('/user')
def createUser(req: Request, res: Response):
  user = req.body.json
  # Update user in database
  res.sendStatus(201)

routes.run(application="Person API", port=1395)
```

## See more exemples in [exemples](https://github.com/luisviniciuslv/PyForgeAPI/tree/main/examples) folder

# ToDo

- [x] Rename Request.form to Request.query
- [x] Print PyForgeAPI Logo again
- [ ] Docs Page automatic
- [ ] Error page automatic
- [x] If function not return response, return status code
- [x] If Route not exists, return status code 
- [ ] Rename variables to improve code readability
- [x] Remove empty spaces code from a query params
- [x] Fix possible infinite execution
- [ ] Better error handling
- [x] Accept underscore in route params
- [ ] Support html pages 

# Contributors

<a href="https://github.com/luisviniciuslv/PyForgeAPI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=luisviniciuslv/PyForgeAPI"/>
</a>

## How to Contributing

Open pull request 😎
