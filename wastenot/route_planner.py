"""
Route Planner class file
"""

import json
import os
import urllib.parse

import requests

from .models import Address


class RoutePlanner:
    """
    Route Planner
    """

    def __init__(self, start: Address, destination: Address, stops: dict[str, Address]):
        """
        Constructor
        :param start: Starting address
        :param destination: Destination address
        :param stops: Dictionary of stops to make (waypoints)
        """

        self.start: Address = start
        self.destination: Address = destination
        self.stops: dict[str, Address] = stops

    @staticmethod
    def load(json_str: str) -> "RoutePlanner":
        """
        Deserialize the route planner from JSON string
        :param json_str: RoutePlanner JSON string
        :return: RoutePlanner object
        """
        address_dict = json.loads(json_str)

        # Get address names
        address_names = [name for name in address_dict]

        # Get the start address
        start = Address.load(address_dict[address_names[0]])
        destination = Address.load(address_dict[address_names[-1]])

        # Get the stops
        stops = {}
        for stop in address_names[1:-1]:
            stops[stop] = Address.load(address_dict[stop])

        return RoutePlanner(start, destination, stops)

    def get_stops(self) -> dict[str, Address]:
        """
        Get the stops to make
        :return: Dictionary of stops

        Uses `https://api.mapbox.com/directions-matrix/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coords = self.build_coordinates_string(self.start, self.stops, self.destination)

        # Build the url
        url = (
            f"https://api.mapbox.com/directions-matrix/v1/{profile}/{coords}?"
            f"sources=all&"
            f"destinations=all&"
            f"access_token={MAPBOX_API_KEY}"
        )

        # Make the request and get the json response
        response = requests.get(url).json()

        # Handle code
        if response["code"] != "Ok":
            raise ValueError(f"Could not get route matrix. Error: {response['message']}")

        # Get the durations
        durations = response["durations"]
        # TODO: implement logic to get the stops

        return self.stops

    def get_route(self) -> list[(str, Address)]:
        """
        Get the optimal route the driver should take
        :return: Set of stops to make

        Uses `https://api.mapbox.com/optimized-trips/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coords = self.build_coordinates_string(self.start, self.stops, self.destination)

        # Build the url
        url = (
            f"https://api.mapbox.com/optimized-trips/v1/{profile}/{coords}?"
            f"source=first&"
            f"destination=last&"
            f"roundtrip=false&"
            f"access_token={MAPBOX_API_KEY}"
        )

        # Make the request and get the json response
        response = requests.get(url).json()

        # Handle code
        if response["code"] != "Ok":
            raise ValueError(f"Could not calculate route. Error: {response['message']}")

        # Get the waypoints
        waypoints = response["waypoints"]

        # Get the waypoint_indices
        waypoint_indices = [wp["waypoint_index"] for wp in waypoints]

        # Get the route info by matching the indices to the stops
        # Ignore the first and last indices as they are the start and destination
        route_info = []
        for wp_i in waypoint_indices[1:-1]:
            wp_i -= 1
            route_info.append(
                (list(self.stops.keys())[wp_i], list(self.stops.values())[wp_i])
            )

        return route_info

    def get_google_maps_link(self) -> str:
        """
        Get the Google Maps link for the route with waypoints
        :return: Google Maps link
        """
        route = self.get_route()

        # Build the url
        url = "https://www.google.com/maps/dir/"

        # Add the start and destination to include in the route
        route = [("start", self.start)] + route + [("destination", self.destination)]

        for _, address in route:
            url += f"{urllib.parse.urlencode({'st1': address.street1.replace(' ', '+')}, safe='+')[4:]},"
            if address.street2:
                url += f"+{urllib.parse.urlencode({'st2': address.street2.replace(' ', '+')}, safe='+')[4:]},"
            url += f"+{urllib.parse.urlencode({'cty': address.city.replace(' ', '+')}, safe='+')[4:]},"
            url += f"+{urllib.parse.urlencode({'stt': address.state})[4:]}"
            url += f"+{urllib.parse.urlencode({'zip': address.zip})[4:]}"
            url += "/"

        return url

    @staticmethod
    def build_coordinates_string(
            start: Address | None,
            stops: dict[str, Address],
            destination: Address | None
    ) -> str:
        """
        Build the coordinates string for the route
        :param start: Starting address
        :param stops: List of stops to make
        :param destination: Destination address
        :return: Coordinates string
        """

        coords = ""

        if start:
            coords += f"{start.coordinates[1]},{start.coordinates[0]};"

        for _, stop in stops.items():
            coords += f"{stop.coordinates[1]},{stop.coordinates[0]};"

        if destination:
            coords += f"{destination.coordinates[1]},{destination.coordinates[0]}"

        return coords
