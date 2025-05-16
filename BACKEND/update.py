import sqlite3
from datetime import datetime
from parse_gasbuddy import fetch_price, get_station_name

# database_path = "/home/victor/gasbuddy-buddy/BACKEND/gas_station.db"
database_path = "gas_station.db"


def refresh(station_id, price, last_updated):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                        INSERT INTO prices (id, price, last_updated)
                        VALUES (?, ?, ?)
                    ''', (station_id, price, last_updated)
                           )
            print(
                f"{datetime.now().replace(microsecond=0)}:  Price for {get_station_name(station_id)} updated to {price} at {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}")
        except sqlite3.IntegrityError:
            print(
                f"{datetime.now().replace(microsecond=0)}:  Price for {get_station_name(station_id)} has not changed since {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}, not updating the database.")
        except sqlite3.OperationalError:
            print("Database does not exist, please run init_db.py first.")


def update_db():
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # get the longitude and latitude of each station
        cursor.execute('''
                       SELECT id
                       FROM stations
                       ''')
        all_station_ids = cursor.fetchall()

    for i in all_station_ids:
        price, last_updated = fetch_price(i[0])
        if i and price and last_updated:  # Ensure all values are valid before updating
            refresh(i[0], price, last_updated)
        else:
            print(f"Failed to fetch or update data for station ID: {i}")


if __name__ == "__main__":
    update_db()
