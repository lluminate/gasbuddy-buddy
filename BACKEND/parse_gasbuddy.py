from bs4 import BeautifulSoup
import requests, json, re, time
from random import choice

# List of User-Agent strings to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def fetch_price(station_id):
    data = fetch_json_data(station_id)
    if data:
        # Extract the price and time from the JSON data
        try:
            price = data['prices'][0]['credit']['price']
            time = data['prices'][0]['credit']['postedTime']
            return price, time
        except KeyError as e:
            print(f"Key error: {e}")
            return None, None
    else:
        print("No data found")
        return None, None

def fetch_json_data(station_id):
    url = f"https://www.gasbuddy.com/station/{station_id}"
    headers = {
        "User-Agent": choice(USER_AGENTS)  # Rotate User-Agent
    }
    for attempt in range(1):  # Retry up to 1 time
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "lxml")
            script_tag = soup.find("script", string=re.compile(r"window\.__APOLLO_STATE__\s*="))
            if script_tag:
                match = re.search(r"window\.__APOLLO_STATE__\s*=\s*(\{.*\});", script_tag.string)
                if match:
                    station_data = json.loads(match.group(1)).get(f"Station:{station_id}")
                    return station_data
            print("Data not found")
            return None
        elif response.status_code == 429:
            print("Rate limited. Retrying...")
            #time.sleep(2 ** attempt)  # Exponential backoff
        else:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return None
    print("Max retries reached")
    return None


def get_location(station_id):
    data = fetch_json_data(station_id)
    if data:
        # Extract the latitude and longitude from the JSON data
        try:
            latitude = data['latitude']
            longitude = data['longitude']
            return latitude, longitude
        except KeyError as e:
            print(f"Key error: {e}")
            return None, None
    else:
        print("No data found")
        return None, None


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
            # print(f"Station Name: {station_name.group(1)}")
            return station_name.group(1)
        else:
            print("Station name not found")
            return None
    else:
        print("Title not found")
        return None


if __name__ == "__main__":
    test_id = 5768
    data = {"name": get_station_name(test_id), "latitude": get_location(test_id)[0],"longitude": get_location(test_id)[1]}
    last_update = {"last_updated": fetch_price(test_id)[1], "price": fetch_price(test_id)[0]}
    print(f"https://www.gasbuddy.com/station/{test_id}")
    print(fetch_json_data(test_id))
    print(data)
    print(last_update)
