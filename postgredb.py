import psycopg2

from resourсes.config import USER, PASSWORD, HOST, DB_NAME


class PostgreDB:

    def __init__(self):
        self.connection = psycopg2.connect(host=HOST, user=USER, password=PASSWORD, database=DB_NAME)
        self.cursor = self.connection.cursor()

    def insert_data(self, data):
        try:
            self.connection.autocommit = True
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS users(
                    id serial PRIMARY KEY,
                    username varchar(50) NOT NULL UNIQUE,
                    user_karma varchar(50) NOT NULL,
                    user_cake_day varchar(50) NOT NULL,
                    post_karma varchar(50) NOT NULL,
                    comment_karma varchar(50) NOT NULL);"""
            )
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS posts(
                    id varchar(50) PRIMARY KEY,
                    post_url varchar(150) NOT NULL,
                    post_date varchar(50) NOT NULL,
                    number_of_comments varchar(50) NOT NULL,
                    number_of_votes varchar(50) NOT NULL,
                    post_category varchar(50) NOT NULL,
                    user_id int,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT);"""
            )
            self.cursor.execute(
                f"""SELECT username from users where username like '{data['username']}';"""
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    f"""INSERT INTO users (username, user_karma, user_cake_day, post_karma, comment_karma) VALUES 
                    ('{data['username']}', '{data['user karma']}', '{data['user cake day']}', 
                    '{data['post karma']}', '{data['comment karma']}');"""
                )
            self.cursor.execute(
                f"""select id from users where username like '{data['username']}';"""
            )
            id_user = self.cursor.fetchone()[0]
            self.cursor.execute(
                f"""INSERT INTO posts VALUES ('{data['unique id']}', '{data['post URL']}', '{data['post date']}', 
                    '{data['number of comments']}', '{data['number of votes']}', '{data['post category']}', 
                    '{id_user}');"""
            )
            self.cursor.execute(
                """SELECT count(*) from posts;"""
            )
            return self.cursor.fetchone()[0]
        except Exception as _ex:
            print(_ex)
            return None

