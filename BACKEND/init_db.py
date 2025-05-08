import sqlite3
from gasbuddy import GasBuddy
import asyncio

#database_path = "/home/victor/gasbuddy-buddy/BACKEND/gas_station.db"
database_path = "gas_station.db"

def initialize_database():
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # Create a table for the station if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER,
                name TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')

        cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS prices (
                                id INTEGER,
                                price REAL,
                                last_updated DATETIME,
                                FOREIGN KEY (id) REFERENCES stations (id),
                                UNIQUE (last_updated, id)
                            )
                        ''')

def add_station(longitude, latitude, name):
    gasbuddy = GasBuddy()
    response = asyncio.run(gasbuddy.price_lookup_service(lat=latitude, lon=longitude, limit=1))
    id = response["results"][0]["station_id"]
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # Insert the new station into the stations table
        cursor.execute('''
            INSERT INTO stations (id, longitude, latitude, name)
            VALUES (?, ?, ?, ?)
        ''', (id, longitude, latitude, name))

if __name__ == '__main__':
    initialize_database()
    print("Database initialized.")
    cont = input("Press y to add a station or any other key to exit: ")
    # Loop to add stations
    while cont.lower() == "y":
        longitude = float(input("Enter the longitude of the station: "))
        latitude = float(input("Enter the latitude of the station: "))
        name = input("Enter the name of the station: ")
        add_station(longitude, latitude, name)
        print("Station added.")
        cont = input("Press y to add another station or any other key to exit: ")

    print("Exiting.")