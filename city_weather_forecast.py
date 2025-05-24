import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import requests
import json
import time
import os

# Constants
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
if not API_KEY:
    print("Error: OPENWEATHERMAP_API_KEY environment variable not set.")
    exit()
HEADERS = {'accept': 'application/json'}
LIMIT = 1
COORDINATES_FILE = "city_coordinates.json"
FORECAST_FILE = "city_weather_forecast.json"
TITLE = "Temperature Forecast for the next five days."
TITLE_FONTSIZE = 24
LABEL_FONTSIZE = 14
X_LABEL = "Dates"
Y_LABEL = "Temperature (°C)"
PROMPT = (
    "Please enter city and optional country code (separated by comma), "
    "e.g., (London,GB) or (Abuja).\nSeparate different city/country "
    "pairs by semicolon ';', e.g., (London,GB;Abuja).\nEnter 'quit' "
    "when you want to exit. "
)


def get_coordinates(location):
    """
    Fetches the coordinates (latitude and longitude) for a given city
    and optional country code using the OpenWeatherMap Geocoding API.

    Args:
        location (str): A string containing the city name and optional
            country code, separated by a comma (e.g., "London,GB" or
            "Abuja").

    Returns:
        dict: A dictionary containing the extracted information
            (name, latitude, longitude, country, state) if the
            coordinates are found, or None if an error occurs or no
            coordinates are found.
    """
    parts = [part.strip().title() for part in location.split(',')]
    city = parts[0]
    country_code = parts[1].upper() if len(parts) > 1 else None

    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        'q': city + (f",{country_code}" if country_code else ""),
        'appid': API_KEY,
        'limit': LIMIT,
    }

    print(f"Fetching coordinates for {city},"
          f"{country_code if country_code else ''}...")
    try:
        geo_response = requests.get(geo_url, headers=HEADERS, 
                                    params=geo_params)
        geo_response.raise_for_status()  # Raise HTTPError for bad responses
        geo_response_dict = geo_response.json()
        print(f"Name: {city}\tCountry: "
              f"{country_code if country_code else None}\tStatus Code: "
              f"{geo_response.status_code}")

        if geo_response_dict:
            for city_data in geo_response_dict:  # Assume first result is best
                extracted_info = {
                    'name': city_data.get('name'),
                    'latitude': city_data.get('lat'),
                    'longitude': city_data.get('lon'),
                    'country': city_data.get('country'),
                    'state': city_data.get('state'),
                }
            return extracted_info
        else:
            print(f"No coordinates found for {city}, "
                  f"{country_code if country_code else ''}")
            return None  # Explicitly return None for no results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for {city}, "
              f"{country_code if country_code else ''}: {e}")
        return None  # Explicitly return None on error
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for coordinates of {city}, "
              f"{country_code if country_code else ''}: {e}")
        return None
    finally:
        time.sleep(1)  # Add a delay, even in case of exceptions


def get_weather_forecast(city_info):
    """
    Fetches the 5-day weather forecast for a given city using the
    OpenWeatherMap Forecast API.

    Args:
        city_info (dict): A dictionary containing the city's
            coordinates (latitude and longitude).

    Returns:
        dict: The JSON response containing the weather forecast, or
            None if an error occurs.
    """
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    forecast_params = {
        'lat': city_info['latitude'],
        'lon': city_info['longitude'],
        'appid': API_KEY,
        'units': 'metric',
    }

    print(f"Fetching weather forecast for {city_info['name']}")
    try:
        forecast_response = requests.get(forecast_url,
                                            headers=HEADERS,
                                            params=forecast_params)
        forecast_response.raise_for_status()
        forecast_response_dict = forecast_response.json()
        print(f"City name: {city_info['name']}\tStatus Code: "
              f"{forecast_response.status_code}")
        return forecast_response_dict

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {city_info['name']}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for weather in "
              f"{city_info['name']}: {e}")
        return None


def plot_forecast(forecast_data, city_name, ax):
    """
    Plots the temperature forecast for a city on a given subplot.

    Args:
        forecast_data (dict): The JSON response containing the weather
            forecast.
        city_name (str): The name of the city.
        ax (matplotlib.axes._subplots.AxesSubplot): The subplot to plot on.
    """
    if forecast_data and 'list' in forecast_data and forecast_data['list']:
        dates_strings = [item['dt_txt'] for item in forecast_data['list']]
        dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                 for date in dates_strings]
        temps = [item['main']['temp'] for item in forecast_data['list']]

        print(f"Plotting forecast for {city_name}")
        ax.plot(dates, temps, label=city_name)
    else:
        print(f"No forecast data available for {city_name}.")



def save_json(data, filename):
    """
    Saves data to a JSON file.

    Args:
        data (dict): The data to save.
        filename (str): The name of the file to save to.
    """
    path = Path(filename)
    try:
        path.write_text(json.dumps(data, indent=4))
        print(f"\nData saved to {filename}")
    except IOError as e:
        print(f"Error writing to {filename}: {e}")



def main():
    """
    Main function to run the program.
    Gets user input for cities, fetches weather data, plots forecasts,
    and saves data to JSON files.
    """
    extracted_data = []
    city_forecasts = [] # Renamed to be plural

    while True:
        user_input = input(PROMPT)

        if user_input == 'quit':
            print("Exiting session...")
            break

        if not user_input:
            print("Please enter a valid city and/or country code.")
            continue

        user_locations = [location.strip()
                          for location in user_input.split(';')]

        for location in user_locations:
            city_info = get_coordinates(location)
            if city_info:  # Only proceed if coordinates were found
                extracted_data.append(city_info)

        # Save the extracted city coordinates to a JSON file
        save_json(extracted_data, COORDINATES_FILE)

        fig, ax = plt.subplots()  # Create figure and axes *once*
        for city_info in extracted_data:
            forecast_data = get_weather_forecast(city_info)
            if forecast_data:
                city_forecasts.append(forecast_data) # collect the forecast data
                plot_forecast(forecast_data, city_info['name'], ax)

        ax.set_title(TITLE, fontsize=TITLE_FONTSIZE)
        ax.set_xlabel(X_LABEL, fontsize=LABEL_FONTSIZE)
        ax.set_ylabel(Y_LABEL, fontsize=LABEL_FONTSIZE)
        fig.autofmt_xdate()
        ax.legend()
        plt.show()

        # Save the extracted city forecasts to a JSON file.
        save_json(city_forecasts, FORECAST_FILE)
        break # Exit the loop after processing one set of locations


if __name__ == "__main__":
    main()
