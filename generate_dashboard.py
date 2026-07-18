import html
from datetime import datetime
from pathlib import Path

import requests


CHARLOTTE_LATITUDE = 35.2271
CHARLOTTE_LONGITUDE = -80.8431

REQUEST_HEADERS = {
    "User-Agent": "DougMorningDashboard/1.0 (personal project)",
    "Accept": "application/geo+json",
}


def get_charlotte_forecast():
    """
    Retrieves the Charlotte forecast from the National Weather Service.
    """

    points_url = (
        f"https://api.weather.gov/points/"
        f"{CHARLOTTE_LATITUDE},{CHARLOTTE_LONGITUDE}"
    )

    points_response = requests.get(
        points_url,
        headers=REQUEST_HEADERS,
        timeout=30,
    )
    points_response.raise_for_status()

    points_data = points_response.json()
    forecast_url = points_data["properties"]["forecast"]

    forecast_response = requests.get(
        forecast_url,
        headers=REQUEST_HEADERS,
        timeout=30,
    )
    forecast_response.raise_for_status()

    forecast_data = forecast_response.json()

    return forecast_data["properties"]["periods"][:4]


def build_weather_html():
    """
    Creates the HTML displayed inside the weather card.
    """

    try:
        periods = get_charlotte_forecast()

        weather_periods = []

        for period in periods:
            name = html.escape(str(period.get("name", "Forecast")))
            temperature = html.escape(str(period.get("temperature", "--")))
            temperature_unit = html.escape(
                str(period.get("temperatureUnit", "F"))
            )
            short_forecast = html.escape(
                str(period.get("shortForecast", "Unavailable"))
            )
            wind_speed = html.escape(
                str(period.get("windSpeed", "Unavailable"))
            )
            wind_direction = html.escape(
                str(period.get("windDirection", ""))
            )

            weather_periods.append(
                f"""
                <div class="weather-period">
                    <h3>{name}</h3>
                    <p class="weather-temperature">
                        {temperature}&deg;{temperature_unit}
                    </p>
                    <p>{short_forecast}</p>
                    <p>
                        <strong>Wind:</strong>
                        {wind_speed} {wind_direction}
                    </p>
                </div>
                """
            )

        return f"""
        <div class="weather-grid">
            {''.join(weather_periods)}
        </div>
        """

    except (requests.RequestException, KeyError, TypeError, ValueError) as error:
        print(f"Weather could not be retrieved: {error}")

        return """
        <p>Charlotte weather is temporarily unavailable.</p>
        """


def generate_dashboard():
    """
    Creates the dashboard's index.html file.
    """

    updated_time = datetime.now().strftime(
        "%A, %B %d, %Y at %I:%M %p"
    )

    weather_html = build_weather_html()

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Doug's Morning Dashboard</title>

    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <header>
        <h1>Doug's Morning Dashboard</h1>
        <p>Weather, space, sports, news, and local information</p>
    </header>

    <main>
        <section class="dashboard-card weather-card">
            <h2>Charlotte Weather</h2>
            {weather_html}
        </section>

        <section class="dashboard-card">
            <h2>NASA Astronomy Picture</h2>
            <p>NASA information will be added here.</p>
        </section>

        <section class="dashboard-card">
            <h2>Naval Academy</h2>
            <p>Navy news and sports information will be added here.</p>
        </section>

        <section class="dashboard-card">
            <h2>Little Sugar Creek</h2>
            <p>Creek gauge information will be added here.</p>
        </section>
    </main>

    <footer>
        <p>Last updated: {updated_time}</p>
    </footer>
</body>
</html>
"""

    output_file = Path("index.html")
    output_file.write_text(page_html, encoding="utf-8")

    print(f"Dashboard created successfully: {output_file.resolve()}")


if __name__ == "__main__":
    generate_dashboard()