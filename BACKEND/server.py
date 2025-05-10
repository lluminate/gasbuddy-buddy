from flask import Flask, jsonify, request
import sqlite3
import requests
import re
from bs4 import BeautifulSoup

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


def get_location(station_id):
    url = f"https://www.gasbuddy.com/station/{station_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        # Find the latitude and longitude elements
        latitude_element = soup.find(string=re.compile(r'"latitude":\s*([0-9.-]+)'))
        longitude_element = soup.find(string=re.compile(r'"longitude":\s*([0-9.-]+)'))
        if latitude_element and longitude_element:
            latitude_match = re.search(r'"latitude":\s*([0-9.-]+)', latitude_element)
            longitude_match = re.search(r'"longitude":\s*([0-9.-]+)', longitude_element)
            if latitude_match and longitude_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                #print(f"Latitude: {latitude}")
                #print(f"Longitude: {longitude}")
                return latitude, longitude
        else:
            print("Location not found")

def get_station_name(station_id):
    url = f"https://www.gasbuddy.com/station/{station_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    # Find the title
    title_element = soup.find("title")
    if title_element:
        title = title_element.get_text()
        # Extract the station name from the title
        station_name = re.search(r'^(.*?)\s+-\s*GasBuddy', title)
        if station_name:
            #print(f"Station Name: {station_name.group(1)}")
            return station_name.group(1)
        else:
            print("Station name not found")
    else:
        print("Title not found")

def add_station(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Insert the new station into the stations table
        cursor.execute('''
            INSERT INTO stations (id, latitude, longitude, name)
            VALUES (?, ?, ?, ?)
        ''', (id, get_location(id)[0], get_location(id)[1], get_station_name(id)))

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
async def new_station():
    #verify the request body
    data = request.get_json()
    print(data)
    if not data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400
    else:
        station_id = data["id"]
        # Add the station to the database
        add_station(station_id)
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

        return jsonify({"message": "Station removed successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)