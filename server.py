from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import json
import datetime
import re

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('logger')

PORT = 8087
NAME_FILE: str = f"reddit-{datetime.datetime.today().strftime('%Y%m%d')}.txt"
DATA = ('unique id', 'post URL', 'username', 'user karma', 'user cake day', 'post karma', 'comment karma', 'post date',
        'number of comments', 'number of votes', 'post category')


class RequestHandler(BaseHTTPRequestHandler):

    def read_file(self):
        try:
            with open(NAME_FILE, 'r') as file:
                list_posts = [post.split(';') for post in file.readlines()]
            result = [{DATA[i]: post[i] for i in range(len(post) - 1)} for post in list_posts]
            return result
        except Exception as _ex:
            logger.error(_ex)

    def write_file(self):
        pass

    def do_GET(self):
        uuid4hex = re.compile('[0-9a-f]{12}1[0-9a-f]{19}')
        if self.path == '/posts/':
            self.send_response(200)
            data = self.read_file()
        elif re.search(uuid4hex, self.path) is not None:
            logger.info('run')
            data = self.read_file()
            for post in data:
                logger.info(post['unique id'])
                if self.path[7:-1] == post['unique id']:
                    self.send_response(200)
                    data = post
                    break
                else:
                    self.send_response(404)
                    data = None
                    break
        else:
            data = None
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    logger.info(f"Server running on port {PORT}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
