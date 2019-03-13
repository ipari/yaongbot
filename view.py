from flask import Blueprint

viewer = Blueprint('blueprint', __name__)


@viewer.route("/")
def main():
    return "Main"


@viewer.route("/hi/")
def hi():
    return "Hi, there."
