from flask import Flask
from flask_restful import Api
from .resources import EventsAPI

app = Flask(__name__)
api = Api(app)

api.add_resource(EventsAPI, "/info")

if __name__ == '__main__':
    app.run(debug=True)