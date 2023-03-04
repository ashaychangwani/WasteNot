"""
Address class file
"""

import json
from dataclasses import dataclass
from enum import Enum

import requests

from secrets import MAPBOX_API_KEY


@dataclass
class Address:
    """
    Address Class
    """

    street1: str
    street2: str | None
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

        # Get the coordinates
        self.coordinates = self.__get_coordinates()

    def __str__(self):
        """
        String representation of Address
        :return: String representation of Address
        """
        return f"{self.street1}{', ' + self.street2 if self.street2 else ''}, {self.city}, {self.state} {self.zip}."

    def __get_coordinates(self) -> tuple[float, float]:
        """
        Get the coordinates of the address
        :return: Tuple of coordinates (latitude, longitude)

        Uses `https://api.mapbox.com/geocoding/v5/{endpoint}/{search_text}.json` to get the coordinates.
        """
        endpoint = "mapbox.places"
        search_text = f"{self.street1}, {self.city}, {self.state} {self.zip}"
        url = f"https://api.mapbox.com/geocoding/v5/{endpoint}/{search_text}.json?access_token={MAPBOX_API_KEY}"

        # Make the request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            raise ValueError(f"Could not get coordinates for {self}.")

        # Get the coordinates
        coordinates = response.json()["features"][0]["center"]
        return coordinates[1], coordinates[0]

    def serialize(self) -> str:
        """
        Serializes the address
        :return: JSON string
        """
        return json.dumps(self.__dict__)

    def deserialize(self, json_str: str) -> None:
        """
        Deserializes the address
        :param json_str: JSON string
        """
        self.__dict__ = json.loads(json_str)


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
