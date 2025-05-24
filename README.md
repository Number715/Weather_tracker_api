# City Temperature and Forecast Viewer

This repository contains two Python scripts that utilize the OpenWeatherMap API to provide temperature information for user-specified cities:

* **`city_temperature_viewer.py`**: Retrieves and displays the current, minimum, and maximum temperatures in a bar chart.
* **`city_forecast_viewer.py`**: Retrieves and displays the 5-day temperature forecast in a line plot.

## Features

### `city_temperature_viewer.py`

* **Interactive City Input:** Allows users to enter one or more cities (with optional country codes) to view their current temperatures.
* **Current, Min, and Max Temperatures:** Presents the data in a clear bar chart.
* **Data Persistence (Optional):** Saves fetched coordinates and weather data to JSON files.

### `city_forecast_viewer.py`

* **Interactive City Input:** Similar input method for retrieving forecasts.
* **5-Day Temperature Forecast:** Displays the forecast as line plots for each city.
* **Clear Visualization:** Presents temperature trends over the next five days.
* **Data Persistence (Optional):** Saves fetched coordinates and forecast data to JSON files.

**Both scripts:**

* Require an **OpenWeatherMap API key** to be set as an environment variable (`OPENWEATHERMAP_API_KEY`).
* Handle basic API request and JSON decoding errors.
* Include delays to respect API rate limits.

## How to Use

1.  **Obtain an OpenWeatherMap API Key:** Sign up at [https://openweathermap.org/appid](https://openweathermap.org/appid).

2.  **Set the API Key:** Set the `OPENWEATHERMAP_API_KEY` environment variable on your system.

3.  **Run the desired script:**
    ```bash
    python city_temperature_viewer.py
    # or
    python city_forecast_viewer.py
    ```

4.  **Enter City Information:** Follow the prompts to input city names (and optional country codes), separated by commas for each city and semicolons for multiple locations (e.g., `London,GB;Tokyo`).

5.  **View the Chart:** A Matplotlib window will display the temperature information as either a bar chart (current temperatures) or line plots (forecast).

## Prerequisites

* Python 3.x
* `requests`
* `matplotlib`

    Install dependencies:
    ```bash
    pip install requests matplotlib
    ```

## API Key

Both scripts require an OpenWeatherMap API key. Ensure you have set the `OPENWEATHERMAP_API_KEY` environment variable.

## Notes

* Ensure correct spelling of city names for accurate results.
* Including the country code (e.g., `,GB` for Great Britain) can improve accuracy.
* Forecast data is typically provided at 3-hour intervals.
* Fetched coordinates and weather data/forecasts can be saved as `city_coordinates.json`, `city_weather_data.json`, and `city_weather_forecast.json` in the script's directory.

This `README` provides a concise overview of both scripts and their usage within a single repository. Let me know if you'd like any adjustments or further details added!
