from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
driver = webdriver.Firefox(
    options=options,
    log_path="/var/log/geckodriver.log")


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "all good"})


@app.route("/CP/searchName", methods=["GET", "POST"])
def searchCommonPleasName():
    return jsonify({"status": "not implemented yet"})


@app.route("/CP/lookupDocket", methods=["GET", "POST"])
def lookupCommonPleasDocket():
    return jsonify({"status": "not implemented yet"})


@app.route("/MDJ/searchName", methods=["GET", "POST"])
def searchMDJName():
    return jsonify({"status": "not implemented yet"})


@app.route("/MDJ/lookupDocket", methods=["GET", "POST"])
def lookupMDJDocket():
    return jsonify({"status": "not implemented yet"})
