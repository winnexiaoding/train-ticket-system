from flask import Flask
from flask_session import Session
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Session(app)

    from routes import auth, home, stopover, station, user, train, price, schedule, ticket, statistics
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(stopover.bp)
    app.register_blueprint(station.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(train.bp)
    app.register_blueprint(price.bp)
    app.register_blueprint(schedule.bp)
    app.register_blueprint(ticket.bp)
    app.register_blueprint(statistics.bp)

    return app
