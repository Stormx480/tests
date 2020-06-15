import sqlite3
from collections import namedtuple


class Singleton(type):

    _instances = {}

    def __new__(class_, *args, **kwargs):

        if class_ not in class_._instances:

            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)

        return class_._instances[class_]


class Database(metaclass=Singleton):

    def __init__(self):
        self.conn = sqlite3.connect("test_bot_database.db",
                                    detect_types=sqlite3.PARSE_DECLTYPES,
                                    check_same_thread=False)
        self.check_tables()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def connection_decorate(a_function_to_decorate):

        def wrapper(self, *args, **kwargs):

            cursor = self.conn.cursor()

            kwargs["cursor"] = cursor

            data = a_function_to_decorate(self, *args, **kwargs)

            self.conn.commit()
            cursor.close()

            return data

        return wrapper

    @connection_decorate
    def check_tables(self, cursor=None):

        sql = "SELECT name FROM sqlite_master WHERE type = 'table'"
        cursor.execute(sql)
        response = cursor.fetchall()

        tables_list = ['users', 'links']

        for x in response:
            if x[0] in tables_list:
                tables_list.remove(x[0])

        if len(tables_list) == 0:
            print('Проверка таблиц завершена.')
            return True
        else:
            for table_name in tables_list:
                eval('self.create_table_'+table_name)()
                return True

    @connection_decorate
    def create_table_users(self, cursor=None):

        # Я в курсе как работает IF NOT EXISTS и что выше я уже проверил наличие.
        sql = "CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY, username text UNIQUE, password text)"
        cursor.execute(sql)

        return True

    @connection_decorate
    def create_table_links(self, cursor=None):

        sql = "CREATE TABLE IF NOT EXISTS links " \
              "(id integer PRIMARY KEY, link text UNIQUE NOT NULL, name text, downloadable boolean DEFAULT(TRUE), " \
              "user_id integer NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))"
        cursor.execute(sql)

        return True

    @connection_decorate
    def create_user(self, username, password, cursor=None):

        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        cursor.execute(sql, (username, password))
        user_id = cursor.lastrowid

        User = namedtuple('User', 'id name'.split())

        user = User(id=user_id, name=username)

        return user

    @connection_decorate
    def check_user(self, username, cursor=None):

        sql = "SELECT id, password FROM users WHERE username=?"
        cursor.execute(sql, (username,))
        response = cursor.fetchall()

        print(response)

        if len(response) == 0:
            return None
        else:
            user_id = response[0][0]
            password_hash = response[0][1]

        User = namedtuple('User', 'id name password_hash'.split())

        user = User(id=user_id, name=username, password_hash=password_hash)

        return user

    @connection_decorate
    def get_links(self, user_id, cursor=None):

        sql = "SELECT id, link, name, downloadable FROM links WHERE user_id = ?"
        cursor.execute(sql, (user_id,))
        response = cursor.fetchall()

        return response

    @connection_decorate
    def get_link(self, link_id, cursor=None):

        sql = "SELECT link, name FROM links WHERE id=? AND downloadable=True"
        cursor.execute(sql, (link_id,))
        response = cursor.fetchall()

        if len(response) == 0:
            return None
        else:
            return {
                'url': response[0][0],
                'name': response[0][1]
            }

    @connection_decorate
    def create_link(self, name, url, user_id, cursor=None):

        sql = "INSERT INTO links (name, link, user_id) VALUES (?, ?, ?)"
        cursor.execute(sql, (name, url, user_id))

        return True

    @connection_decorate
    def delete_link(self, link_id, cursor=None):

        sql = "DELETE FROM links WHERE id=?"
        cursor.execute(sql, (link_id,))

        return True


if __name__ == '__main__':
    db = Database()
    db.create_user('test', 'test')

