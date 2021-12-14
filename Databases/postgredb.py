"""The module contains a class with methods for interacting with the PostgreSQL database"""

import logging
from typing import Tuple, Dict, Optional, List

import psycopg2

from Databases.Base_Database.abstract_database import Database
from resourсes.config import USER, PASSWORD, HOST, DB_NAME

DATA: Tuple[str, ...] = ('_id', 'post URL', 'username', 'user karma', 'user cake day', 'post karma',
                         'comment karma', 'post date', 'number of comments',
                         'number of votes', 'post category')  # cortege of the post fields

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


class PostgreDB(Database):
    """Create a class for working with the database

    The class contains methods that allow you to read, write,
    update or delete data in database tables.
    """

    def __init__(self):
        """Constructor

        Create 2 tables if they do not already exist in the database.
        Arguments:
        connection - link to the database server.
        cursor - object for interaction with the database.
        connection.autocommit - automatically save all changes to the database.
        """
        self.connection: psycopg2.connect = psycopg2.connect(user=USER, password=PASSWORD, database=DB_NAME)
        self.cursor = self.connection.cursor()
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

    def insert_data(self, data: Dict[str, str]) -> Optional[int]:
        """Add data to tables of posts and users

        :param data: dictionary (object) containing the data of one post and one user
        :return: row number in the table of posts or None
        """
        try:
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

            id_user: int = self.cursor.fetchone()[0]

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
            logger.error(_ex)
            return None

    def get_data(self) -> Optional[List[Dict[str, str]]]:
        """Get all data from the database tables

        :return: list of dictionaries (objects) that contain data about the post and user or None
        """
        try:
            self.cursor.execute(
                f"""SELECT p.id, p.post_url, u.username, u.user_karma, u.user_cake_day, u.post_karma, u.comment_karma, 
                p.post_date, p.number_of_comments, p.number_of_votes, p.post_category  
                FROM posts as p join users as u on p.user_id = u.id;"""
            )

            list_posts: List[Tuple[str, ...]] = self.cursor.fetchall()

            if not list_posts:
                return None

            return [dict(zip(DATA, post)) for post in list_posts]
        except Exception as _ex:
            logger.error(_ex)
            return None

    def put_data(self, id_str: str, data: Dict[str, str]) -> Optional[bool]:
        """Update data in database tables

        :param id_str: unique post key
        :param data: dictionary (object) containing the data of one post and one user which is replaced by
        :return: bool value (flag) or None
        """
        try:
            self.cursor.execute(
                f"""SELECT id from users where username like '{data['username']}';"""
            )
            user_id: int = self.cursor.fetchone()[0]

            self.cursor.execute(
                f"""UPDATE posts SET
                post_url = '{data['post URL']}',
                post_date = '{data['post date']}',
                number_of_comments = '{data['number of comments']}',
                number_of_votes = '{data['number of votes']}',
                post_category = '{data['post category']}',
                user_id = {user_id}
                where id like '{id_str}';"""
            )

            self.cursor.execute(
                f"""UPDATE users SET
                username = '{data['username']}',
                user_karma = '{data['user karma']}',
                user_cake_day = '{data['user cake day']}',
                post_karma = '{data['post karma']}',
                comment_karma = '{data['comment karma']}'
                where id = {user_id}"""
            )

            return True
        except Exception as _ex:
            logger.error(_ex)
            return None

    def delete_data(self, id_str: str) -> Optional[bool]:
        """Remove data from the database tables

        :param id_str: unique post key
        :return: bool value (flag) or None
        """
        try:
            self.cursor.execute(
                f"""SELECT user_id from posts where id like '{id_str}';"""
            )

            user_id: int = self.cursor.fetchone()[0]

            self.cursor.execute(
                f"""DELETE FROM posts where id like '{id_str}';"""
            )

            self.cursor.execute(
                f"""SELECT * from posts where user_id = {user_id};"""
            )

            if not self.cursor.fetchone():
                self.cursor.execute(
                    f"""DELETE FROM users where id = {user_id};"""
                )

            return True
        except Exception as _ex:
            logger.error(_ex)
            return None
