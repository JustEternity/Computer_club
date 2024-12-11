import pymysql
from cryptography.fernet import Fernet

class Database:
    def __init__(self, host, user, password, db, encryption_key):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        self.cipher = Fernet(encryption_key)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка: {e}")
            self.connection.rollback()

    def fetch_all(self, query, params=None):
        self.execute_query(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        self.execute_query(query, params)
        return self.cursor.fetchone()

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def decrypt_data(self, data_list):
        for item in data_list:
            for field in item:
                item[field] = self.decrypt(item[field])
        return data_list

    def close(self):
        self.cursor.close()
        self.connection.close()