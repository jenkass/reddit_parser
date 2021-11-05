import requests
from bs4 import BeautifulSoup
import logging
import datetime
import uuid
import json
import pprint
"""A module containing a class for parsing a page and logging"""
format = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('reddit')


class Client:
    """Create methods for parsing

    The class contains methods that allow you to load a page,
    parse it and roadblocks, save the result to a file
    and a method to run the parser.
    """

    def __init__(self) -> None:
        """Сlass constructor

        Arguments:
        session - an object for saving certain parameters in requests to the same site
        session.headers - overridden request header in order not to be suspected of parsing
        result - list of saved parsing parameters.
        """
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/95.0.4638.69 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result: list[str] = []

    def load_page(self) -> str:
        """Return page markup

        Sends a request to the site by url and gets the markup,
        otherwise generates an exception.
         Returns the page layout.
        """
        url = 'https://www.reddit.com/top?t=month'
        response = self.session.get(url=url)
        response.raise_for_status()
        return response.text

    def parse_page(self, text: str) -> None:
        """Parsing a page block

        Gets blocks of posts from the site
        and calls the function parse_block() for each block.
        Accepts page layout.
        """
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select(
            'div._1oQyIsiPHYt6nx7VOmd1sz', limit=100)
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block) -> None:
        """Parsing a single post

        Gets the necessary information from the post
        and saves it to the result list.
        Logs errors in case of missing information
        """

        url = 'https://reddit.com' + block.select_one('a.SQnoC3ObvgnGjWt90zD9Z').get('href')

        if not url:
            logger.error('no elements')
            return
        logger.info(url)

        self.result.append(f"{self.get_unique_id()},{url}\n")

    def get_unique_id(self):
        """Generate and return a unique id"""
        return str(uuid.uuid1().hex)

    def save_result(self) -> None:
        """Save the result to a file

        Creates or overwrites a file with parsing results.
        """
        name_file: str = f"reddit-{datetime.datetime.today().strftime('%Y%m%d%H%M')}.txt"
        with open(name_file, 'w', encoding="utf-8") as f:
            f.writelines(self.result)

    def run(self) -> None:
        """ Run the parser"""
        text = self.load_page()
        self.parse_page(text=text)
        self.save_result()


if __name__ == "__main__":
    parser = Client()
    parser.run()
