"""
This module contains the main application logic for the application.

It sets up the Flask application and defines the routes for the API.

Routes:
    - "/" (POST): Handles POST requests to the root URL by asynchronously
      getting a random status and returning it as a JSON response.

Functions:
    - simple_request(): Handles POST requests to the root URL.
"""
import random
import asyncio
from flask import Flask, jsonify
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)


ERROR_RATE = 0.1


async def random_status():
    """
    Asynchronously generates a random status with a 1 second delay. If the
    random number generated is less than the ERROR_RATE, a dictionary with
    'data' set to 'failed' and 'status' set to 503 is returned. Otherwise, a
    dictionary with 'data' set to 'success' and 'status' set to 200 is returned.

    Returns:
        dict: A dictionary with 'data' set to 'failed' or 'success' and 'status'
        set to 503 or 200 respectively.
    """
    await asyncio.sleep(1)
    if random.random() < ERROR_RATE:
        return {'data': 'failed', 'status': 503}

    return {'data': 'success', 'status': 200}


@app.route("/", methods=["POST"])
async def simple_request():
    """
    Handles POST requests to the root URL by asynchronously getting a random
    status and returning it as a JSON response.
    """
    data = await random_status()
    return jsonify(data)

asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
