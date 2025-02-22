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
    
    def create_tables(self):
        """Ejecutar esta función al principio del programa para crear las tablas necesarias"""

        cursor = self.connection.cursor()
        # Crear la tabla 'users' si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE
        )
        """)

        # Crear la tabla 'diary_entries' si no existe, con mejora en los tipos de datos de las emociones
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            date DATE,
            entry TEXT,
            happy TINYINT(1),
            angry TINYINT(1),
            surprise TINYINT(1),
            sad TINYINT(1),
            fear TINYINT(1),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Guardar los cambios y cerrar el cursor
        self.connection.commit()
        cursor.close()

    
    def insert_diary_entry(self, user: str, diary_entry: dict):
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (user,))
            user_id = cursor.lastrowid
        
        # Insertar la entrada del diario
        cursor.execute("""
        INSERT INTO diary_entries (user_id, date, entry, happy, angry, surprise, sad, fear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, diary_entry['date'], 
              diary_entry['entry'], 
              diary_entry['emotions']['Happy'], 
              diary_entry['emotions']['Angry'], 
              diary_entry['emotions']['Surprise'], 
              diary_entry['emotions']['Sad'], 
              diary_entry['emotions']['Fear']))

        # Guardar los cambios y cerrar el cursor
        self.connection.commit()
        cursor.close()


    def close(self):
        self.connection.close()

if __name__ == '__main__':
    access_bd = AccessBD()
    access_bd.create_tables()
    access_bd.insert_diary_entry("user1", {
        "date": "2021-09-01",
        "entry": "Hoy fue un día muy feliz",
        "emotions": {
            "Happy": 1,
            "Angry": 0,
            "Surprise": 0,
            "Sad": 0,
            "Fear": 0
        }
    })
    access_bd.close()