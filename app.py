"""
Flask Server
"""

import json

from flask import Flask, jsonify, request

from wastenot import RoutePlanner, Store
from wastenot.chatbot.chatbot import ChatBot
from wastenot.messaging import MessagingBot
from wastenot.models import Address

store = Store()
app = Flask(__name__)

chats = dict()


@app.route("/echo", methods=["GET"])
def echo() -> json:
    """
    Echoes the request body back to the client
    :return: JSON response
    """
    return jsonify({"data": request.data.decode("utf-8")})


@app.route("/chat", methods=["POST"])
def chat() -> json:
    """
    Echoes the request body back to the client
    :return: JSON response
    """
    try:
        data = request.json
        if len(data) != 2:
            raise ValueError("Invalid format.")
        data_id = data["id"]
        if data_id not in chats:
            chats[data_id] = ChatBot()

        query = data["query"]
        print(f"From: {data_id}. Query: {query}")

        response = chats[data_id].get_response(query)
        print(f"To: {data_id}. Response: {response}")

        return jsonify({"success": True, "prompt": str(response)})
    except Exception as e:
        # Return error response
        print(e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/order-pickup", methods=["POST"])
def order_pickup() -> json:
    """
    Place an order to pick up at the address
    :return: True if successful
    """
    try:
        # Read the address details from the request
        data = json.loads(request.data.decode("utf-8"))

        # Validate format {<name string>: <serialized address object>}
        if len(data) != 1:
            raise ValueError("Invalid format.")

        # Get the name and address
        name = list(data.keys())[0]
        address = Address.load(data[name])

        # Add the address to the store
        store.add_pickup_location(name, address)
    except Exception as e:
        # Return error response
        return jsonify({"success": False, "error": str(e)})

    # Return JSON response
    return jsonify({"success": True})


@app.route("/driver-pickup", methods=["POST"])
def driver_pickup() -> json:
    """
    Driver accepts to pick up at a list of addresses
    :return: JSON response

    Request body format
    -------------------
    {
        phone: <phone number>,
        destination: <serialized address object>,
        time: <time available in minutes>
    }
    """
    data = json.loads(request.data.decode("utf-8"))

    phone = data["phone"]
    destination = store.get_food_bank(data["destination"])
    time = int(data["time"])

    # Get the pickup locations addresses
    pickup_locations = {}
    for name, address in store.pickup_locations.items():
        pickup_locations[name] = address

    # Fix the start location to Lincoln Medical Center
    start = Address("234 E 149th St", "", "The Bronx", "NY", 10451)

    route_planner = RoutePlanner(start, destination, pickup_locations)

    # Get the stops
    addresses = route_planner.get_stops(time)

    # Iterate through the addresses and remove them from the store
    count = 0
    for name, _ in addresses:
        store.remove_pickup_location(name)
        count += 1

    # Create route planner
    map_link = route_planner.get_google_maps_link(stops=addresses)

    # Send a text message to the driver
    MessagingBot().send_message(
        f"Thank you for helping to pick up {count} food donations! "
        f"Here is the route you should take: {map_link}",
        phone,
    )

    # Return JSON response
    return jsonify({"success": True})


@app.route("/driver-query", methods=["POST"])
def driver_query() -> json:
    """
    Check how many stops can be made in a given time frame
    :return: JSON response

    Request body format
    -------------------
    {
        destination: <serialized address object>,
        time: <time available in minutes>
    }
    """

    data = json.loads(request.data.decode("utf-8"))

    destination = store.get_food_bank(data["destination"])
    time = data["time"]

    # Get the pickup locations addresses
    pickup_locations = {}
    for name, address in store.pickup_locations.items():
        pickup_locations[name] = address

    # Fix the start location to Lincoln Medical Center
    start = Address("234 E 149th St", "", "The Bronx", "NY", 10451)

    route_planner = RoutePlanner(start, destination, pickup_locations)

    # Get the stops
    addresses = route_planner.get_stops(time)

    # Compare the number of stops to the database
    for name, address in addresses:
        if name not in store.pickup_locations:
            addresses.remove((name, address))

    # Return JSON response
    return jsonify({"stops": addresses})


@app.route("/navigate", methods=["POST"])
def navigate() -> json:
    """
    Navigates the driver to the destination
    :return: JSON response
    """
    # Create route planner using address data from request
    route_planner = RoutePlanner.load(request.data.decode("utf-8"))

    # Get optimal route
    route = route_planner.get_route()

    # Create response object
    response = {"route": route}

    # Return JSON response
    return jsonify(response)


@app.route("/foodbanks", methods=["GET"])
def get_foodbanks() -> json:
    """
    Get a list of foodbanks
    :return: JSON response
    """
    # Create a list of foodbanks: [(name, (street, city, state, zip))]
    foodbanks = []

    for _, foodbank in store.food_banks_df.iterrows():
        foodbanks.append(
            {
                "text": " ".join(
                    [foodbank["name"], foodbank["street1"], foodbank["city"]]
                ),
                "name": foodbank["name"],
            }
        )

    return jsonify(foodbanks)


if __name__ == "__main__":
    app.run(debug=True, port=8123, host="0.0.0.0")
