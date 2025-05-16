import sqlite3
from parse_gasbuddy import get_station_name, get_location

# database_path = "/home/victor/gasbuddy-buddy/BACKEND/gas_station.db"
database_path = "gas_station.db"


def initialize_database():
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # Create a table for the station if it doesn't exist
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS stations
                       (
                           id        INTEGER,
                           name      TEXT,
                           latitude  REAL,
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


if __name__ == '__main__':
    initialize_database()
    print("Database initialized.")
    cont = input("Press y to add a station or any other key to exit: ")
    # Loop to add stations
    while cont.lower() == "y":
        station_id = input("Enter the id of the station: ")
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()
            # Insert the new station into the station table
            cursor.execute('''
                           INSERT INTO stations (id, latitude, longitude, name)
                           VALUES (?, ?, ?, ?)
                           ''', (station_id, get_location(station_id)[0], get_location(station_id)[1],
                                 get_station_name(station_id)))
        print("Station added.")
        cont = input("Press y to add another station or any other key to exit: ")

    print("Exiting.")
