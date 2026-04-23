### Code for CodeDataService and CanvasDataService
### Each Canvas is associated with a table
import psycopg2


class CodeDataService:

    def __init__(self, canvas_name: str = None):

        if canvas_name is None:
            raise TypeError("table_name for CodeDataService cannot be of type None")

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

        self.canvas_name = canvas_name


class CanvasDataService:

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
        self.cur.execute("""SELECT * FROM canvas""")
        return self.cur.fetchall()


if __name__ == "__main__":
    with CanvasDataService() as c:
        print(c.create_canvas("test"))
        print(c.fetch_canvases())