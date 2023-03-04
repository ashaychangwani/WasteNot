"""
Address class file
"""

from dataclasses import dataclass

from enum import Enum


@dataclass
class Address:
    """
    Address Class
    """

    street1: str
    street2: str
    city: str
    state: str
    zip: int

    def __post_init__(self):
        """
        Post init method to validate the inputs
        """
        # Check if the inputs are valid
        for field in ["street1", "city", "state", "zip"]:
            if not getattr(self, field):
                raise ValueError(f"{field} cannot be empty.")

        # Check if the state is valid
        if not State.isValid(self.state):
            raise ValueError(f"{self.state} is not a valid state.")

    def __str__(self):
        """
        String representation of Address
        :return: String representation of Address
        """
        return f"{self.street1}{', ' + self.street2 if self.street2 else ''}, {self.city}, {self.state} {self.zip}."


class State(Enum):
    """
    Supported States
    """
    NY = "New York"

    def __str__(self) -> str:
        """
        String representation of State
        :return: String representation of State
        """
        return self.name

    @staticmethod
    def isValid(state: str) -> bool:
        """
        Checks if the state is valid
        :param state: State to check
        :return: True if valid, False otherwise
        """
        return state in State.__members__
