import bcrypt
import mysql.connector
from dotenv import load_dotenv
import os

class AccessBD:
    def __init__(self):
        load_dotenv()
        self.connection = self.get_db_connection()

    def get_db_connection(self):
        return mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )

    def list_to_entris_json(self, entries: list) -> list:
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
    
    def list_to_chat_json(self, entries: list) -> list:
        """Convertir la lista de entradas del diario a un formato JSON"""
        json_entries = []
        for entry in entries:
            json_entry = {
                "date": entry[0].strftime("%Y-%m-%d"),
                "human_message": entry[1],
                "bot_message": entry[2],
                "emotions": {
                    "Happy": entry[3],
                    "Angry": entry[4],
                    "Surprise": entry[5],
                    "Sad": entry[6],
                    "Fear": entry[7]
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

        # Crear la tabla 'diary_entries' si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary_entries (
            user_id INT,
            date DATE,
            entry TEXT,
            happy DECIMAL(3,2),
            angry DECIMAL(3,2),
            surprise DECIMAL(3,2),
            sad DECIMAL(3,2),
            fear DECIMAL(3,2),
            UNIQUE (user_id, date),
            PRIMARY KEY (user_id, date),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            date DATETIME,
            human_message TEXT,
            bot_message TEXT,
            happy DECIMAL(3,2),
            angry DECIMAL(3,2),
            surprise DECIMAL(3,2),
            sad DECIMAL(3,2),
            fear DECIMAL(3,2),
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

    def change_password(self, username: str, new_password: str):
        cursor = self.connection.cursor()

        # Hashear la nueva contraseña antes de guardarla en la base de datos
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))

        self.connection.commit()
        cursor.close()

    def check_user(self, username: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        (count,) = cursor.fetchone()
        cursor.close()
        return count > 0

    def verify_user(self, username: str, password: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            match = bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))
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
        ON DUPLICATE KEY UPDATE 
        entry = VALUES(entry), 
        happy = VALUES(happy),
        angry = VALUES(angry),
        surprise = VALUES(surprise),
        sad = VALUES(sad),
        fear = VALUES(fear)
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

    def get_diary_entries(self, user: str, limit: int = 50) -> list:
        """
        Obtener todas las entradas del diario de un usuario
        :param user: Nombre de usuario
        :param limit: Número de entradas a obtener. Si es None, se obtienen todas las entradas        
        """
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            return []
        
        if limit is None:
            cursor.execute("""
                       SELECT date, entry, happy, angry, surprise, sad, fear
                       FROM diary_entries
                       WHERE user_id = %s
                       ORDER BY date
                       """, (user_id,))
        else:
            cursor.execute("""
                        SELECT *
                        FROM (
                            SELECT date, entry, happy, angry, surprise, sad, fear
                            FROM diary_entries
                            WHERE user_id = %s
                            ORDER BY date DESC
                            LIMIT %s
                        ) subquery
                        ORDER BY date ASC;
                        """, (user_id, limit))
        entries = cursor.fetchall()
        cursor.close()
        return self.list_to_entris_json(entries)
    
    def get_diary_entry(self, user: str, date: str) -> dict:
        """
        Obtener una entrada del diario de un usuario
        :param user: Nombre de usuario  
        :param date: Fecha de la entrada
        """
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            return {}
        
        cursor.execute("""
                       SELECT date, entry, happy, angry, surprise, sad, fear
                       FROM diary_entries
                       WHERE user_id = %s AND date = %s
                       """, (user_id, date))
        entry = cursor.fetchone()
        cursor.close()
        if entry:
            return self.list_to_entris_json([entry])[0]
        else:
            return None

    def insert_chat_history(self, user: str, chat_history: dict):
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            print("Usuario no encontrado")
        
        # Insertar el historial del chat
        cursor.execute("""
        INSERT INTO chat_history (user_id, date, human_message, bot_message, happy, angry, surprise, sad, fear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, chat_history['date'], 
              chat_history['human_message'], 
              chat_history['bot_message'],
              chat_history['emotions']['Happy'], 
              chat_history['emotions']['Angry'], 
              chat_history['emotions']['Surprise'], 
              chat_history['emotions']['Sad'], 
              chat_history['emotions']['Fear']))

        # Guardar los cambios y cerrar el cursor
        self.connection.commit()
        cursor.close()

    def get_chat_history(self, user: str, limit: int = None) -> list:
        """Obtener todo el historial del chat de un usuario"""
        cursor = self.connection.cursor()

        # Obtener el id del usuario
        cursor.execute("SELECT id FROM users WHERE username = %s", (user,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
        else:
            return []
        
        if limit is None:
        
            cursor.execute("""
                        SELECT date, human_message, bot_message, happy, angry, surprise, sad, fear
                        FROM chat_history
                        WHERE user_id = %s
                        ORDER BY date
                        """, (user_id,))
        else:
            cursor.execute("""
                        SELECT *
                        FROM (
                            SELECT date, human_message, bot_message, happy, angry, surprise, sad, fear
                            FROM chat_history
                            WHERE user_id = %s
                            ORDER BY date DESC
                            LIMIT %s
                        ) subquery
                        ORDER BY date ASC;
                        """, (user_id, limit))
        entries = cursor.fetchall()
        cursor.close()
        return self.list_to_chat_json(entries)   

    def close(self):
        self.connection.close()

    def drop_table(self):
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE diary_entries")
        
        self.connection.commit()
        cursor.close()

if __name__ == '__main__':
    access_bd = AccessBD()
    access_bd.create_tables()
    
    """
    access_bd.insert_diary_entry("user1", {
        "date": "2021-09-03",
        "entry": "Hoy fue un día muy xD aaa",
        "emotions": {
            "Happy": 0,
            "Angry": 0,
            "Surprise": 0,
            "Sad": 1,
            "Fear": 0
        }
    })
    """
    

    print(access_bd.get_diary_entries("Sergio"))
    access_bd.close()
    
