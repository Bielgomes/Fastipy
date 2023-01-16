# PyForgeAPI

<div>
  <img src="https://media.discordapp.net/attachments/1044673680145383485/1064406961455648789/PyForgeAPI_Logo.png" width="250px" height="100px">
</div>

## What is it and what is it for

[PyForgeAPI](https://github.com/luisviniciuslv/PyForgeAPI) is a fast, very simple to use and understand open source python library for developing RESTful APIs.

## Installation `future`

```bash
pip install pyforgeapi
```

## Exemples

### Exemple for GET Route with form params

```python
from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  # Get form params age
  age = req.form['age']
  # Recovery all persons from database with this age
  res.html("<h1>Listing all persons</h1><ul><li>A Person</li></ul>").status(200).send()

routes.run(application="Person API", port=1395)
```

### Exemple for GET Route with params

```python
from pyforgeapi import Routes, Response, Request

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
from pyforgeapi import Routes, Response, Request

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
from pyforgeapi import Routes, Response, Request

routes = Routes()

@routes.put('/user')
def createUser(req: Request, res: Response):
  user = req.body.json
  # Update user in database
  res.sendStatus(201)

routes.run(application="Person API", port=1395)
```

# Contributors

<a href="https://github.com/luisviniciuslv/PyForgeAPI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=luisviniciuslv/PyForgeAPI"/>
</a>

## How to Contributing

Open pull request 😎
