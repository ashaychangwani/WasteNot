"""
Route Planner class file
"""

import heapq
import json
import os
import urllib.parse

import requests

from wastenot.store import Store
from .models import Address

store = Store()


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

    def get_stops(self, time: int = 30) -> (list[(str, Address)], float):
        """
        Get the stops to make
        :param time: Time to make the stops in minutes
        :return: Dictionary of stops

        Uses `https://api.mapbox.com/directions-matrix/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coords, weights = self.build_coordinates_string(
            self.start, self.stops, self.destination
        )

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
            raise ValueError(
                f"Could not get route matrix. Error: {response['message']}"
            )

        # Get the durations
        durations = response["durations"]
        route_i, durations, total_weight = self.find_optimal_route(
            durations, time * 60, weights
        )

        # Handle no route found
        if route_i is None:
            return [], 0

        # Get the stops
        stops = []
        stops_names = list(self.stops.keys())
        for stop_i in route_i[1:-1]:
            stop_name = stops_names[stop_i - 1]
            stops.append((stop_name, self.stops[stop_name]))

        return stops, total_weight

    @staticmethod
    def find_optimal_route(
        durations: list[list[float]], time_limit: float, weights=None
    ):
        """
        Find the optimal route to take
        :param durations: Durations matrix of the possible routes
        :param time_limit: Time limit to get to the destination
        :param weights: Profits matrix of the possible routes
        :return: Tuple of the best profit, best route, and best distance
        """
        for d in durations:
            print(d)
        n: int = len(durations)
        source: int = 0
        destination: int = n - 1

        # Set the weights to 1 if not provided.
        # Set the source and destination weights to 0.
        if weights is None:
            weights = [1 for _ in range(n)]
            weights[source] = 0
            weights[destination] = 0

        best_solution = None
        best_profit = 0
        best_route = None
        best_distance = 0

        priority_queue = [(0, 0, source, {source}, [source])]

        while priority_queue:
            distance, profit, node, visited, route = heapq.heappop(priority_queue)

            if (node == destination and distance <= time_limit) and (
                profit > best_profit
                or (profit == best_profit and distance < best_distance)
            ):
                best_profit = profit
                best_solution = visited
                best_route = route
                best_distance = distance

            for child_node in range(n):
                if child_node not in visited and child_node != source:
                    child_distance = distance + durations[node][child_node]
                    child_profit = profit + weights[child_node]
                    if child_distance <= time_limit and child_profit > best_profit:
                        child_route = route.copy()
                        child_route.append(child_node)
                        heapq.heappush(
                            priority_queue,
                            (
                                child_distance,
                                child_profit,
                                child_node,
                                visited | {child_node},
                                child_route,
                            ),
                        )

        return best_route, best_distance, best_profit

    def get_route(self) -> list[(str, Address)]:
        """
        Get the optimal route the driver should take
        :return: Set of stops to make

        Uses `https://api.mapbox.com/optimized-trips/v1/{profile}/{coordinates}` api to calculate the route.
        """
        MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

        profile = "mapbox/driving-traffic"

        # Build the coordinates string
        coords, _ = self.build_coordinates_string(
            self.start, self.stops, self.destination
        )

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

    def get_google_maps_link(self, stops: list[(str, Address)] | None = None) -> str:
        """
        Get the Google Maps link for the route with waypoints
        :param stops: List of stops to include in the route
        :return: Google Maps link
        """
        # Get stops if not provided
        if stops is None:
            stops, total_weight = self.get_stops()

        # Build the url
        url = "https://www.google.com/maps/dir/"

        # Add the start and destination to include in the route
        if stops:
            route = (
                [("start", self.start)] + stops + [("destination", self.destination)]
            )
        else:
            route = [("start", self.start), ("destination", self.destination)]

        for _, address in route:
            url += f"{urllib.parse.urlencode({'st1': address.street1.replace(' ', '+')}, safe='+')[4:]},"
            if address.street2:
                url += f"+{urllib.parse.urlencode({'st2': address.street2.replace(' ', '+')}, safe='+')[4:]},"
            url += f"+{urllib.parse.urlencode({'cty': address.city.replace(' ', '+')}, safe='+')[4:]},"
            url += f"+{urllib.parse.urlencode({'stt': address.state})[4:]}"
            url += f"+{urllib.parse.urlencode({'zip': address.zip})[4:]}"
            url += "/"

        # Shorten the url
        s_url = requests.get(
            f"https://www.google.com/maps/rpc/shorturl?authuser=0&hl=en&gl=us&pb=!1s{url}"
        ).content
        # Get the url encloses between double quotes
        url = s_url[s_url.find(b'"') + 1 : s_url.rfind(b'"')].decode("utf-8")

        return url

    @staticmethod
    def build_coordinates_string(
        start: Address | None, stops: dict[str, Address], destination: Address | None
    ) -> (str, list[float]):
        """
        Build the coordinates string for the route
        :param start: Starting address
        :param stops: List of stops to make
        :param destination: Destination address
        :return: Coordinates string and list of weights
        """

        coords = ""
        weights = []

        if start:
            coords += f"{start.coordinates[1]},{start.coordinates[0]};"
            weights.append(0)

        for name, address in stops.items():
            coords += f"{address.coordinates[1]},{address.coordinates[0]};"
            print(store.pickup_locations_df)
            print(store.pickup_locations_df[store.pickup_locations_df["name"] == name][
                      "weight"
                  ])
            weights.append(
                store.pickup_locations_df[store.pickup_locations_df["name"] == name][
                    "weight"
                ].values[0]
            )

        if destination:
            coords += f"{destination.coordinates[1]},{destination.coordinates[0]}"
            weights.append(0)

        return coords, weights
