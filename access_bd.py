import mysql.connector
from dotenv import load_dotenv
import os

class AccessBD:
    def __init__(self):
        load_dotenv()
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER1'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

    def insert(self, query, values):
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()

    def select(self, query, values):
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        result = cursor.fetchall()
        cursor.close()
        return result

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    access_bd = AccessBD()
    access_bd.insert("CREATE TABLE prueba (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255))", ())
    access_bd.insert("INSERT INTO prueba (name, email) VALUES (%s, %s)", ("SergioG", "sergio@gmail.com"))
    access_bd.close()