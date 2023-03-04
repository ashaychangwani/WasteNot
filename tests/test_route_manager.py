"""
Test RouteManager
"""

from wastenot import RouteManager
from wastenot.models import Address

if __name__ == "__main__":
    landmarks = {
        "Central Park": Address("Central Park", None, "New York", "NY", 10024),
        "Empire State Building": Address("350 5th Ave", None, "New York", "NY", 10118),
        "Times Square": Address("Times Square", None, "New York", "NY", 10036),
        "Rockefeller Center": Address("Rockefeller Center", None, "New York", "NY", 10111),
        "Grand Central Terminal": Address("Grand Central Terminal", None, "New York", "NY", 10017),
        "Metropolitan Museum of Art": Address("1000 5th Ave", None, "New York", "NY", 10028),
        "Brooklyn Bridge": Address("Brooklyn Bridge", None, "New York", "NY", 11201),
    }

    # Build the stops dictionary
    stops = {}
    for name, address in list(landmarks.items())[1:-1]:
        stops[name] = address

    # Create a route manager
    route_manager = RouteManager(
        landmarks[list(landmarks.keys())[0]],
        landmarks[list(landmarks.keys())[-1]],
        stops
    )

    # Calculate the route
    print(route_manager.get_route())
