"""
User class file
"""

from .address import Address


class User:
    """
    User Class
    """

    def __init__(self, name: str, address: Address):
        """
        Constructor
        :param name: User's name
        :param address: User's address
        """

        self.name: str = name
        self.address: Address = address
