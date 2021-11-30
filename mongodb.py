import pymongo
import logging

from typing import Tuple

from resourсes.config import CLUSTER

DATA_POST: Tuple[str, ...] = ('post URL', 'username', 'post date', 'number of comments',
                              'number of votes', 'post category')  # cortege of the post fields

DATA_USER: Tuple[str, ...] = ('user karma', 'user cake day', 'post karma',
                              'comment karma')  # cortege of the user fields

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


class MongoDB:

    def __init__(self):
        self.client = pymongo.MongoClient(CLUSTER)
        self.db = self.client.reddit
        self.users = self.db.users
        self.posts = self.db.posts

    def insert_data(self, data):
        try:
            if not self.users.find_one({"_id": data["username"]}):
                data_user = {"_id": data["username"]}
                data_user.update({field: data[field] for field in DATA_USER})
                self.users.insert_one(data_user)
            data_post = {"_id": data["unique id"]}
            data_post.update({field: data[field] for field in DATA_POST})
            self.posts.insert_one(data_post)
            return self.posts.count_documents({})
        except Exception as _ex:
            logger.error(_ex)
            return None

    def get_data(self):
        try:
            data = []
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

    def put_data(self, id, data):
        try:
            new_data_post = ({field: data[field] for field in DATA_POST})
            new_data_user = ({field: data[field] for field in DATA_USER})
            if self.posts.update_one({"_id": id}, {"$set": new_data_post}).matched_count == 1:
                if self.users.update_one({"_id": data["username"]}, {"$set": new_data_user}).matched_count == 1:
                    return True
            return None
        except Exception as _ex:
            logger.error(_ex)
            return None

    def delete_data(self, id):
        try:
            username = self.posts.find_one({"_id": id})["username"]
            if self.posts.delete_one({"_id": id}):
                if not self.posts.find_one({"username": username}):
                    self.users.delete_one({"_id": username})
                return True
        except Exception as _ex:
            logger.error(_ex)
            return None

