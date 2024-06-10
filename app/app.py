from flask import Flask
from flask_restful import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .resources import EventsAPI


app = Flask(__name__)
api = Api(app)

# Initialize the Limiter to restrict the number of requests from one user
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "15 per hour"]
)

api.add_resource(EventsAPI, "/info")

if __name__ == '__main__':
    app.run(debug=True)