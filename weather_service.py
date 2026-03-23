import httpx

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def fetch_weather_by_city(city: str) -> dict:
    city = city.strip()
    if not city:
        raise ValueError("City is required.")

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        geocode_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        results = geocode_data.get("results") or []
        if not results:
            raise ValueError(
                f"City '{city}' was not found by the Open-Meteo geocoding service."
            )

        place = results[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        forecast_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join(
                    [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "is_day",
                        "precipitation",
                        "weather_code",
                        "cloud_cover",
                        "wind_speed_10m",
                        "wind_direction_10m",
                    ]
                ),
                "timezone": "auto",
            },
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

    current = forecast_data.get("current")
    if not current:
        raise ValueError("Weather source returned no current weather data.")

    weather_code = current.get("weather_code")

    return {
        "resolved_city": place.get("name"),
        "country": place.get("country"),
        "admin1": place.get("admin1"),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": forecast_data.get("timezone"),
        "observation_time": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "apparent_temperature_c": current.get("apparent_temperature"),
        "relative_humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_degrees": current.get("wind_direction_10m"),
        "cloud_cover_pct": current.get("cloud_cover"),
        "precipitation_mm": current.get("precipitation"),
        "is_day": bool(current.get("is_day", 1)),
        "weather_code": weather_code,
        "weather_description": WEATHER_CODE_MAP.get(weather_code, "Unknown"),
        "source": "Open-Meteo",
    }
