"""A module containing a class for parsing a site and logging"""

import argparse
from argparse import Namespace
import json
import logging
import requests
import time
from typing import Dict, List, NoReturn, Optional

from bs4 import BeautifulSoup, ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selector import base

DOMEN: str = 'https://reddit.com'  # reddit domain
SECONDARY_URL: str = '/top?t=month'  # url to the top posts of the month

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('reddit')


class Client(base.BaseSelector):
    """Create methods for parsing

    The class contains methods that allow you to get a dynamic page,
    searching article blocks and parse it,searching a data on the user page and parse it,
    sends POST requests to the server with the received data
    and a method to run the parser.
    """

    def __init__(self):
        """Constructor

        Arguments:
        url - path to site.
        count_result_posts - the number of posts sent to the server.
        """
        self.url: str = DOMEN + SECONDARY_URL
        self.count_result_posts: int = 0

    def optional_args(self) -> Namespace:
        """Get optional parameters

        Sets one optional parameter - the number of posts.
        :return: args - a list with the received parameters
        """
        parser: argparse.ArgumentParser = argparse.ArgumentParser()
        parser.add_argument('-cp', '--count_posts', type=int, default=1000, help='number of posts for parsing')
        args: Namespace = parser.parse_args()
        return args

    def send_post_request(self, post: Dict[str, str]) -> NoReturn:
        """Send POST request to API

        :param post: dictionary (object) containing the data of one post
        """
        api_url: str = 'http://localhost:8087/posts/'
        headers = {"Content-Type": "application/json"}
        requests.post(api_url, data=json.dumps(post), headers=headers)

    def start_selenium(self) -> WebDriver:
        """Create a Chrome Web Driver

         :return: Web Driver
         """
        options: Options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                             "like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        driver: WebDriver = webdriver.Chrome(executable_path='resourсes/chromedriver.exe', options=options)
        return driver

    def get_result(self) -> None:
        """Searching for posts and getting results

        Sends a request to the site by url, scrolls down the page
        and gets the dynamic markup.
        Searching article blocks and calling the parsing method of each block.
        :return: None - to exit the function
        """
        driver = self.start_selenium()
        driver.maximize_window()
        driver.get(url=self.url)
        try:
            count_post: int = self.optional_args().count_posts
            initial_post_count: int = 0
            while True:
                container: ResultSet = self.parse_page(driver.page_source)
                last_post_count: int = len(container)
                logger.info(initial_post_count)
                logger.info(last_post_count)
                for i in range(initial_post_count, last_post_count):
                    if self.count_result_posts == count_post:
                        return None
                    else:
                        self.parse_block(container[i])
                initial_post_count = last_post_count
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        except Exception as _ex:
            logger.error(_ex)
        finally:
            driver.close()
            driver.quit()

    def parse_page(self, text: str) -> ResultSet:
        """Parsing a page block

        Gets blocks of posts from the site
        and and his return.
        :param text: all the markup of the page
        :return: list of all posts
        """
        soup = BeautifulSoup(text, 'lxml')
        container: ResultSet = soup.select(
            'div._1oQyIsiPHYt6nx7VOmd1sz')
        return container

    def parse_block(self, block: Tag) -> None:
        """Parsing a single post

        Gets the necessary information from the post
        and the user account, sends POST requests to the server with the received data.
        Logs errors in case of missing information.
        :param block: all the markup of one post
        :return: None - to exit the function
        """
        uniq_id: str = self.get_unique_id()
        url: Optional[str] = self.get_post_url(block)
        user_name: Optional[str] = self.get_user_name(block)
        user_url: Optional[str] = self.get_user_url(block)
        post_date: Optional[str] = self.get_post_date(block)
        count_comments: Optional[str] = self.get_count_comments(block)
        count_of_votes: Optional[str] = self.get_count_of_votes(block)
        post_category: Optional[str] = self.get_post_category(block)
        if None in [url, user_name, count_comments, count_of_votes, post_date, post_category]:
            return None

        user_data: Dict[str, str] = self.parse_user_account(user_url)
        if user_data is None:
            return None

        post: Dict[str, str] = {"unique id": uniq_id, "post URL": url, "username": user_name,
                                "user karma": user_data["karma"], "user cake day": user_data["cake day"],
                                "post karma": user_data["post karma"], "comment karma": user_data["comment karma"],
                                "post date": post_date, "number of comments": count_comments,
                                "number of votes": count_of_votes, "post category": post_category}
        self.send_post_request(post)
        self.count_result_posts += 1

    def parse_user_account(self, user_url: str) -> Optional[Dict[str, str]]:
        """Parsing a user account

            Getting the necessary information about the user (also in hidden blocks).
            Return the dictionary with the user's data.
            Logs errors in case of missing information.
            :param user_url: link to user page
            :return: Dictionary with received data or None - to exit the function
            """
        driver: WebDriver = self.start_selenium()
        driver.maximize_window()
        driver.get(url=user_url)
        try:
            block_to_hover: WebElement = driver.find_element_by_id("profile--id-card--highlight-tooltip--karma")
        except Exception as _ex:
            logger.error(_ex)
            return None
        hover: ActionChains = ActionChains(driver).move_to_element(block_to_hover)
        hover.perform()
        soup = BeautifulSoup(driver.page_source, 'lxml')
        block: Tag = soup.select_one('div._3odBTM7RqvRgN1nvkf5k8B')
        block_karma: Tag = soup.select_one('div._3uK2I0hi3JFTKnMUFHD2Pd')
        try:
            if block and block_karma:
                karma: Optional[str] = self.get_karma(block)
                cake_day: Optional[str] = self.get_cake_day(block)
                post_and_comment_karma: Optional[List] = self.get_post_and_comment_karma(block_karma)
                if None in [karma, cake_day, post_and_comment_karma]:
                    return None

                return dict([('karma', karma), ('cake day', cake_day), ('post karma', post_and_comment_karma[0]),
                             ('comment karma', post_and_comment_karma[1])])
            else:
                logger.error('age limit')
                return None
        except Exception as _ex:
            logger.error(_ex)
        finally:
            driver.close()
            driver.quit()

    def run(self) -> NoReturn:
        """ Run the parser and show run time"""
        start_time: float = time.time()
        self.get_result()
        logger.info(f"------ {time.time() - start_time} seconds ------")


if __name__ == '__main__':
    parser = Client()
    parser.run()
