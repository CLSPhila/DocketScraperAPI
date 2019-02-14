from flask import Flask, jsonify, request

from .CommonPleas import CommonPleas




app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "all good"})


@app.route("/CP/searchName", methods=["POST"])
def searchCommonPleasName():
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    dob = request.json["dob"]
    return jsonify(CommonPleas.searchName(first_name, last_name, dob))


@app.route("/CP/lookupDocket", methods=["POST"])
def lookupCommonPleasDocket():
    return jsonify({"status": "not implemented yet"})


@app.route("/MDJ/searchName", methods=["POST"])
def searchMDJName():
    return jsonify({"status": "not implemented yet"})


@app.route("/MDJ/lookupDocket", methods=["POST"])
def lookupMDJDocket():
    return jsonify({"status": "not implemented yet"})


@app.route("/<path:path>", methods=["GET", "POST"])
def catchall_route(path):
    return jsonify({"status": "not a valid endpoint"})
