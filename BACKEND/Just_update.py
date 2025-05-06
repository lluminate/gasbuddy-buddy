import asyncio
from gasbuddy import GasBuddy
import configparser
import sqlite3

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
            # Check if the previous price has the same last update time
            cursor.execute(f'''SELECT last_updated FROM {table_name} ORDER BY last_updated DESC LIMIT 1''')
            last_price = cursor.fetchone()
            if last_price is None or last_price[0] != last_updated:
                cursor.execute(f'''
                    INSERT INTO {table_name} (price, last_updated)
                    VALUES (?, ?)
                ''', (price, last_updated))
                print(f"{gas_type.replace('_', ' ').title()} price has been updated.")

async def main():
    config = read_config()
    await update_prices(config)

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return {
        'latitude': float(config.get('Location', 'latitude')),
        'longitude': float(config.get('Location', 'longitude')),
        'db_name': config.get('Database', 'db_name'),
    }

if __name__ == "__main__":
    asyncio.run(main())