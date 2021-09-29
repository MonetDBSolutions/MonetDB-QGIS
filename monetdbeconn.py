import pymonetdb

class MonetDB:

    def __init__(self, username, password, hostname, database):
        conn = pymonetdb.connect(username=username, password=password, 
                                hostname=hostname, database=database)
        self.conn = conn

    def fetch_points(self):
        cursor = self.conn.cursor()
        queries = ["SELECT geom FROM ports;",  "SELECT polygonwkb FROM europe_coastline_single;", "SELECT longitude, latitude FROM wpi;"]
        data_points = []
        for i in queries:
            cursor.execute(i)
            res = cursor.fetchall()

            for x in res:
                try:
                    col_type = self.get_column_type(x[0])
                    if col_type == "MULTIPOINT":
                        data_points.append(self.parse_multipoint(x[0]))
                    elif col_type == "MULTILINESTRING":
                        x = x[0].split(',' ' ')
                        for i in x:
                            data_points.append(self.parse_multiline(i))
                    elif col_type == "LINESTRING":
                        x = x[0].split(',' ' ')
                        for i in x:
                            data_points.append(self.parse_linestring(i))

                    else:
                        data_points.append(x)
                except:
                    data_points.append(x)

        return data_points
        
    def parse_multipoint(self, x):
        x = x.replace('MULTIPOINT', '').strip()
        x = x.replace(')', '')
        x = x.replace('(', '')

        s = x.split(' ')

        return (float(s[0]), float(s[1]))

    def parse_linestring(self, x):
        x = x.strip()
        x = x.replace('LINESTRING', '')
        x = x.replace(')', '')
        x = x.replace('(', '')
        x = x.strip()
        s = x.split(' ')

        return (float(s[0]), float(s[1]))

    def parse_multiline(x):
        x = x.strip()
        x = x.replace('MULTILINESTRING', '')
        x = x.replace(')', '')
        x = x.replace('(', '')
        x = x.strip()
        s = x.split(' ')

        return (float(s[0]), float(s[1]))


    def get_column_type(self, col):
        types = ["MULTIPOINT", "MULTILINESTRING", "LINESTRING"]
        for x in types:
            if x in col:
                return x
