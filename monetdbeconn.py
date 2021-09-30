import pymonetdb

class MonetDB:

    def __init__(self, username, password, hostname, database):
        conn = pymonetdb.connect(username=username, password=password, 
                                hostname=hostname, database=database)
        self.conn = conn

    def query(self, q):
        cursor = self.conn.cursor()
        cursor.execute(q)
        return cursor.fetchall()

    def get_column_type(self, col):
        types = ["MULTIPOINT", "LINESTRING", "MULTILINESTRING"]
        for x in types:
            if x in col:
                return x

        return "POINT"
