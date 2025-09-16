import os

import httpx

OPEN_WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

OPEN_WEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
assert len(OPEN_WEATHER_API_KEY) == 32


def open_weather_fetch_forecast(zip_code: str) -> dict[str, float]:
    assert len(zip_code) == 5, zip_code
    params = {
        "zip": zip_code,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial",  # or 'metric' for Celsius
    }
    response = httpx.get(OPEN_WEATHER_BASE_URL, params=params)
    response.raise_for_status()
    payload = dict(response.json())
    hourly = list(payload["list"])
    return {d["dt_txt"]: round(d["main"]["temp"], 1) for d in hourly}
