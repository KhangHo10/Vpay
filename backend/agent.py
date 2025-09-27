from google.adk.agents import Agent
from google.adk.tools import google_search

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city using Open-Meteo API.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    # First, get coordinates for the city
    coord_result = get_coordinates_for_city(city)
    if coord_result["status"] == "error":
        return coord_result
    
    latitude = coord_result["latitude"]
    longitude = coord_result["longitude"]
    city_name = coord_result["city_name"]
    country = coord_result["country"]
    
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "auto"
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Weather service error (HTTP {response.status_code}). Please try again later."
            }
        
        data = response.json()
        current = data.get("current", {})
        
        temp = round(current.get("temperature_2m", 0))
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed = current.get("wind_speed_10m", 0)
        weather_code = current.get("weather_code", 0)
        
        # Convert weather code to description
        condition = get_weather_description(weather_code)
        
        # Format location string
        location = f"{city_name}"
        if country:
            location += f", {country}"
        
        report = (
            f"Current weather in {location}: {condition}, {temp}°F, "
            f"humidity {humidity}%, wind {wind_speed} mph. Have a great day!"
        )
        
        return {
            "status": "success", 
            "report": report,
            "details": {
                "city": city_name,
                "country": country,
                "temperature": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "weather_code": weather_code,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_message": "Weather service request timed out. Please try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error_message": "Unable to connect to weather service. Please check your internet connection."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting weather for {city}: {str(e)}"
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    city_lower = city.lower()
    
    tz_identifier = _CITY_TIMEZONE_MAP.get(city_lower)
    
    if not tz_identifier:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}. "
                f"Please try a major city name."
            ),
        }

    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = (
            f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        )
        return {
            "status": "success", 
            "report": report,
            "details": {
                "city": city,
                "timezone": tz_identifier,
                "timestamp": now.isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting time for {city}: {str(e)}"
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)