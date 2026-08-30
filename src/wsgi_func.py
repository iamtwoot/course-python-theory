import json
from wsgiref.simple_server import make_server

import requests


def app(environ, start_response):
    url = "https://api.exchangerate-api.com/v4/latest"
    currency = str(environ["PATH_INFO"]).strip("/")

    try:
        response = requests.get(f"{url}/{currency}")
        response.raise_for_status()
        response_body = json.dumps(response.json()).encode("utf-8")
        status = "200 OK"
    except requests.exceptions.RequestException:
        response_body = json.dumps(
            {"error": "Invalid currency or upstream error"}
        ).encode("utf-8")
        status = "404 NOT FOUND"

    start_response(status, [("Content-Type", "application/json")])
    return [response_body]


if __name__ == "__main__":
    with make_server("", 8000, app) as server:
        print("Serving on port 8000...")
        server.serve_forever()
