import matplotlib.pyplot as plt
from pathlib import Path
import requests
import json
import numpy as np
import time
import os

# Constants
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
if not API_KEY:
    print("Error: OPENWEATHERMAP_API_KEY environment variable not set.")
    exit()
REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 1  # seconds
COORDINATES_FILE = "city_coordinates.json"
WEATHER_DATA_FILE = "city_weather_data.json"
PROMPT = (
    "Please enter city and optional country code (separated by comma), "
    "e.g., (London,GB) or (Abuja).\n"
    "Separate different city/country pairs by semicolon ';', "
    "e.g., (London,GB;Abuja): "
)
HEADERS = {'accept': 'application/json'}
LIMIT = 1
TITLE = "Temperatures of Different Cities"
X_LABEL = "Cities"
Y_LABEL = "Temperatures (°C)"
BAR_COLOR_CURRENT = 'violet'
BAR_COLOR_MIN = 'red'
BAR_COLOR_MAX = 'blue'
TICK_LABEL_ROTATION = 45
TICK_LABEL_ALIGNMENT = "right"


def get_coordinates(location):
    """Fetches city coordinates from OpenWeatherMap Geocoding API.

    Args:
        location (str): City name and optional country code (e.g.,
            "London,GB").

    Returns:
        dict: City coordinates (name, lat, lon, country, state) or None
            on error.
    """
    parts = [part.strip().title() for part in location.split(',')]
    city = parts[0]
    country_code = parts[1].upper() if len(parts) > 1 else None

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city + (f",{country_code}" if country_code else ""),
        'appid': API_KEY,
        'limit': LIMIT,
    }

    print(f"Fetching coordinates for {city}, {country_code or ''}...")
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        if data:
            city_data = data[0]  # Assume first result is best
            return {
                'name': city_data.get('name'),
                'latitude': city_data.get('lat'),
                'longitude': city_data.get('lon'),
                'country': city_data.get('country'),
                'state': city_data.get('state'),
            }
        else:
            print(f"No results found for {city}, {country_code or ''}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for {city}, "
              f"{country_code or ''}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for {city}, "
              f"{country_code or ''}: {e}")
        return None
    finally:
        time.sleep(RATE_LIMIT_DELAY)  # Respect API rate limits


def get_weather_data(city_info):
    """Fetches weather data for a city from OpenWeatherMap Weather API.

    Args:
        city_info (dict): City information containing latitude and longitude.

    Returns:
        dict: Weather data in JSON format or None on error.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': city_info['latitude'],
        'lon': city_info['longitude'],
        'appid': API_KEY,
        'units': 'metric',
    }

    print(f"Fetching weather data for {city_info['name']}...")
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data for {city_info['name']}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for "
              f"{city_info['name']}: {e}")
        return None
    finally:
        time.sleep(RATE_LIMIT_DELAY)  # Respect API rate limits


def save_json(data, filename):
    """Saves data to a JSON file.

    Args:
        data (dict): Data to save.
        filename (str): Name of the JSON file.
    """
    path = Path(filename)
    try:
        path.write_text(json.dumps(data, indent=4))
        print(f"\nData saved to {filename}")
    except IOError as e:
        print(f"Error writing to {filename}: {e}")


def plot_temperatures(city_weather_data):
    """Plots current, min, and max temperatures for each city.

    Args:
        city_weather_data (list): A list of dictionaries, where each
            dictionary contains weather data for a city.
    """
    if not city_weather_data:
        print("No weather data to plot.")
        return

    names = [city['name'] for city in city_weather_data]
    temps = [city['main']['temp'] for city in city_weather_data]
    min_temps = [city['main']['temp_min'] for city in city_weather_data]
    max_temps = [city['main']['temp_max'] for city in city_weather_data]

    plt.style.use('dark_background')
    bar_width = 0.2
    index = np.arange(len(names))

    plt.bar(index, temps, bar_width, color=BAR_COLOR_CURRENT,
            label='Current Temperature')
    plt.bar(index + bar_width, min_temps, bar_width,
            color=BAR_COLOR_MIN, label='Minimum Temperature')
    plt.bar(index + 2 * bar_width, max_temps, bar_width,
            color=BAR_COLOR_MAX, label='Maximum Temperature')

    plt.title(TITLE)
    plt.xlabel(X_LABEL)
    plt.ylabel(Y_LABEL)
    plt.xticks(index + bar_width, names, rotation=TICK_LABEL_ROTATION,
               ha=TICK_LABEL_ALIGNMENT)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    """Main function to run the program."""
    while True: 
        user_input = input(PROMPT)

        if user_input == "quit":
            print("Exiting the session...")
            break

        if not user_input:
            print("Enter a valid city and/or country")
            continue
        
        user_locations = [location.strip() for location in user_input.split(';')]

        extracted_data = []
        for location in user_locations:
            city_info = get_coordinates(location)
            if city_info:
                extracted_data.append(city_info)

        save_json(extracted_data, COORDINATES_FILE)

        city_weather_data = []
        for city_info in extracted_data:
            weather_data = get_weather_data(city_info)
            if weather_data:
                city_weather_data.append(weather_data)

        save_json(city_weather_data, WEATHER_DATA_FILE)
        plot_temperatures(city_weather_data)


if __name__ == "__main__":
    main()
