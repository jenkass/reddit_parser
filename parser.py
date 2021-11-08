import datetime
import logging
import time
import uuid
from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver

"""A module containing a class for parsing a page and logging"""
format = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('reddit')


class Client:
    """Create methods for parsing

    The class contains methods that allow you to get a dynamic page,
    searching article blocks and parse it, save the result to a file
    and a method to run the parser.
    """

    def __init__(self) -> None:
        """Сlass constructor

        Arguments:
        url - path to site
        result - list of saved parsing parameters.
        """
        self.url = url = 'https://www.reddit.com/top?t=month'
        self.result: list[str] = []

    def get_result(self):
        """Searching for posts and getting results

        Sends a request to the site by url, scrolls down the page
        and gets the dynamic markup.
        Searching article blocks and calling the parsing method of each block.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path='resourсes/chromedriver.exe', options=options)
        driver.maximize_window()
        try:
            driver.get(url=self.url)
            time.sleep(3)
            initial_post_count = 0
            while True:
                container = self.parse_page(driver.page_source)
                last_post_count = len(container)
                logger.info(initial_post_count)
                logger.info(last_post_count)
                for i in range(initial_post_count, last_post_count):
                    if len(self.result) == 100:
                        return
                    else:
                        self.parse_block(container[i])
                initial_post_count = last_post_count
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(3)
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

    def parse_page(self, text) -> ResultSet:
        """Parsing a page block

        Gets blocks of posts from the site
        and calls the function parse_block() for each block.
        Takes the path to page markup.
        """
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select(
            'div._1oQyIsiPHYt6nx7VOmd1sz')
        return container

    def parse_block(self, block) -> None:
        """Parsing a single post

        Gets the necessary information from the post
        and saves it to the result list.
        Logs errors in case of missing information.
        """
        block_url = block.select_one('a.SQnoC3ObvgnGjWt90zD9Z')
        if not block_url:
            logger.error('no block url')
            return
        url = 'https://reddit.com' + block_url.get('href')
        if not url:
            logger.error('no elements')
            return
        username = block.select_one('a._2tbHP6ZydRpjI44J3syuqC').text[2:]
        if username == '[deleted]':
            logger.error('no username')
            return
        logger.info(block_url)
        logger.info(url)
        logger.info(username)
        self.result.append(f'{self.get_unique_id()};{url};{username}\n')

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
        self.get_result()
        self.save_result()


if __name__ == '__main__':
    parser = Client()
    parser.run()
