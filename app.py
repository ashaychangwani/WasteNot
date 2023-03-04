"""
Flask Server
"""

import json

from flask import Flask, jsonify, request

from wastenot import RouteManager

app = Flask(__name__)


@app.route("/echo", methods=["GET"])
def echo() -> json:
    """
    Echoes the request body back to the client
    :return: JSON response
    """
    return jsonify({"data": request.data.decode("utf-8")})


@app.route("/navigate", methods=["POST"])
def navigate() -> json:
    """
    Navigates the driver to the destination
    :return: JSON response
    """
    # Create route manager using address data from request
    route_manager = RouteManager.load(request.data.decode("utf-8"))

    # Get optimal route
    route = route_manager.get_route()

    # Create response object
    response = {"route": route}

    # Return JSON response
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
