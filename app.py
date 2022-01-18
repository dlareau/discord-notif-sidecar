import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def send_notif():
    routes = {}
    with open("routes.txt") as f:
        raw_routes = f.read().strip().split("\n")
        for route in raw_routes:
            split = route.split(",")
            if(len(split != 2)):
                print("Improperly formatted routes file.")
                continue
            # service name = discord hook
            routes[split[0]] = split[1]

    data = request.get_json(force=True)
    
    return 'ok'
