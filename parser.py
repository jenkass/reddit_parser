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
        url - path to site,
        result - list of saved parsing parameters,
        user_urls - list of urls to user accounts.
        """
        self.url = url = 'https://www.reddit.com/top?t=month'
        self.user_urls = []
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
        options.add_argument('--headless')
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
        uniq_id = self.get_unique_id()
        url = self.get_url(block)
        user_name = self.get_user_name(block)
        user_url = self.get_user_url(block)
        post_date = None
        count_comments = self.get_count_comments(block)
        count_of_votes = self.get_count_of_votes(block)
        post_category = self.get_post_category(block)
        if None in [url, user_name, count_comments, count_of_votes, post_category]:
            return
        self.user_urls.append(user_url)
        self.result.append(f'{uniq_id};{url};{user_name};{post_date};'
                           f'{count_comments};{count_of_votes};{post_category}\n')

    def get_unique_id(self):
        """Generate and return a unique id"""
        return str(uuid.uuid1().hex)

    def get_url(self, block):
        block_url = block.select_one('a.SQnoC3ObvgnGjWt90zD9Z')
        if not block_url:
            logger.error('no block url')
            return
        url = 'https://reddit.com' + block_url.get('href')
        if not url:
            logger.error('no elements')
            return
        logger.info(url)
        return url

    def get_user_name(self, block):
        user_name = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if user_name == '[deleted]' or not user_name:
            logger.error('no user name')
            return
        logger.info(user_name)
        return user_name.text[2:]

    def get_user_url(self, block):
        user_url = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if not user_url:
            logger.error('no user url')
            return
        logger.info(user_url)
        return 'https://reddit.com' + user_url.get('href')

    def get_post_date(self, block):
        pass

    def get_count_comments(self, block):
        count_comments = block.find('span', class_='FHCV02u6Cp2zYL0fhQPsO').text
        if not count_comments:
            logger.error('no comments')
            return
        logger.info(count_comments)
        return count_comments

    def get_count_of_votes(self, block):
        count_of_votes = block.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text
        if not count_of_votes:
            logger.error('no votes')
            return
        logger.info(count_of_votes)
        return count_of_votes

    def get_post_category(self, block):
        post_category = block.select_one('a._3ryJoIoycVkA88fy40qNJc')
        if not post_category:
            logger.error('no category')
            return
        logger.info(post_category)
        return post_category.get('href')[3:-1]

    def save_result(self) -> None:
        """Save the result to a file

        Creates or overwrites a file with parsing results.
        """
        name_file: str = f"reddit-{datetime.datetime.today().strftime('%Y%m%d%H%M')}.txt"
        with open(name_file, 'w', encoding="utf-8") as f:
            f.writelines(self.result)

    def run(self) -> None:
        """ Run the parser and show run time"""
        start_time = time.time()
        self.get_result()
        self.save_result()
        print(f"------ {time.time() - start_time} seconds ------")


if __name__ == '__main__':
    parser = Client()
    parser.run()
