import datetime
import logging
import uuid
"""The module contains an inherited class for retrieving data"""
format = '%(asctime)s %(lineno)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)
logger = logging.getLogger('reddit')


class BaseSelector:
    """Create methods to retrieve data"""

    def get_unique_id(self):
        """Generate and return a unique id"""
        return str(uuid.uuid1().hex)

    def get_post_url(self, block) -> str or None:
        """Get and return post url"""
        block_url = block.select_one('a.SQnoC3ObvgnGjWt90zD9Z')
        if not block_url:
            logger.error('no block url')
            return
        url = 'https://reddit.com' + block_url.get('href')
        if not url:
            logger.error('no elements')
            return
        return url

    def get_user_name(self, block) -> str or None:
        """Get and return user name"""
        user_name = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if user_name == '[deleted]' or not user_name:
            logger.error('no user name')
            return
        logger.info(user_name.text)
        return user_name.text[2:]

    def get_user_url(self, block) -> str or None:
        """Get and return user url"""
        user_url = block.select_one('a._2tbHP6ZydRpjI44J3syuqC')
        if not user_url:
            logger.error('no user url')
            return
        return 'https://reddit.com' + user_url.get('href')

    def get_post_date(self, block) -> str or None:
        """Get and return post date"""
        day_ago = block.select_one('a._3jOxDPIQ0KaOWpzvSQo-1s')
        if not day_ago:
            logger.error('no post date')
            return
        return datetime.date.today() - datetime.timedelta(days=int(day_ago.text.split()[0]))

    def get_count_comments(self, block) -> str or None:
        """Get and return count comments"""
        count_comments = block.find('span', class_='FHCV02u6Cp2zYL0fhQPsO')
        if not count_comments:
            logger.error('no comments')
            return
        return count_comments.text

    def get_count_of_votes(self, block) -> str or None:
        """Get and return count of votes"""
        count_of_votes = block.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO')
        if not count_of_votes:
            logger.error('no votes')
            return
        return count_of_votes.text

    def get_post_category(self, block) -> str or None:
        """Get and return post category"""
        post_category = block.select_one('a._3ryJoIoycVkA88fy40qNJc')
        if not post_category:
            logger.error('no category')
            return
        return post_category.get('href')[3:-1]

    def get_karma(self, block) -> str or None:
        """Get and return user karma"""
        karma = block.select_one('span._1hNyZSklmcC7R_IfCUcXmZ')
        if not karma:
            logger.error('no karma')
            return
        return karma.text

    def get_cake_day(self, block) -> str or None:
        """Get and return user cake day"""
        cake_day = block.select_one('span#profile--id-card--highlight-tooltip--cakeday')
        if not cake_day:
            logger.error('no cake_day')
            return
        return cake_day.text

    def get_post_and_comment_karma(self, block_karma) -> str or None:
        """Get and return user post karma and user comment karma"""
        if not block_karma:
            logger.error('no post and comment carma')
            return
        return [block_karma.text.split()[0], block_karma.text.split()[3]]
