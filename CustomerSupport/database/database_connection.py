import psycopg2

class DatabaseConnection():
    """The Databse Connection class provides connection method."""
    conn_string = "host='localhost' dbname='customersupport' user='customersupport' password='12341234'"
    def connect_to_database(self):
        try:
            self.conn = psycopg2.connect(DatabaseConnection.conn_string)
        except:
            print("Unable to connect to the database!")
        return self.conn