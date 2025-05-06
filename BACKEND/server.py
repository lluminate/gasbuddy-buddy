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



@app.route('/gas_prices')
def get_gas_prices():
    conn = get_db()
    cursor = conn.cursor()
    # Fetch only the last 30 days of data
    cursor.execute("SELECT * FROM regular_gas_prices WHERE last_updated >= datetime('now', '-30 days') ORDER BY last_updated DESC")
    prices = cursor.fetchall()
    close_db(conn)

    # Convert the list of Row objects to a list of dictionaries for JSON serialization
    price_list = [dict(row) for row in prices]
    return jsonify(price_list)

if __name__ == '__main__':
    app.run(port=5003, debug=True)