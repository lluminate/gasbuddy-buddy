from flask import Flask, jsonify, request
import sqlite3
from gasbuddy import GasBuddy
import asyncio

from flask_cors import CORS
app = Flask(__name__)
CORS(app)
DATABASE = "./gas_station.db"  # Adjust the path if your database is in a different location

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    return conn

def close_db(conn):
    if conn:
        conn.close()

def add_station(longitude, latitude, name):
    gasbuddy = GasBuddy()
    response = asyncio.run(gasbuddy.price_lookup_service(lat=latitude, lon=longitude, limit=1))
    id = response["results"][0]["station_id"]
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Insert the new station into the stations table
        cursor.execute('''
            INSERT INTO stations (id, longitude, latitude, name)
            VALUES (?, ?, ?, ?)
        ''', (id, longitude, latitude, name))

@app.route("/api/gas_prices")
def get_gas_prices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            prices.last_updated,
            prices.price,
            prices.id,
            stations.name AS station_name
        FROM prices
        JOIN stations ON prices.id = stations.id
        WHERE last_updated >= datetime('now', '-30 days')
    ''')
    prices = cursor.fetchall()
    cursor.execute("SELECT id, name FROM stations")
    close_db(conn)

    # Convert the list of Row objects to a list of dictionaries for JSON serialization
    price_list = [dict(row) for row in prices]
    return jsonify(price_list)

@app.route("/api/stations")
def get_stations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stations")
    stations = cursor.fetchall()
    close_db(conn)

    # Convert the list of Row objects to a list of dictionaries for JSON serialization
    station_list = [dict(row) for row in stations]
    return jsonify(station_list)

@app.route("/api/stations/add", methods=["POST"])
def new_station():
    #verify the request body
    data = request.get_json()
    if not data or "name" not in data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Invalid request"}), 400
    else:
        name = data["name"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        # Add the station to the database
        add_station(longitude, latitude, name)
        return jsonify({"message": "Station added successfully"}), 201

@app.route("/api/stations/remove", methods=["POST"])
def remove_station():
    #verify the request body
    data = request.get_json()
    if not data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400
    else:
        station_id = data["id"]
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Delete the station from the stations table
            cursor.execute('''
                DELETE FROM stations WHERE id = ?
            ''', (station_id,))
            # Delete the prices associated with the station
            cursor.execute('''
                DELETE FROM prices WHERE id = ?
            ''', (station_id,))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)