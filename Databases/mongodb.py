"""The module contains a class with methods for interacting with the MongoDB No-SQL database"""

import logging
from typing import Tuple, Dict, Optional, List

import pymongo

from Databases.Base_Database.abstract_database import Database
from resourсes.config import CLUSTER

DATA_POST: Tuple[str, ...] = ('post URL', 'username', 'post date', 'number of comments',
                              'number of votes', 'post category')  # cortege of the post fields

DATA_USER: Tuple[str, ...] = ('user karma', 'user cake day', 'post karma',
                              'comment karma')  # cortege of the user fields

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


class MongoDB(Database):
    """Create a class for working with the database

        The class contains methods that allow you to read, write,
        update or delete data in database collections.
        """

    def __init__(self):
        """Constructor

        Arguments:
        client - database cluster.
        db - database.
        users - collection users.
        posts - collection posts.
        """
        self.client: pymongo.MongoClient = pymongo.MongoClient(CLUSTER)
        self.db = self.client.reddit
        self.users = self.db.users
        self.posts = self.db.posts

    def insert_data(self, data: Dict[str, str]) -> Optional[int]:
        """Add data to collections of posts and users

        :param data: dictionary (object) containing the data of one post and one user
        :return: document number in the collection of posts or None
        """
        try:
            if not self.users.find_one({"_id": data["username"]}):
                data_user: Dict[str, str] = {"_id": data["username"]}
                data_user.update({field: data[field] for field in DATA_USER})
                self.users.insert_one(data_user)

            data_post: Dict[str, str] = {"_id": data["unique id"]}
            data_post.update({field: data[field] for field in DATA_POST})
            self.posts.insert_one(data_post)

            return self.posts.count_documents({})
        except Exception as _ex:
            logger.error(_ex)
            return None

    def get_data(self) -> Optional[List[Dict[str, str]]]:
        """Get all data from the database collections

        :return: list of dictionaries (objects) that contain data about the post and user or None
        """
        try:
            data: Optional[List[Dict[str, str]]] = []

            for post in self.posts.find():
                post.update(self.users.find_one({"_id": post["username"]}, {"_id": 0, "user karma": 1,
                                                                            "user cake day": 1, "post karma": 1,
                                                                            "comment karma": 1}))
                data.append(post)

            if not data:
                return None

            return data
        except Exception as _ex:
            logger.error(_ex)
            return None

    def put_data(self, id_str: str, data: Dict[str, str]) -> Optional[bool]:
        """Update data in database collections

        :param id_str: unique post key
        :param data: dictionary (object) containing the data of one post and one user which is replaced by
        :return: bool value (flag) or None
        """
        try:
            new_data_post: Dict[str, str] = {field: data[field] for field in DATA_POST}
            new_data_user: Dict[str, str] = {field: data[field] for field in DATA_USER}

            if self.users.find_one({"_id": data["username"]}):
                if self.posts.update_one({"_id": id_str}, {"$set": new_data_post}).matched_count == 1:
                    if self.users.update_one({"_id": data["username"]}, {"$set": new_data_user}).matched_count == 1:
                        return True

            return None
        except Exception as _ex:
            logger.error(_ex)
            return None

    def delete_data(self, id_str: str) -> Optional[bool]:
        """Remove data from the database collections

        :param id_str: unique post key
        :return: bool value (flag) or None
        """
        try:
            username: str = self.posts.find_one({"_id": id_str})["username"]

            if self.posts.delete_one({"_id": id_str}):
                if not self.posts.find_one({"username": username}):
                    self.users.delete_one({"_id": username})
                return True

            return None
        except Exception as _ex:
            logger.error(_ex)
            return None
