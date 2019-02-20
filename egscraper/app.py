from flask import Flask, jsonify, request

from .CommonPleas import CommonPleas
from .MDJ import MDJ

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "all good"})


@app.route("/searchName/<str:court>", methods=["POST"])
def searchName(court):
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    dob = request.json["dob"]
    if court == "CP":
        return jsonify(CommonPleas.searchName(first_name, last_name, dob))
    elif court == "MDJ":
        return jsonify(MDJ.searchName(first_name, last_name, dob))
    else:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})


@app.route("/lookupDocket/<str:court>", methods=["POST"])
def lookupDocket(court):
    docket_number = request.json["docket_number"]
    if court == "CP":
        return jsonify(CommonPleas.lookupDocket(docket_number))
    elif court == "MDJ":
        return jsonify(MDJ.lookupDocket(docket_number))
    else:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})


@app.route("/<path:path>", methods=["GET", "POST"])
def catchall_route(path):
    return jsonify({"status": "not a valid endpoint"})
