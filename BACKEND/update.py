
import sqlite3
from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup

#database_path = "/home/victor/gasbuddy-buddy/BACKEND/gas_station.db"
database_path = "gas_station.db"

def fetch_price(station_id):
    url = f"https://www.gasbuddy.com/station/{station_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        # Find the price element
        price_element = soup.find(string=re.compile(r'"price":\s*([1-9][0-9]{2}\.[0-9])'))
        time_element = soup.find(string=re.compile(r'"postedTime":\s*"(.*?)"'))
        if price_element:
            price_match = re.search(r'"price":\s*([1-9][0-9]{2}\.[0-9])', price_element)
            if price_match:
                price = price_match.group(1)
                #print(f"Price: {price}")
        else:
            print("Price not found")
        if time_element:
            time_match = re.search(r'"postedTime":\s*"(.*?)"', time_element)
            if time_match:
                time = time_match.group(1)
                #print(f"Time: {time}")
        else:
            print("Time not found")

        return price, time

def update_db(station_id, price, last_updated):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                        INSERT INTO prices (id, price, last_updated)
                        VALUES (?, ?, ?)
                    ''', (station_id, price, last_updated)
                           )
            print(f"{datetime.now().replace(microsecond=0)}:  Price for {get_name(station_id)} {get_location(station_id)} updated to {price} at {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}")
        except sqlite3.IntegrityError:
            print(f"{datetime.now().replace(microsecond=0)}:  Price for {get_name(station_id)} {get_location(station_id)} has not changed since {datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)}, not updating the database.")
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
                    SELECT id FROM stations
                ''')
        rows = cursor.fetchall()

    for station_id in rows:
        price, last_updated = fetch_price(station_id[0])
        if station_id and price and last_updated:  # Ensure all values are valid before updating
            update_db(station_id[0], price, last_updated)
        else:
            print(f"Failed to fetch or update data for station ID: {station_id}")