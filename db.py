import mysql.connector as m

# Establish and return a connection to the MySQL database
def get_connection():
    try:
        conn = m.connect(
            host='localhost',
            user='ayush',
            password='Techno@blast',
            database='insurance_policy_management'
        )
        return conn
    except m.Error as err:
        print(err)
        return None
