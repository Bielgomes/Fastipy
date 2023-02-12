import json
import uuid

from pathlib import Path

class Database:
  def __init__(self):
    self.database = {}
    self.path = Path(__file__).parent.parent / 'db.json'
    self.__load()

  def __load(self) -> None:
    if not self.path.exists():
      self.__persist()
      return

    with open(self.path, 'r') as f:
      self.database = json.load(f)

  def __persist(self) -> None:
    with open(self.path, 'w') as f:
      json.dump(self.database, f, indent=2)

  def select(self, table: dict, search: dict = None) -> list:
    try:
      return [row for row in self.database[table] if all(
        (row.get(key) == value if not isinstance(value, str) else value.lower() in str(row.get(key, '')).lower())
        for key, value in search.items()
      )] if search else self.database[table]
    except KeyError:
      return []
      
  def insert(self, table: str, data: dict) -> dict:
    if data == {}:
      raise Exception("Data cannot be empty")

    data = {'_id': str(uuid.uuid4()), **data}

    try:
      self.database[table].append(data)
    except:
      self.database[table] = [data]

    self.__persist()

    return data

  def delete(self, table: str, _id: str) -> bool:
    for row in self.database[table]:
      if row['_id'] == _id:
        self.database[table].remove(row)
        self.__persist()
        return True

    return False

  def update(self, table: str, _id: str, data: dict) -> bool:
    for row in self.database[table]:
      if row['_id'] == _id:
        row.update(data)
        self.__persist()
        return True

    return False
  
