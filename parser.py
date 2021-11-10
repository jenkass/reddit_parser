import datetime
import logging
import time
from typing import List

from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from selector import base
"""A module containing a class for parsing a site and logging"""
format = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('reddit')


class Client(base.BaseSelector):
    """Create methods for parsing

    The class contains methods that allow you to get a dynamic page,
    searching article blocks and parse it, пo to a user page and parse it,
    save the result to a file
    and a method to run the parser.
    """

    def __init__(self):
        """Сlass constructor

        Arguments:
        url - path to site,
        result - list of saved parsing parameters,
        """
        self.url = 'https://www.reddit.com/top?t=month'
        self.result: List[str] = []

    def start_selenium(self) -> WebDriver:
        """Create a Chrome Web Driver """
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        driver = webdriver.Chrome(executable_path='resourсes/chromedriver.exe', options=options)
        return driver

    def get_result(self) -> None:
        """Searching for posts and getting results

        Sends a request to the site by url, scrolls down the page
        and gets the dynamic markup.
        Searching article blocks and calling the parsing method of each block.
        """
        try:
            driver = self.start_selenium()
            driver.maximize_window()
            driver.get(url=self.url)
            initial_post_count = 0
            while True:
                container = self.parse_page(driver.page_source)
                last_post_count = len(container)
                logger.info(initial_post_count)
                logger.info(last_post_count)
                for i in range(initial_post_count, last_post_count):
                    if len(self.result) == 3:
                        return
                    else:
                        self.parse_block(container[i])
                initial_post_count = last_post_count
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

    def parse_page(self, text) -> ResultSet:
        """Parsing a page block

        Gets blocks of posts from the site
        and and his return.
        """
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select(
            'div._1oQyIsiPHYt6nx7VOmd1sz')
        return container

    def parse_block(self, block) -> None:
        """Parsing a single post

        Gets the necessary information from the post
        and the user account, saves it to the result list.
        Logs errors in case of missing information.
        """
        uniq_id = self.get_unique_id()
        url = self.get_post_url(block)
        user_name = self.get_user_name(block)
        user_url = self.get_user_url(block)
        post_date = self.get_post_date(block)
        count_comments = self.get_count_comments(block)
        count_of_votes = self.get_count_of_votes(block)
        post_category = self.get_post_category(block)
        if None in [url, user_name, count_comments, count_of_votes, post_date, post_category]:
            return
        user_data = self.parse_user_account(user_url)
        if user_data is None:
            return
        self.result.append(f'{uniq_id};{url};{user_name};{user_data["karma"]};{user_data["cake day"]};'
                           f'{user_data["post karma"]};{user_data["comment karma"]};{post_date};'
                           f'{count_comments};{count_of_votes};{post_category}\n')

    def parse_user_account(self, user_url) -> dict:
        """Parsing a user account

            Getting the necessary information about the user (also in hidden blocks).
            Return the dictionary with the user's data.
            Logs errors in case of missing information.
            """
        driver = self.start_selenium()
        driver.maximize_window()
        driver.get(url=user_url)
        try:
            block_to_hover = driver.find_element_by_id("profile--id-card--highlight-tooltip--karma")
        except Exception as _ex:
            print(_ex)
            return
        hover = ActionChains(driver).move_to_element(block_to_hover)
        hover.perform()
        soup = BeautifulSoup(driver.page_source, 'lxml')
        block = soup.select_one('div._3odBTM7RqvRgN1nvkf5k8B')
        block_karma = soup.select_one('div._3uK2I0hi3JFTKnMUFHD2Pd')
        try:
            if block and block_karma:
                karma = self.get_karma(block)
                cake_day = self.get_cake_day(block)
                post_and_comment_karma = self.get_post_and_comment_karma(block_karma)

                if None in [karma, cake_day, post_and_comment_karma]:
                    return
                return dict([('karma', karma), ('cake day', cake_day), ('post karma', post_and_comment_karma[0]),
                             ('comment karma', post_and_comment_karma[1])])
            else:
                logger.error('age limit')
                return
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

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
