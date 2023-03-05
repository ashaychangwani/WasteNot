"""
Flask Server
"""

import json

from flask import Flask, jsonify, request

from wastenot import RoutePlanner, Store
from wastenot.models import Address
from wastenot.chatbot.chatbot import ChatBot

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
    Echoes the requst body back to the client
    :return: JSON response
    """
    try:
        data = request.json
        if len(data) != 2:
            raise ValueError("Invalid format.")
        id = data["id"]
        if id not in chats:
            chats[id] = ChatBot()
        query = data["query"]
        print("query is ", query)
        response = chats[id].getResponse(query)
        return jsonify({"success": True, "prompt": str(response)})
    except Exception as e:
        # Return error response
        print(e)
        return jsonify({"success": False, "error": str(e)})
    return jsonify({"data": request.data.decode("utf-8")})


@app.route("/pickup", methods=["POST"])
def pickup() -> json:
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


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
