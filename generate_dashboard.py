import html
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

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
            temperature = html.escape(
                str(period.get("temperature", "--"))
            )
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


def get_nasa_apod():
    """
    Retrieves NASA's Astronomy Picture of the Day.
    """

    nasa_api_key = os.getenv("NASA_API_KEY")

    if not nasa_api_key:
        raise ValueError("NASA_API_KEY is missing from the .env file.")

    nasa_url = "https://api.nasa.gov/planetary/apod"

    nasa_response = requests.get(
        nasa_url,
        params={
            "api_key": nasa_api_key,
            "thumbs": "true",
        },
        timeout=30,
    )
    nasa_response.raise_for_status()

    return nasa_response.json()


def build_nasa_html():
    """
    Creates the HTML displayed inside the NASA card.
    """

    try:
        nasa_data = get_nasa_apod()

        title = html.escape(
            str(nasa_data.get("title", "Astronomy Picture of the Day"))
        )
        explanation = html.escape(
            str(nasa_data.get("explanation", "No explanation available."))
        )
        apod_date = html.escape(str(nasa_data.get("date", "")))
        media_type = nasa_data.get("media_type", "image")

        copyright_name = nasa_data.get("copyright")

        if copyright_name:
            credit_html = (
                f"<p class=\"nasa-credit\">"
                f"Credit: {html.escape(str(copyright_name))}"
                f"</p>"
            )
        else:
            credit_html = ""

        if media_type == "video":
            visual_url = nasa_data.get("thumbnail_url")
            original_url = nasa_data.get("url", visual_url)
            media_label = "View NASA video"
        else:
            visual_url = nasa_data.get("hdurl") or nasa_data.get("url")
            original_url = nasa_data.get("url", visual_url)
            media_label = "View full-size NASA image"

        if not visual_url:
            raise ValueError("NASA did not provide an image or thumbnail URL.")

        safe_visual_url = html.escape(str(visual_url), quote=True)
        safe_original_url = html.escape(str(original_url), quote=True)
        safe_media_label = html.escape(media_label)

        return f"""
        <div class="nasa-content">
            <a
                href="{safe_original_url}"
                target="_blank"
                rel="noopener noreferrer"
            >
                <img
                    class="nasa-image"
                    src="{safe_visual_url}"
                    alt="{title}"
                >
            </a>

            <div class="nasa-details">
                <h3>{title}</h3>
                <p class="nasa-date">{apod_date}</p>
                {credit_html}
                <p>{explanation}</p>

                <a
                    class="nasa-link"
                    href="{safe_original_url}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    {safe_media_label}
                </a>
            </div>
        </div>
        """

    except (
        requests.RequestException,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        print(f"NASA information could not be retrieved: {error}")

        return """
        <p>NASA's Astronomy Picture of the Day is temporarily unavailable.</p>
        """


def generate_dashboard():
    """
    Creates the dashboard's index.html file.
    """

    updated_time = datetime.now().strftime(
        "%A, %B %d, %Y at %I:%M %p"
    )

    weather_html = build_weather_html()
    nasa_html = build_nasa_html()

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Doug's Morning Dashboard</title>

    <link rel="stylesheet" href="styles.css">
</head>

<body>
    <header>
        <h1>Doug's Morning Dashboard</h1>
        <p>Charlotte weather and NASA's Astronomy Picture of the Day</p>
    </header>

    <main>
        <section class="dashboard-card weather-card">
            <h2>Charlotte Weather</h2>
            {weather_html}
        </section>

        <section class="dashboard-card nasa-card">
            <h2>NASA Astronomy Picture</h2>
            {nasa_html}
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