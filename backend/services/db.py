### Code for CodeDataService and CanvasDataService
### Each Canvas is associated with a table
import psycopg2


class CodeDataService:

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
                         group VARCHAR(100),
                         text VARCHAR(50),
                         color INT,
                         position POINT
                         );
                         """)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def create_code_entry() -> int:
        pass

    def delete_code_entry() -> int:
        pass

    def update_code_entry():
        pass

    def get_code_by_id() -> tuple:
        pass

    def get_groups() -> list[str]:
        pass

    def fetch_codes() -> list[tuple]:
        pass


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