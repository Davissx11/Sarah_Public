import os

import httpx

WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1/current.json"

WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
assert len(WEATHER_API_KEY) == 31


def weather_api_fetch_forecast(zip_code: str, country_code: str = "US") -> dict:  # type: ignore
    params = {
        "key": WEATHER_API_KEY,
        "q": f"{zip_code},{country_code}",
        "aqi": "yes",
        "days": "1",  # Number of days to forecast
        "hour": "1",  # Get hourly forecasts
    }
    response = httpx.get(WEATHER_API_BASE_URL, params=params)
    print(response.status_code, type(response), 1)
    print(response.text, 2)
    response.raise_for_status()
    return dict(response.json())
