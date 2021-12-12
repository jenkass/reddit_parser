"""The module contains a mixin for retrieving data"""

import datetime
import logging
import uuid
from typing import List, Optional

from bs4 import Tag

DOMEN: str = 'https://reddit.com'  # reddit domain

format_log: str = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format_log, level=logging.DEBUG)
logger: logging.Logger = logging.getLogger('reddit')


class SelectorMixin:
    """Create methods to retrieve data"""

    @staticmethod
    def get_unique_id() -> str:
        """Generate a unique id

        :return: unique id
        """
        return str(uuid.uuid1().hex)

    @staticmethod
    def get_post_url(block: Tag) -> Optional[str]:
        """Get post url

        :param block: all the markup of one post
        :return: post url or None
        """
        block_url: Tag = block.select_one('a.SQnoC3ObvgnGjWt90zD9Z')
        if not block_url:
            logger.error('no block url')
            return None
        url: str = DOMEN + block_url.get('href')
        if not url:
            logger.error('no elements')
            return None
        return url

    @staticmethod
    def get_user_name(block: Tag) -> Optional[str]:
        """Get user name

        :param block: all the markup of one post
        :return: user name url or None
        """
        user_name: Tag = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if user_name == '[deleted]' or not user_name:
            logger.error('no user name')
            return None
        logger.info(user_name.text)
        return user_name.text[2:]

    @staticmethod
    def get_user_url(block: Tag) -> Optional[str]:
        """Get user url

        :param block: all the markup of one post
        :return: user url url or None
        """
        user_url: Tag = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if not user_url:
            logger.error('no user url')
            return None
        return DOMEN + user_url.get('href')

    @staticmethod
    def get_post_date(block: Tag) -> Optional[str]:
        """Get post date

        :param block: all the markup of one post
        :return: post date or None
        """
        day_ago: Tag = block.select_one('a._3jOxDPIQ0KaOWpzvSQo-1s')
        if not day_ago:
            logger.error('no post date')
            return None
        return str(datetime.date.today() - datetime.timedelta(days=int(day_ago.text.split()[0])))

    @staticmethod
    def get_count_comments(block: Tag) -> Optional[str]:
        """Get count comments

        :param block: all the markup of one post
        :return: count comments or None
        """
        count_comments: Tag = block.find('span', class_='FHCV02u6Cp2zYL0fhQPsO')
        if not count_comments:
            logger.error('no comments')
            return None
        return count_comments.text

    @staticmethod
    def get_count_of_votes(block: Tag) -> Optional[str]:
        """Get count of votes

        :param block: all the markup of one post
        :return: count of votes or None
        """
        count_of_votes: Tag = block.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO')
        if not count_of_votes:
            logger.error('no votes')
            return None
        return count_of_votes.text

    @staticmethod
    def get_post_category(block: Tag) -> Optional[str]:
        """Get post category

        :param block: all the markup of one post
        :return: post category or None
        """
        post_category: Tag = block.select_one('a._3ryJoIoycVkA88fy40qNJc')
        if not post_category:
            logger.error('no category')
            return None
        return post_category.get('href')[3:-1]

    @staticmethod
    def get_karma(block: Tag) -> Optional[str]:
        """Get user karma

        :param block: user page layout
        :return: user karma or None
        """
        karma: Tag = block.select_one('span._1hNyZSklmcC7R_IfCUcXmZ')
        if not karma:
            logger.error('no karma')
            return None
        return karma.text

    @staticmethod
    def get_cake_day(block: Tag) -> Optional[str]:
        """Get user cake day

        :param block: user page layout
        :return: user cake day or None
        """
        cake_day: Tag = block.select_one('span#profile--id-card--highlight-tooltip--cakeday')
        if not cake_day:
            logger.error('no cake_day')
            return None
        return cake_day.text

    @staticmethod
    def get_post_and_comment_karma(block_karma: Tag) -> Optional[List]:
        """Get user post karma and user comment karma

        :param block_karma: user page layout
        :return: list containing post and comment karma or None
        """
        if not block_karma:
            logger.error('no post and comment carma')
            return None
        return [block_karma.text.split()[0], block_karma.text.split()[3]]
