import sqlite3


class DatabaseOperations:
    __slots__ = "connection"

    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.create_db()

    def create_db(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patienter(
            förnamn TEXT,
            efternamn TEXT,
            personnummer TEXT,
            tillhörighet TEXT,
            kommentar TEXT
            )
            """)

            self.connection.commit()

    def new_record(self, record: tuple):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("""
            INSERT INTO patienter(förnamn, efternamn, personnummer, tillhörighet, kommentar)
            VALUES(?, ?, ?, ?, ?)
            """, record)

            self.connection.commit()

    def get_all_from_table(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM patienter ORDER BY tillhörighet ASC")
            result = cursor.fetchall()
            return result

    def get_personal_numbers(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT personnummer FROM patienter")
            result = cursor.fetchall()
            return result

    def update_record(self, target_column, value1, value2):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE patienter SET {target_column} = ? WHERE personnummer = ?", (value1, value2))

    def delete_record(self, personal_nr):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM patienter WHERE personnummer = ?", (personal_nr,))

# dbo = DatabaseOperations()
# dbo.create_db()
# dbo.new_record(("Sandra", "Jonson", "330619-4457", "Maggis", "Ny patient"))
# res = dbo.get_all_from_table()
# print(res)
