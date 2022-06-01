import pymonetdb

from qgis.core import Qgis

class MonetDB:

    def __init__(self, username, password, hostname, database, logger):
        conn = pymonetdb.connect(username=username, password=password,
                                 hostname=hostname, database=database)
        self.conn = conn
        self.logger = logger

        self.logger.log(f"Succesfully connected to database: {database} on {hostname}", Qgis.Success)

    def query(self, q):
        cursor = self.conn.cursor()
        self.logger.log(f"About to execute query:\n {q}", Qgis.Info)
        count = cursor.execute(q)
        if count == 0:
            self.logger.log(f"Did not receive rows from previous query, table might be empty", Qgis.Warning)
        else:
            self.logger.log(f"Succesfully fetched {count} rows", Qgis.Info)
        return cursor.fetchall()

    def get_column_type(self, col):
        types = ["MULTIPOINT", "LINESTRING", "MULTILINESTRING", "POLYGON", "MULTIPOLYGON"]
        for x in types:
            if x in col:
                return x

        return "POINT"
