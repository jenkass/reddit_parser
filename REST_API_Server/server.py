"""Module containing the REST API server class with writing and reading data from databases"""

import argparse
from argparse import Namespace
import json
import logging
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Tuple, Optional, NoReturn, Pattern, Any

from Databases.mongodb import MongoDB
from Databases.postgredb import PostgreDB

PORT: int = 8087  # server port
DATA: Tuple[str, ...] = ('unique id', 'post URL', 'username', 'user karma', 'user cake day', 'post karma',
                         'comment karma', 'post date', 'number of comments',
                         'number of votes', 'post category')  # cortege of the post fields
UUID4HEX: Pattern = re.compile('/posts/[0-9a-f]{12}1[0-9a-f]{19}/')  # pattern for a unique key (uuid4.hex)
REG_UUID: Pattern = re.compile('[0-9a-f]{12}1[0-9a-f]{19}')  # pattern for the unique key in the url

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


def optional_args() -> Any:
    """Get optional parameters

    Sets one optional parameter - database.
    :return: args - a list with the received parameters
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-db', '--database', type=str, default='mongo', help='database for saving data')
    args: Namespace = parser.parse_args()
    if args.database == 'mongo':
        return MongoDB()
    elif args.database == 'postgre':
        return PostgreDB()
    else:
        logger.error("unknown database")
        return None


class RequestHandler(BaseHTTPRequestHandler):
    """Creating handlers for CRUD methods

    The class contains GET, POST, PUT, DELETE methods handlers
    """

    db = optional_args()

    @staticmethod
    def check_valid_post(post: Dict[str, str]) -> bool:
        """Check the validity of the post

        :param post: dictionary (object) containing the data of one post
        :return: bool value (flag)
        """
        if len(post) != len(DATA):
            logger.error('The amount of data in the post is invalid')
            return False

        for i, (key, value) in enumerate(post.items()):
            if key != DATA[i]:
                logger.error('invalid key')
                return False

            if not isinstance(value, str):
                logger.error('invalid type value')
                return False
        return True

    def do_GET(self) -> NoReturn:
        """REST method GET

        A method which waits for certain endpoints
        and returns either all data from the database,
        or data about a specific post and user.
        """
        data: Optional[List[Dict[str, str]]] = self.db.get_data()

        if data is not None:

            if self.path == '/posts/':
                self.send_response(200)
                logger.info('response sent')

            elif re.search(UUID4HEX, self.path) is not None:
                url_uuid: str = re.search(REG_UUID, self.path).group()

                for post in data:

                    if url_uuid == post['_id']:
                        self.send_response(200)
                        data: Dict[str, str] = post
                        logger.info('response sent')
                        break

                else:
                    self.send_response(404)
                    data: str = 'Not found'

            else:
                logger.error('unknown path for GET')
                data = None

        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self) -> NoReturn:
        """REST method POST

        A method which waits for certain endpoints
        and writes new data to database
        if there is no post with the same unique key.
        """
        if self.path == '/posts/':
            length = int(self.headers.get('content-length'))
            new_post: Dict[str, str] = json.loads(self.rfile.read(length))
            if self.check_valid_post(new_post):
                row_number: Optional[int] = self.db.insert_data(new_post)
                if row_number is not None:
                    self.send_response(201)
                    logger.info('post added')
                    data: Optional[Dict[str, int]] = {"unique id": row_number}

                else:
                    data = None

            else:
                data = None

        else:
            logger.error('unknown path for POST')
            data = None

        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_PUT(self) -> NoReturn:
        """REST method PUT

        A method which waits for certain endpoints
        and updates data with the unique key obtained in the url.
        """
        if re.search(UUID4HEX, self.path) is not None:
            length = int(self.headers.get('content-length'))
            update_post: Dict[str, str] = json.loads(self.rfile.read(length))

            if self.check_valid_post(update_post):
                url_uuid: str = re.search(REG_UUID, self.path).group()

                if self.db.put_data(url_uuid, update_post):
                    self.send_response(200)
                    logger.info('post updated')
                    data = None

                else:
                    data = None

            else:
                data = None

        else:
            logger.error('unknown path for PUT')
            data = None

        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_DELETE(self) -> NoReturn:
        """REST method DELETE

        A method which waits for certain endpoints
        and deletes data with the unique key obtained in the url.
        """
        if re.search(UUID4HEX, self.path) is not None:
            url_uuid: str = re.search(REG_UUID, self.path).group()

            if self.db.delete_data(url_uuid):
                self.send_response(200)
                logger.info('row was deleted')
                data = None

            else:
                data = None

        else:
            logger.error('unknown path for DELETE')
            data = None

        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server() -> NoReturn:
    """ Run the server"""
    server_address: Tuple[str, int] = ('', PORT)
    httpd: HTTPServer = HTTPServer(server_address, RequestHandler)
    logger.info(f"Server running on port {PORT}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
