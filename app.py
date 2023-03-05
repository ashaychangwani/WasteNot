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
    :return: True if successful

    Request body format
    -------------------
    {
        phone: <phone number>,
        addresses: [<serialized address object>, ...]
        destination: <serialized address object>
    }
    """
    try:
        data = json.loads(request.data.decode("utf-8"))

        phone = data["phone"]
        addresses = data["addresses"]
        destination = Address.load(data["destination"])

        # Load the addresses
        stops = {}
        for name, address in addresses.items():
            stops[name] = Address.load(address)

        # Iterate through the addresses
        count = 0
        for address in addresses:
            # Remove the address from the store
            store.remove_pickup_location(address)
            count += 1

        # Fix the start location to CEWIT
        start = Address("1500 Stony Brook Rd", "", "Stony Brook", "NY", 11790)

        # Create route planner
        route_planner = RoutePlanner(start, destination, stops)
        map_link = route_planner.get_google_maps_link(stops=route_planner.get_route())

        # Send a text message to the driver
        MessagingBot().send_message(
            f"Thank you for helping to pick up {count} food donations! "
            f"Here is the route you should take: {map_link}",
            phone,
        )

    except Exception as e:
        # Return error response
        return jsonify({"success": False, "error": str(e)})

    # Return JSON response
    return jsonify({"success": True})


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
    # Create dictionary of foodbanks
    foodbanks = store.food_banks_df[["name", "address"]].set_index("name", inplace=False).to_dict()["address"]

    # Convert to array of (name, address) tuples
    return jsonify([(name, Address.load(address)) for name, address in foodbanks.items()])


if __name__ == "__main__":
    app.run(debug=True, port=8123, host="0.0.0.0")
