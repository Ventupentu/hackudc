import bcrypt
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

    def list_to_json(self, entries: list) -> list:
        """Convertir la lista de entradas del diario a un formato JSON"""
        json_entries = []
        for entry in entries:
            json_entry = {
                "date": entry[0].strftime("%Y-%m-%d"),
                "entry": entry[1],
                "emotions": {
                    "Happy": entry[2],
                    "Angry": entry[3],
                    "Surprise": entry[4],
                    "Sad": entry[5],
                    "Fear": entry[6]
                }
            }
            json_entries.append(json_entry)
        return json_entries
    
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
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255) NOT NULL
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

    def register_user(self, username: str, password: str):
        cursor = self.connection.cursor()

        # Hashear la contraseña antes de guardarla en la base de datos
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        self.connection.commit()
        cursor.close()

    def verify_user(self, username: str, password: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            match = bcrypt.checkpw(password.encode('utf-8'), result[0])
            if not match:
                print("Contraseña incorrecta")
            return match
        else:
            print("Usuario no encontrado")
            return False


    def insert_diary_entry(self, user: str, diary_entry: dict):
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            print("Usuario no encontrado")
        
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

    def get_diary_entries(self, user: str) -> list:
        """Obtener todas las entradas del diario de un usuario"""
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            return []
        
        cursor.execute("""
                       SELECT date, entry, happy, angry, surprise, sad, fear
                       FROM diary_entries
                       WHERE user_id = %s
                       """, (user_id,))
        entries = cursor.fetchall()
        cursor.close()
        return self.list_to_json(entries)   

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    access_bd = AccessBD()
    access_bd.create_tables()
    """
    access_bd.insert_diary_entry("user1", {
        "date": "2021-09-02",
        "entry": "Hoy fue un día muy triste",
        "emotions": {
            "Happy": 0,
            "Angry": 0,
            "Surprise": 0,
            "Sad": 1,
            "Fear": 0
        }
    })
    """
    entries = access_bd.get_diary_entries("user1")
    print(entries)
    access_bd.close()
    
