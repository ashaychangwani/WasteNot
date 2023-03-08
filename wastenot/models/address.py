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
    zip: str

    def __post_init__(self):
        """
        Post init method to validate the inputs
        """
        # Set street2 to "" if it is None or float
        if self.street2 is None or isinstance(self.street2, float):
            self.street2 = ""

        # Check if the inputs are valid
        for field in ["street1", "city", "state", "zip"]:
            if not getattr(self, field):
                raise ValueError(f"{field} cannot be empty.")

        # Set the state enum and validate it
        self.state = State.set_enum(self.state).name

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

    NJ = "NEW JERSEY"
    NY = "NEW YORK"

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
        return (state.upper() in State.__members__) or (state.upper() in State.__members__.values())

    @staticmethod
    def set_enum(state: str) -> "State":
        """
        Convert String to Enum
        :param state: State to convert
        :return: State Enum
        """
        # Match the input enum value to the enum
        for enum in State:
            if state.upper() == enum.name or state.upper() == enum.value:
                return enum
        return State.NY
