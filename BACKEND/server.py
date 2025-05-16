from flask import Flask, jsonify, request
import sqlite3
from update import update_db
from parse_gasbuddy import get_location, get_station_name

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATABASE = "./gas_station.db"  # Adjust the path if your database is in a different location


@app.route("/api/gas_prices")
def get_gas_prices():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT prices.last_updated,
                              prices.price,
                              prices.id,
                              stations.name AS station_name
                       FROM prices
                                JOIN stations ON prices.id = stations.id
                       WHERE last_updated >= datetime('now', '-30 days')
                       ''')
        prices = cursor.fetchall()
        cursor.execute("SELECT id, name FROM stations")
    # Convert the list of Row objects to a list of dictionaries for JSON serialization
    price_list = [dict(row) for row in prices]
    return jsonify(price_list)


@app.route("/api/stations")
def get_stations():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stations")
        stations = cursor.fetchall()
    # Convert the list of Row objects to a list of dictionaries for JSON serialization
    station_list = [dict(row) for row in stations]
    return jsonify(station_list)


@app.route("/api/stations/add", methods=["POST"])
def new_station():
    # verify the request body
    data = request.get_json()
    print(data)
    if not data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400
    else:
        station_id = data["id"]
        # Add the station to the database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Insert the new station into the station table
            cursor.execute('''
                           INSERT INTO stations (id, latitude, longitude, name)
                           VALUES (?, ?, ?, ?)
                           ''', (station_id, get_location(station_id)[0], get_location(station_id)[1],
                                 get_station_name(station_id)))
        update_db()
        return jsonify({"message": "Station added successfully"}), 201


@app.route("/api/stations/remove", methods=["POST"])
def remove_station():
    # verify the request body
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400
    else:
        station_id = data["id"]
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Delete the station from the station table
            cursor.execute('''
                           DELETE
                           FROM stations
                           WHERE id = ?
                           ''', (station_id,))
            # Delete the prices associated with the station
            cursor.execute('''
                           DELETE
                           FROM prices
                           WHERE id = ?
                           ''', (station_id,))
        return jsonify({"message": "Station removed successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
