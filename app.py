import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/echo", methods=["GET"])
def echo() -> json:
    """
    Echoes the request body back to the client
    :return: JSON response
    """
    return jsonify({"data": request.data.decode("utf-8")})


if __name__ == '__main__':
    app.run(debug=True)
