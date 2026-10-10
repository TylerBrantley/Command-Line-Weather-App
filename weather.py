import openmeteo_requests
import requests_cache
import argparse
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
        "wind_speed_unit": "mph",
        "current": ["temperature_2m", "weather_code", "relative_humidity_2m", "wind_speed_10m",
                    "wind_direction_10m", "wind_gusts_10m", "is_day"],
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
    current_humiditiy = int(current.Variables(2).Value())
    current_wind_speed = int(current.Variables(3).Value())
    current_wind_direction = current.Variables(4).Value()
    current_wind_gusts = int(current.Variables(5).Value())
    current_isDay = current.Variables(6).Value()

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    current_precipitation_probability = int(hourly.Variables(0).ValuesAsNumpy()[0])

    # Return a dictionary with the values
    data = {
        "temp": current_temperature_2m,
        "rain_chance": current_precipitation_probability,
        "code": WEATHER_CODES.get(current_code, "Unknown"),
        "humidity": current_humiditiy,
        "wind_speed": current_wind_speed,
        "wind_direction": current_wind_direction,
        "wind_gusts": current_wind_gusts,
        "is_day": current_isDay,
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
    elif condition == "Rainy":
        txt_file = "img/rainy.txt"
    elif condition == "Thunderstorm":
        txt_file = "img/thunderstorm.txt"
    elif condition == "Snowy":
        txt_file = "img/snowy.txt"

    # Print out each line in txt_file
    with open(txt_file, "r") as file:
        for line in file:
            print(line, end="")

# Prints the weather data gathered from Openmeteo API
def print_data(data):
    condition = data["code"]
    print("\n\nAthens, GA\n")

    # Print weather conditions
    print(condition)
    print(str(int(data["temp"])) + "°F")
    print("Rain in next hour:", str(data["rain_chance"]) + "%")

# Prints extra weather data if verbose option is present
def print_more_data(data):
    print("Humidity:", str(data["humidity"]) + "%")
    print("Wind speed:", str(data["wind_speed"]) + "mph", get_wind_arrow(data["wind_direction"]), "\nwith gusts up to", str(data["wind_gusts"]) + "mph")

# Returns a string of the arrow direction of the wind based off wind direction degrees
def get_wind_arrow(deg):
    deg = deg % 360 # Just to ensure value is within range
    # Determine wind direction arrow based off of degrees
    if deg >= 337.5 or deg <= 22.5: return "↓" # North wind
    if 22.5 < deg < 67.5: return "↙" # Northeast wind
    if 67.5 <= deg <= 112.5: return "←" # East wind
    if 112.5 < deg < 157.5: return "↖" # Southeast wind
    if 157.5 <= deg <= 202.5: return "↑" # South wind
    if 202.5 < deg < 247.5: return "↗" # Southwest wind
    if 247.5 <= deg <= 292.5: return "→" # West wind
    if 292.5 < deg < 337.5: return "↘" # Northwest wind

def main():
    # Initialize Parser
    parser = argparse.ArgumentParser(description="Athens Weather API")
    parser.add_argument("--verbose", "-v", action="store_true", help="View more detailed information")
    args = parser.parse_args()

    # Retrieve data from Openmeteo API
    weather_data = get_weather()

    # Print ASCII art with proper weather condition
    print_picture(weather_data)

    # Print basic data retrieved from API
    print_data(weather_data)

    # If verbose flag is present, print extra data
    if args.verbose:
        print_more_data(weather_data)


if __name__ == "__main__":
    main()