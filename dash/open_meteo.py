import httpx

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def open_meteo_fetch_forecast(zip_code: str, country_code: str = "US") -> dict[str, float]:
    assert country_code == "US"
    assert zip_code == "94025", zip_code
    lat, lng = 37.4528, -122.1833

    params = {
        "latitude": f"{lat}",
        "longitude": f"{lng}",
        "hourly": "temperature_2m",
        "timezone": "auto",
    }
    response = httpx.get(OPEN_METEO_BASE_URL, params=params)
    response.raise_for_status()
    payload = response.json()
    hourly_data = payload["hourly"]
    return {
        dt: round(temp, 1)
        for dt, temp in zip(
            hourly_data["time"],
            hourly_data["temperature_2m"],
            strict=False,
        )
    }
