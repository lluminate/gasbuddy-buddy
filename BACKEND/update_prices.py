import asyncio
from gasbuddy import GasBuddy
import configparser
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

def initialize_database(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regular_gas_prices (
                id INTEGER PRIMARY KEY,
                price REAL,
                last_updated TEXT
            )
        ''')

async def update_prices(config):
    gasbuddy = GasBuddy()
    response = await gasbuddy.price_lookup_service(lat=config["latitude"], lon=config["longitude"], limit=1)

    prices = {
        "regular_gas": (response["results"][0]["regular_gas"]["price"], response["results"][0]["regular_gas"]["last_updated"])
    }

    with sqlite3.connect(config["db_name"]) as conn:
        cursor = conn.cursor()
        for gas_type, (price, last_updated) in prices.items():
            table_name = f"{gas_type}_prices"
            cursor.execute(f'''
                INSERT INTO {table_name} (price, last_updated)
                VALUES (?, ?)
            ''', (price, last_updated))
            print(f"{gas_type.replace('_', ' ').title()} price has been updated.")

async def main():
    config = read_config()
    initialize_database(config["db_name"])
    scheduler = AsyncIOScheduler()
    interval_hours = int(input("How long between each update check? (in hours): "))
    scheduler.add_job(update_prices, IntervalTrigger(hours=interval_hours), args=[config])
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    print(f"Gas prices will be updated every {interval_hours} hours.")
    # Keep the script running
    await asyncio.Event().wait()
    await scheduler.shutdown()

def read_config():
    config = configparser.ConfigParser()
    if not config.read('config.ini'):
        print("Configuration file not found. Creating a new one.")
        latitude = input("Latitude: ")
        longitude = input("Longitude: ")
        config["Location"] = {"latitude": latitude, "longitude": longitude}
        config["Database"] = {"db_name": "gas_station.db"}
        with open("config.ini", "w") as configfile:
            config.write(configfile)
    config.read('config.ini')
    return {
        'latitude': float(config.get('Location', 'latitude')),
        'longitude': float(config.get('Location', 'longitude')),
        'db_name': config.get('Database', 'db_name'),
    }

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Exiting...")