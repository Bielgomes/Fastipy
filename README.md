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

```python
from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.get('/')
def home(req: Request, res: Response):
  password = req.params['password']
  print(password)

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()
```

```python
from pyforgeapi import Routes, Response, Request

routes = Routes(debug=True)

@routes.post('/')
def home(req: Request, res: Response):
  password = req.body.json['password']
  print(password)

  if password == '123':
    return res.html("<h1>Logado</h1>").status(200).send()
  return res.html("<h1>Senha incorreta</h1>").status(401).send()
```

# Contributors

<a href="https://github.com/luisviniciuslv/PyForgeAPI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=luisviniciuslv/PyForgeAPI"/>
</a>

## How to Contributing

Open pull request 😎