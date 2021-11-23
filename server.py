import datetime
import json
import logging
import re

from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Tuple, Optional, NoReturn, Pattern

PORT: int = 8087
NAME_FILE: str = f"reddit-{datetime.datetime.today().strftime('%Y%m%d')}.txt"
DATA: Tuple[str, ...] = ('unique id', 'post URL', 'username', 'user karma', 'user cake day', 'post karma',
                         'comment karma', 'post date', 'number of comments', 'number of votes', 'post category')
UUID4HEX: Pattern = re.compile('[0-9a-f]{12}1[0-9a-f]{19}')

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')


class RequestHandler(BaseHTTPRequestHandler):

    def read_file(self) -> Optional[List[Dict[str, str]]]:
        try:
            with open(NAME_FILE, 'r') as file:
                list_posts: List[List[str]] = [post.split(';') for post in file.readlines()]
            return [{DATA[i]: post[i] for i in range(len(post) - 1)} for post in list_posts]
        except Exception as _ex:
            logger.error(_ex)
            return None

    def write_file(self, post: Dict[str, str]) -> Optional[int]:
        try:
            with open(NAME_FILE, 'a+') as file:
                file.write(f"{';'.join(post.values())};\n")
            return len(open(NAME_FILE, 'r').readlines())
        except Exception as _ex:
            logger.error(_ex)
            return None

    def match_check_id(self, new_post: Dict[str, str]) -> bool:
        list_posts: Optional[List[Dict[str, str]]] = self.read_file()
        if list_posts is not None:
            for post in list_posts:
                if new_post['unique id'] == post['unique id']:
                    logger.error('post with this unique id already exists')
                    return False
            return True
        return False

    def do_GET(self) -> NoReturn:
        data: Optional[List[Dict[str, str]]] = self.read_file()

        if data is not None:

            if self.path == '/posts/':
                self.send_response(200)
                logger.info('response sent')

            elif re.search(UUID4HEX, self.path) is not None:
                logger.info('run')

                for post in data:
                    logger.info(post['unique id'])

                    if self.path[7:-1] == post['unique id']:
                        self.send_response(200)
                        data: Dict[str, str] = post
                        logger.info('response sent')
                        break

                    else:
                        self.send_response(404)
                        data: str = 'Not found'
                        break

            else:
                logger.error('unknown path for GET')
                data = None

        self.send_header('content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self) -> NoReturn:
        if self.path == '/posts/':
            length = int(self.headers.get('content-length'))
            new_post: Dict[str, str] = json.loads(self.rfile.read(length))

            if self.match_check_id(new_post):
                row_number: Optional[int] = self.write_file(new_post)

                if row_number is not None:
                    self.send_response(201)
                    logger.info('Post added')
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


def run_server() -> NoReturn:
    server_address: Tuple[str, int] = ('', PORT)
    httpd: HTTPServer = HTTPServer(server_address, RequestHandler)
    logger.info(f"Server running on port {PORT}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
