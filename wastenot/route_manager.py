"""
Route Manager class file
"""

import json
import os
import urllib.parse

import requests

from .models import Address


class RouteManager:
    """
    Route Manager
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
    def load(json_str: str) -> "RouteManager":
        """
        Deserialize the route manager from JSON string
        :param json_str: Route Manager JSON string
        :return: Route Manager object
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

        return RouteManager(start, destination, stops)

    def get_route(self) -> list[(str, Address)]:
        """
        Get the optimal route the driver should take
        :return: Set of stops to make

        Uses `https://api.mapbox.com/optimized-trips/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coords = f"{self.start.coordinates[1]},{self.start.coordinates[0]};"
        # Add the coordinates of the stops
        for stop in self.stops.values():
            coords += f"{stop.coordinates[1]},{stop.coordinates[0]};"
        # Add the destination coordinates
        coords += f"{self.destination.coordinates[1]},{self.destination.coordinates[0]}"

        # Build the url
        url = (
            f"https://api.mapbox.com/optimized-trips/v1/{profile}/{coords}?"
            f"source=first&"
            f"destination=last&"
            f"roundtrip=true&"
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
