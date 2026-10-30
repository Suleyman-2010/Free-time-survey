import psycopg2


class PostgresDBConnectionManager:
    def __init__(self, url: str):
        self.url = url

    def __enter__(self):
        self.connection = psycopg2.connect(self.url)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.commit()
        self.connection.close()
