import asyncio
from gasbuddy import GasBuddy
import sqlite3
from datetime import datetime

#database_path = "/home/victor/gasbuddy-buddy/BACKEND/gas_station.db"
database_path = "gas_station.db"

async def fetch_price(location):
    gasbuddy = GasBuddy()
    response = await gasbuddy.price_lookup_service(lat=location["latitude"], lon=location["longitude"], limit=1)
    return response["results"][0]["station_id"], response["results"][0]["regular_gas"]["price"], response["results"][0]["regular_gas"]["last_updated"]

def update_db(id, price, last_updated):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                        INSERT INTO prices (id, price, last_updated)
                        VALUES (?, ?, ?)
                    ''', (id, price, last_updated)
                           )
            print(f"{datetime.now().replace(microsecond=0)}:  Price for {get_name(id)} {get_location(id)} updated to {price} at {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}")
        except sqlite3.IntegrityError:
            print(f"{datetime.now().replace(microsecond=0)}:  Price for {get_name(id)} {get_location(id)} has not changed since {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}, not updating the database.")
        except sqlite3.OperationalError:
            print("Database does not exist, please run init_db.py first.")

def get_name(id):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # select the name of the station using id
        cursor.execute(f'''
                    SELECT name FROM stations WHERE id = {id}
                ''')
        name = cursor.fetchone()
        if name is not None:
            return name[0]
        else:
            print(f"No station found with id {id}")
            return None

def get_location(id):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # select the name of the station using id
        cursor.execute(f'''
                    SELECT latitude, longitude FROM stations WHERE id = {id}
                ''')
        location = cursor.fetchone()
        if location is not None:
            return location[0], location[1]
        else:
            print(f"No station found with id {id}")
            return None

if __name__ == "__main__":
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        # get the longitude and latitude of each station
        cursor.execute('''
                    SELECT id, longitude, latitude FROM stations
                ''')
        rows = cursor.fetchall()
        location = []
        for row in rows:
            location.append({
                "latitude": row[2],
                "longitude": row[1]
            })

        #print(location)

    # Fetch the price for each location
    for loc in location:
        id, price, last_updated = asyncio.run(fetch_price(loc))
        update_db(id, price, last_updated)
        #print(f"Station: {get_name(id)} {get_location(id)}, Price: {price}, Last Updated: {last_updated}")