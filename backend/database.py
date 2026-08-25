import mysql.connector;

def get_connection():
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'adibanoor09',
        database = 'gestion_inscription'
    )
    return connection
