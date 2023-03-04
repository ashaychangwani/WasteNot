"""
Address class file
"""

import json
import os
from dataclasses import dataclass
from enum import Enum

import requests


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

    def __str__(self) -> str:
        """
        Serialized JSON representation of Address
        :return: JSON string
        """
        return self.serialize()

    def __get_coordinates(self) -> tuple[float, float]:
        """
        Get the coordinates of the address
        :return: Tuple of coordinates (latitude, longitude)

        Uses `https://api.mapbox.com/geocoding/v5/{endpoint}/{search_text}.json` to get the coordinates.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

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

    @staticmethod
    def load(json_str: str) -> "Address":
        """
        Deserialize the address from JSON string
        :param json_str: Address JSON string
        :return: Address object
        """
        json_dict = json.loads(json_str)
        return Address(
            street1=json_dict["street1"],
            street2=json_dict["street2"],
            city=json_dict["city"],
            state=json_dict["state"],
            zip=json_dict["zip"],
        )


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
