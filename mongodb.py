from typing import Tuple

import pymongo
import logging

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
