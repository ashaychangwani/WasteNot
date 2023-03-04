"""
Route Manager class file
"""

import os

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

    def get_route(self) -> list[(str, Address)]:
        """
        Get the optimal route the driver should take
        :return: Set of stops to make

        Uses `https://api.mapbox.com/optimized-trips/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coordinates = f"{self.start.coordinates[1]},{self.start.coordinates[0]};"
        # Add the coordinates of the stops
        for stop in self.stops.values():
            coordinates += f"{stop.coordinates[1]},{stop.coordinates[0]};"
        # Add the destination coordinates
        coordinates += f"{self.destination.coordinates[1]},{self.destination.coordinates[0]}"

        # Build the url
        url = f"https://api.mapbox.com/optimized-trips/v1/{profile}/{coordinates}?" \
              f"source=first&" \
              f"destination=last&" \
              f"roundtrip=true&" \
              f"access_token={MAPBOX_API_KEY}"

        # Make the request
        response = requests.get(url)
        # Get the json
        json = response.json()

        # Handle code
        if json["code"] != "Ok":
            raise ValueError(f"Could not calculate route. Error: {json['message']}")

        # Get the waypoints
        waypoints = json["waypoints"]

        # Get the waypoint_indices
        waypoint_indices = [wp["waypoint_index"] for wp in waypoints]

        # Get the route info by matching the indices to the stops
        # Ignore the first and last indices as they are the start and destination
        route_info = []
        for index in waypoint_indices[1:-1]:
            index -= 1
            route_info.append((list(self.stops.keys())[index], list(self.stops.values())[index]))

        return route_info


if __name__ == "__main__":
    __landmarks = {
        "Empire State Building": Address("350 5th Ave", None, "New York", "NY", 10118),
        "Central Park": Address("Central Park", None, "New York", "NY", 10024),
        "Times Square": Address("Times Square", None, "New York", "NY", 10036),
        "Brooklyn Bridge": Address("Brooklyn Bridge", None, "New York", "NY", 11201),
        "Rockefeller Center": Address("Rockefeller Center", None, "New York", "NY", 10111),
        "Grand Central Terminal": Address("Grand Central Terminal", None, "New York", "NY", 10017),
        "Metropolitan Museum of Art": Address("1000 5th Ave", None, "New York", "NY", 10028),
    }

    # Build the stops dictionary
    __stops = {}
    for name, address in list(__landmarks.items())[1:-1]:
        __stops[name] = address

    # Create a route manager
    __route_manager = RouteManager(
        __landmarks[list(__landmarks.keys())[0]],
        __landmarks[list(__landmarks.keys())[-1]],
        __stops
    )

    # Calculate the route
    print(__route_manager.get_route())
