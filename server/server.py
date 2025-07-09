from flask import Flask, render_template, jsonify
from threading import Thread, Lock
from database.dbmgr import DBInterface


class Server(Thread):
    def __init__(self, database_ctl):
        self.app = Flask(__name__)
        self.setup_routes()
        self.database = database_ctl

    def setup_routes(self):
        @self.app.route("/")
        def map_view():
            return render_template("map.html")

        @self.app.route("/get_data")
        def get_data():
            return jsonify({})

    def run(self):
        self.app.run(host="0.0.0.0", port=5000, debug=True)

    def stop(self):
        self.join()
