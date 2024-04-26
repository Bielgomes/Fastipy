from pathlib import Path
import json, uuid


class Database:
    """A simple JSON-based database class."""

    def __init__(self):
        """
        Initialize the Database object.
        """
        self.database = {}  # Initialize an empty dictionary to hold data
        self.path = (
            Path(__file__).parent.parent / "db.json"
        )  # Set the path to the database file

        self.__load()  # Load data from the database file

    def __load(self) -> None:
        """
        Load data from the database file.
        """
        if not self.path.exists():
            # If the file doesn't exist, initialize an empty database and persist it
            self.__persist()
            return

        with open(self.path, "r") as f:
            self.database = json.load(f)  # Load data from the file into the database

    def __persist(self) -> None:
        """
        Persist the current state of the database to the file.
        """
        with open(self.path, "w") as f:
            json.dump(
                self.database, f, indent=2
            )  # Write the database contents to the file

    def insert(self, table: str, data: dict) -> dict:
        """
        Insert a new row into a table with the provided data.

        Args:
            table (str): The name of the table to insert into.
            data (dict): A dictionary containing the data for the new row.

        Returns:
            dict: The inserted row.
        """
        if data == {}:
            raise Exception("Data cannot be empty")

        data = {
            "_id": str(uuid.uuid4()),
            **data,
        }  # Generate a unique identifier for the new row

        try:
            self.database[table].append(data)
        except:
            self.database[table] = [data]

        self.__persist()  # Persist the changes to the database file

        return data  # Return the inserted row

    def select(self, table: str, search: dict = None) -> list:
        """
        Select rows from a table based on the given search criteria.

        Args:
            table (str): The name of the table to select from.
            search (dict, optional): A dictionary containing search criteria. Like {"name": "John"}. Defaults to None.

        Returns:
            list: A list of rows that match the search criteria.
        """
        try:
            return (
                [
                    row
                    for row in self.database[table]
                    if all(
                        (
                            row.get(key) == value
                            if not isinstance(value, str)
                            else value.lower() in str(row.get(key, "")).lower()
                        )
                        for key, value in search.items()
                    )
                ]
                if search
                else self.database[table]
            )
        except KeyError:
            return []  # Return an empty list if the table doesn't exist

    def find_by_id(self, table: str, _id: str) -> dict:
        """
        Find a row in a table by its unique identifier.

        Args:
            table (str): The name of the table to search.
            _id (str): The unique identifier of the row to find.

        Returns:
            dict: The row if found, otherwise an empty dictionary.
        """
        for row in self.database[table]:
            if row["_id"] == _id:
                return row

        return {}  # Return an empty dictionary if the row is not found

    def find_unique(self, table: str, search: dict) -> dict:
        """
        Find a unique row in a table based on the provided search criteria.

        Args:
            table (str): The name of the table to search.
            search (dict): A dictionary containing search criteria. Like {"name": "John"}.

        Returns:
            dict: The first row that matches all the criteria, or an empty dictionary if no match is found.
        """
        try:
            return next(
                row
                for row in self.database[table]
                if all(
                    (
                        row.get(key) == value
                        if not isinstance(value, str)
                        else value.lower() in str(row.get(key, "")).lower()
                    )
                    for key, value in search.items()
                )
            )
        except StopIteration:
            return {}  # Return an empty dictionary if no match is found

    def delete(self, table: str, _id: str) -> bool:
        """
        Delete a row from a table by its unique identifier.

        Args:
            table (str): The name of the table to delete from.
            _id (str): The unique identifier of the row to delete.

        Returns:
            bool: True if the row is successfully deleted, otherwise False.
        """
        for row in self.database[table]:
            if row["_id"] == _id:
                self.database[table].remove(row)
                self.__persist()  # Persist the changes to the database file
                return True

        return False  # Return False if the row is not found

    def update(self, table: str, _id: str, data: dict) -> bool:
        """
        Update a row in a table with the provided data.

        Args:
            table (str): The name of the table to update.
            _id (str): The unique identifier of the row to update.
            data (dict): A dictionary containing the updated data.

        Returns:
            bool: True if the row is successfully updated, otherwise False.
        """
        for row in self.database[table]:
            if row["_id"] == _id:
                row.update(data)
                self.__persist()  # Persist the changes to the database file
                return True

        return False  # Return False if the row is not found
