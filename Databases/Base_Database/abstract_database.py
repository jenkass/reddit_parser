"""The module contains a basic abstract class for databases"""


class Database:
    """Create a class for working with the database

    The class contains methods that allow you to read, write,
    update or delete data in database.
    """

    def insert_data(self, *args, **kwargs):
        """Add data to database"""
        pass

    def get_data(self, *args, **kwargs):
        """Get all data from database"""
        pass

    def put_data(self, *args, **kwargs):
        """Update data in database"""
        pass

    def delete_data(self, *args, **kwargs):
        """Remove data from database"""
        pass
