import httpx
from uszipcode import SearchEngine

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def open_meteo_fetch_forecast(zip_code: str, country_code: str = "US") -> dict[str, float]:
    assert country_code == "US"
    lat, lng = zip_to_coords(zip_code)

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


zip_eng = SearchEngine()


def zip_to_coords(zip_code: str) -> tuple[float, float]:
    """Maps ZIP to a (lat,lng) tuple."""
    r = zip_eng.by_zipcode(zip_code)
    assert r, zip_code
    assert isinstance(r.lat, float)
    assert isinstance(r.lng, float)
    return r.lat, r.lng
