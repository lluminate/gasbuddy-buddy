from flask import Flask, jsonify
import sqlite3

from flask_cors import CORS
app = Flask(__name__)
CORS(app)
DATABASE = './gas_station.db'  # Adjust the path if your database is in a different location

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    return conn

def close_db(conn):
    if conn:
        conn.close()

@app.route('/api/gas_prices')
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)