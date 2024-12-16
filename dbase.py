import pymysql
from cryptography.fernet import Fernet, InvalidToken


class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, host, user, password, db, encryption_key):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.encryption_key = encryption_key
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        self.cipher = Fernet(self.encryption_key)

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
        return self.cipher.encrypt(data.encode()).decode() if data != None else None

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(str(encrypted_data).encode()).decode()

    def decrypt_data(self, data_list: list):
        for item in data_list:
            for field in item.keys():
                if item[field] is not None:
                    try:
                        item[field] = self.decrypt(item[field])
                    except (InvalidToken, TypeError, AttributeError):
                        pass
        return data_list

    def execute_and_fetch(self, query, params=None, many=False):
        self.execute_query(query, params)
        if many:
            result = self.cursor.fetchall()
        else:
            result = self.cursor.fetchone()
        return result

    def close(self):
        self.cursor.close()
        self.connection.close()