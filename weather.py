import openmeteo_requests
import requests_cache
from constants import WEATHER_CODES
from retry_requests import retry

# Retrieves current weather data from Openmeteo API
def get_weather():

    # Set up the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)


    url = "https://api.open-meteo.com/v1/forecast" # Link to Openmeteo API

    # Specify data to return
    params = {
        "latitude": 33.95,
        "longitude": -83.38,
        "temperature_unit": "fahrenheit",
        "current": ["temperature_2m", "weather_code"],
        "hourly": "precipitation_probability",
        "timezone": "auto",
        "forecast_hours": 1,
    }

    # Get data from API
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process current data
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_code = int(current.Variables(1).Value())

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    current_precipitation_probability = int(hourly.Variables(0).ValuesAsNumpy()[0])

    # Return a dictionary with the values
    data = {
        "temp": current_temperature_2m,
        "rain_chance": current_precipitation_probability,
        "code": WEATHER_CODES.get(current_code, "Unknown"),
    }

    return data

# Prints out ASCII art of weather condition
def print_picture(data):
    condition = data["code"] # current weather condition
    txt_file = None

    # Match condition with the proper ASCII Art
    if condition == "Sunny":
        txt_file = "img/sunny2.txt"
    elif condition == "Partly Cloudy":
        txt_file = "img/cloudy.txt"
    elif condition == "Overcast":
        txt_file = "img/overcast.txt"
    elif condition == "Foggy":
        txt_file = "img/overcast.txt"
    elif condition == "Thunderstorm":
        txt_file = "img/thunderstorm.txt"
    elif condition == "Snowy":
        txt_file = "img/snowy.txt"

    # Print out each line in txt_file
    with open(txt_file, "r") as file:
        for line in file:
            print(line, end="")
def print_data(data):
    condition = data["code"]
    print("\n")
    # print(" " * 12, end="")
    print("Athens, GA\n")

    # Print weather conditions
    # print(" " * 12, end="")
    print(condition)
    #print(" " * 12, end="")
    print(str(int(data["temp"])) + "°F")
    #print(" " * 12, end="")
    print("Rain in next hour:", str(data["rain_chance"]) + "%")

def main():
    weather_data = get_weather()
    print_picture(weather_data)
    print_data(weather_data)


if __name__ == "__main__":
    main()