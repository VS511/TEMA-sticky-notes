### Code for CodeDataService and CanvasDataService
### Each Canvas is associated with a table
import psycopg2


class CodeDataService:

    _columns: list[str] = ["id", "codeid", "collection", "text", "color", "position"]
    _text_columns: list[str] = ["collection", "text"]

    def __init__(self, canvas_name: str = None):

        if canvas_name is None:
            raise TypeError("table_name for CodeDataService cannot be of type None")

        self.canvas_name = canvas_name

    def __enter__(self):

        try:
            self.conn = psycopg2.connect(
                dbname="dev_db",
                user="dev",
                password="12345",
                host="localhost",
                port="5432",
            )
        except Exception as e:
            print(e)
            return

        self.cur = self.conn.cursor()

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {self.canvas_name} (
                         id SERIAL PRIMARY KEY,
                         codeid INT UNIQUE,
                         collection VARCHAR(100),
                         text VARCHAR(1000),
                         color INT,
                         position POINT
                         );
                         """)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_code_entry(self, **kwargs) -> int:

        # Create entry strings dynamically based on the provided data for the insertion
        entry_string: str = f"{','.join([entry for entry in kwargs if entry in self._columns])}"
        data_list: list[str] = []
        for entry in kwargs:
            if entry in self._text_columns:
                data_list.append(f"'{kwargs[entry]}'")
            elif entry == "position":
                data_list.append(f"point{str(kwargs[entry])}")
            elif entry in self._columns:
                data_list.append(f"{str(kwargs[entry])}")

        data_string: str = ",".join(data_list)

        self.cur.execute(f"""INSERT INTO {self.canvas_name} ({entry_string}) VALUES
                         ({data_string});""")
        
        self.cur.execute(f"""SELECT * FROM {self.canvas_name}
                    WHERE codeid = {kwargs["codeid"]};""")
        
        return self.cur.fetchone()[0]

    def delete_code_entry(self, codeid: int = None):

        if codeid is None:
            TypeError("id is of type None")
        if codeid is not None:
            if codeid < 0:
                ValueError("Invalid id")

        self.cur.execute(f"""DELETE FROM {self.canvas_name}
                         WHERE codeid = {codeid};""")

    def update_code_entry(self, **kwargs):

        if "codeid" not in kwargs.keys():
            raise KeyError("codeid missing")

        # Generate the SET string dynamically based on the provided data
        data_list: list[str] = []
        for entry in kwargs:
            if entry in self._text_columns:
                data_list.append(f"{entry} = '{kwargs[entry]}'")
            elif entry == "position":
                data_list.append(f"{entry} = point{str(kwargs[entry])}")
            elif entry in self._columns and entry not in ["id", "codeid"]:
                data_list.append(f"{entry} = {str(kwargs[entry])}")

        data_string: str = ",\n\t".join(data_list)

        self.cur.execute(f"""UPDATE {self.canvas_name}
                         SET
                            {data_string}
                         WHERE codeid = {kwargs["codeid"]};""")

    def get_code_by_id(self, id: int = None) -> tuple | None:

        if id is None:
            raise TypeError("id is None")
        if id is not None:
            if id < 0:
                raise ValueError("Invalid id")

        self.cur.execute(f"""SELECT * FROM {self.canvas_name}
                         WHERE id = {id};""")
        return self.cur.fetchall()

    def get_code_by_codeid(self, codeid: int = None) -> tuple | None:

        if codeid is None:
            raise TypeError("codeid is None")

        self.cur.execute(f"""SELECT * FROM {self.canvas_name}
                         WHERE codeid = {codeid};""")
        return self.cur.fetchall()

    def get_collections(self) -> list[str] | None:
        self.cur.execute(f"""SELECT DISTINCT collection
                         FROM {self.canvas_name};""")
        return [c[0] for c in self.cur.fetchall()]

    def fetch_codes(self) -> list[tuple]:
        self.cur.execute(f"""SELECT * FROM {self.canvas_name}""")
        return self.cur.fetchall()


class CanvasDataService:
    """
    Service to connect to the Postgres database containing information on all canvases
    """

    def __init__(self):
        pass

    def __enter__(self):

        try:
            self.conn = psycopg2.connect(
                dbname="dev_db",
                user="dev",
                password="12345",
                host="localhost",
                port="5432",
            )
        except Exception as e:
            print(e)
            return

        self.cur = self.conn.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS canvas (
                         id SERIAL PRIMARY KEY,
                         name VARCHAR(50) UNIQUE
                         );
                         """)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_canvas(self, canvas_name: str = None) -> int:
        """
        Create an entry into the canvas Postgres database with name `canvas_name`
        # Parameters
            canvas_name (str): The name of the canvas
        # Raises
            TypeError if canvas_name is None.
            ValueError if canvas_name is a whitespace string
        # Returns
            An int corresponding to the canvases id in the Postgres database
        """

        if canvas_name is None:
            raise TypeError("canvas_name cannot be None in create_canvas")
        elif canvas_name.strip() == "":
            raise ValueError("canvas_name cannot be an empty or whitespace string")

        self.cur.execute(f"""INSERT INTO canvas (name) VALUES
                         ('{canvas_name.strip()}');""")
        
        self.cur.execute(f"""SELECT * FROM canvas
                         WHERE name = '{canvas_name}';""")
        
        return self.cur.fetchone()[0]

    def fetch_canvases(self) -> list[tuple[int, str]]:
        """
        Get a list of canvases in the Postgres database
        # Returns
            A list containing tuple pairs of (database id, name)
        """
        self.cur.execute("""SELECT * FROM canvas""")
        return self.cur.fetchall()
    
    def get_canvas_id(self, canvas_name: str = None) -> int | None:
        """
        Get a canvas' id based on its name
        # Parameters
            canvas_name (str): The name of the canvas
        # Raises
            TypeError if canvas_name is None
            ValueError if canvas_name is a whitespace string
        # Returns
            An int corresponding to the canvas' id in the database or None if no entry with canvas_name was found
        """

        if canvas_name is None:
            raise TypeError("canvas_name is None")
        if canvas_name.strip() == "":
            raise ValueError("Whitespace string given for canvas_name")
        
        self.cur.execute(f"""SELECT id FROM canvas
                         WHERE name = '{canvas_name}';""")
        
        return self.cur.fetchone()[0]

    def get_canvas_name(self, id: int = None) -> str | None:
        """
        Get a canvas' name based on its id in the Postgres database
        # Parameters
            id (int): The id of the canvas in the Postgres database
        # Raises
            TypeError if id is None
            ValueError if id < 0
        # Returns
            A string corresponding to the name of the canvas with the id or None if no entry with id was found
        """

        if id is None:
            raise TypeError("id is None")
        if id < 0:
            raise ValueError("Incorrect id provided")
        
        self.cur.execute(f"""SELECT name FROM canvas
                         WHERE id = {id};""")
        
        return self.cur.fetchone()[0]

    def delete_canvas(self, canvas_name: str = None, id: int = None):
        """
        Deletes a canvas based on either its name or id in the Postgres database
        # Parameters
            canvas_name (str): The name of the canvas
            id (int): The id of the canvas in the Postgres database
        # Raises
            TypeError if both id and canvas_name are None
            ValueError if an id < 0 is given
            ValueError if a whitespace string is provided for canvas_name
        # Note
            Only the canvas_name or id should be provided, providing both does not change the result
        """

        if id is None and canvas_name is None:
            raise TypeError("id and canvas_name are None")
        if id is not None:
            if id < 0:
                raise ValueError("Incorrect id given in delete_canvas")
        if canvas_name.strip() == "":
            raise ValueError("Whitespace string given for canvas_name")
        
        if id is not None:            
            self.cur.execute(f"""DELETE FROM canvas
                            WHERE id = {id};""")
        elif canvas_name is not None:
            self.cur.execute(f"""DELETE FROM canvas
                            WHERE name = '{canvas_name}';""")


if __name__ == "__main__":

    with CanvasDataService() as c:
        print(c.delete_canvas("test"))
        print(c.create_canvas("test"))
        print(c.fetch_canvases())
        print(c.get_canvas_id("test"))
        print(c.get_canvas_name(c.get_canvas_id("test")))
        print(c.delete_canvas("test"))
        print(c.fetch_canvases())


    with CanvasDataService() as c:
        print(c.delete_canvas("codetest"))
        print(c.create_canvas("codetest"))

    entry = {
        "text": "This is a test code",
        "color": 0,
        "collection": "Test",
        "position": (2.0, 4.5),
        "codeid": 5,
    }

    update_entry = {
        "text": "This is an updated test code",
        "position": (2.0, 3.5),
        "codeid": 5,
    }

    with CodeDataService(canvas_name="codetest") as codes:
        print(codes.delete_code_entry(5))
        print(codes.create_code_entry(**entry))
        print(codes.fetch_codes())
        print(codes.update_code_entry(**update_entry))
        print(codes.fetch_codes())
        print(codes.get_code_by_codeid(5))
        print(codes.get_code_by_codeid(1))
        print(codes.get_code_by_id(100))
        print(codes.get_collections())