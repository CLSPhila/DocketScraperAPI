from flask import Flask, jsonify, request
from .CommonPleas import CommonPleas
from .MDJ import MDJ
from .SearchBot import SearchBot
from .helpers import cp_or_mdj
import os
import logging


app = Flask(__name__)
if os.getenv("GUNICORN_LOGGER"):
    gunicorn_logger = logging.getLogger('gunicorn.info')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
def index():
    app.logger.info("logging a call to /")
    return jsonify({"status": "all good"})


@app.route("/searchName/<court>", methods=["POST"])
def searchName(court):
    try:
        first_name = request.json["first_name"]
        last_name = request.json["last_name"]
    except KeyError:
        app.logger.error("Request to searchName missing parameter")
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    dob = request.json.get("dob")
    if court == "CP":
        return jsonify(CommonPleas.searchName(first_name, last_name, dob))
    elif court == "MDJ":
        return jsonify(MDJ.searchName(first_name, last_name, dob))
    else:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})


@app.route("/lookupDocket/<court>", methods=["POST"])
def lookupDocket(court):
    try:
        docket_number = request.json["docket_number"]
    except KeyError:
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    searchbot = SearchBot()
    if court in ["CP", "MDJ"]:
        return jsonify(searchbot.lookup_docket(docket_number, court))
    else:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})


@app.route("/lookupMultipleDockets", methods=["POST"])
def lookupMany():
    """ Route for looking up many docket numbers."""
    try:
        docket_numbers = request.json["docket_numbers"]
    except KeyError:
        return jsonify(
            {"status": "Error. Missing docket_numbers parameter."}
        )
    searchbot = SearchBot()
    results = searchbot.lookup_multiple_dockets(docket_numbers)
    return jsonify({"status": "success", "dockets": results})


@app.route("/<path:path>", methods=["GET", "POST"])
def catchall_route(path):
    app.logger.info("call to an invalid path")
    return jsonify({"status": "not a valid endpoint"})
