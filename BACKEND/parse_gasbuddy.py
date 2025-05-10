import re
from bs4 import BeautifulSoup
import requests

def get_info(station_id):
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

        return (price, time)

def get_location(station_id):
    url = f"https://www.gasbuddy.com/station/{station_id}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "lxml")
        # Find the latitude and longitude elements
        latitude_element = soup.find(string=re.compile(r'"latitude":\s*([0-9.-]+)'))
        longitude_element = soup.find(string=re.compile(r'"longitude":\s*([0-9.-]+)'))
        if latitude_element and longitude_element:
            latitude_match = re.search(r'"latitude":\s*([0-9.-]+)', latitude_element)
            longitude_match = re.search(r'"longitude":\s*([0-9.-]+)', longitude_element)
            if latitude_match and longitude_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                #print(f"Latitude: {latitude}")
                #print(f"Longitude: {longitude}")
                return (latitude, longitude)
        else:
            print("Location not found")

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
            #print(f"Station Name: {station_name.group(1)}")
            return station_name.group(1)
        else:
            print("Station name not found")
    else:
        print("Title not found")

if __name__ == "__main__":
    data = {"name": get_station_name(65469), "latitude": get_location(65469)[0], "longitude": get_location(65469)[1]}
    last_update = {"last_updated": get_info(65469)[1], "price": get_info(65469)[0]}

    print(data)
    print(last_update)