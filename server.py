"""Module containing the REST API server class with writing and reading data from file"""

import datetime
import json
import logging
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Tuple, Optional, NoReturn, Pattern

PORT: int = 8087  # server port
NAME_FILE: str = f"reddit-{datetime.datetime.today().strftime('%Y%m%d')}.txt"  # name of the resulting file
DATA: Tuple[str, ...] = ('unique id', 'post URL', 'username', 'user karma', 'user cake day', 'post karma',
                         'comment karma', 'post date', 'number of comments',
                         'number of votes', 'post category')  # cortege of the post fields
UUID4HEX: Pattern = re.compile('/posts/[0-9a-f]{12}1[0-9a-f]{19}/')  # pattern for a unique key (uuid4.hex)

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


class RequestHandler(BaseHTTPRequestHandler):
    """Creating handlers for CRUD methods and writing and reading data from the file

        The class contains methods that allow you to read, write,
        update or delete lines (post data) in the file.
        Also the class contains GET, POST, PUT, DELETE methods handlers
        """

    def read_file(self) -> Optional[List[Dict[str, str]]]:
        """Read all lines (post data) from the file and translate them into the dictionary

        :return: list of dictionaries (objects) that contain data about the post or None
        """
        try:
            with open(NAME_FILE, 'r') as file:
                list_posts: List[List[str]] = [post.split(';') for post in file.readlines()]
            return [{DATA[i]: post[i] for i in range(len(post) - 1)} for post in list_posts]
        except Exception as _ex:
            logger.error(_ex)
            return None

    def write_file(self, post: Dict[str, str]) -> Optional[int]:
        """Open the file for writing and write the post data on a new line

        :param post: dictionary (object) containing the data of one post
        :return: the number of the line inserted into the file or None
         """
        try:
            with open(NAME_FILE, 'a') as file:
                if not self.match_check_id(post):
                    return None
                file.write(f"{';'.join(post.values())};\n")
            return len(open(NAME_FILE, 'r').readlines())
        except Exception as _ex:
            logger.error(_ex)
            return None

    def update_file(self, uuid: str, update_post: Dict[str, str]) -> Optional[bool]:
        """Read all lines from the file and update the data of the required post

        :param uuid: unique post key
        :param update_post: dictionary (object) containing the data of one post which is replaced by
        :return: bool value (flag) or None
        """
        try:
            with open(NAME_FILE, 'r') as old_file:
                list_posts: List[str] = old_file.readlines()

            for i, post in enumerate(list_posts):
                if post.startswith(uuid):
                    list_posts[i]: str = f"{';'.join(update_post.values())};\n"

                    with open(NAME_FILE, 'w') as new_file:
                        new_file.writelines(list_posts)

                    return True
        except Exception as _ex:
            logger.error(_ex)
            return None

    def delete_row_in_file(self, uuid: str) -> Optional[bool]:
        """Read all lines from the file and delete the line of the required post

        :param uuid: unique post key
        :return: bool value (flag) or None
        """
        try:
            with open(NAME_FILE, 'r') as old_file:
                list_posts: List[str] = old_file.readlines()

            for i, post in enumerate(list_posts):
                if post.startswith(uuid):
                    list_posts.pop(i)

                    with open(NAME_FILE, 'w') as new_file:
                        new_file.writelines(list_posts)

                    return True
        except Exception as _ex:
            logger.error(_ex)
            return None

    def match_check_id(self, new_post: Dict[str, str]) -> bool:
        """Compare all existing unique keys in the file with the obtained

        :param new_post: dictionary (object) containing the data of one post which all existing posts will be compared
        :return: bool value (flag)
        """
        list_posts: Optional[List[Dict[str, str]]] = self.read_file()

        if list_posts is not None:

            for post in list_posts:

                if new_post['unique id'] == post['unique id']:
                    logger.error('post with this unique id already exists')
                    return False
        return True


    def do_GET(self) -> NoReturn:
        """REST method GET

        A method which waits for certain endpoints
        and returns either the contents of the entire file in json,
        or returns the contents of a string with a unique key specified in the url.
        """
        data: Optional[List[Dict[str, str]]] = self.read_file()

        if data is not None:

            if self.path == '/posts/':
                self.send_response(200)
                logger.info('response sent')

            elif re.search(UUID4HEX, self.path) is not None:
                for post in data:

                    if self.path[7:-1] == post['unique id']:
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
        and writes new post data to the file
        if there is no post with the same unique key.
        """
        if self.path == '/posts/':
            length = int(self.headers.get('content-length'))
            new_post: Dict[str, str] = json.loads(self.rfile.read(length))
            row_number: Optional[int] = self.write_file(new_post)
            if row_number is not None:
                self.send_response(201)
                logger.info('post added')
                data: Optional[Dict[str, int]] = {"unique id": row_number}

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
        and updates the post data with the unique key obtained in the url in the file.
        """
        if re.search(UUID4HEX, self.path) is not None:
            length = int(self.headers.get('content-length'))
            update_post: Dict[str, str] = json.loads(self.rfile.read(length))

            if self.update_file(self.path[7:-1], update_post):
                self.send_response(200)
                logger.info('post updated')
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
        and deletes the post data with the unique key obtained in the url in the file.
        """
        if re.search(UUID4HEX, self.path) is not None:

            if self.delete_row_in_file(self.path[7:-1]):
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