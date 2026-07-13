from datetime import datetime
from pathlib import Path


def generate_dashboard():
    """
    Creates the dashboard's index.html file.
    """

    updated_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

    html = f"""<!DOCTYPE html>
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
        <section class="dashboard-card">
            <h2>Charlotte Weather</h2>
            <p>Weather information will be added here.</p>
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
    output_file.write_text(html, encoding="utf-8")

    print(f"Dashboard created successfully: {output_file.resolve()}")


if __name__ == "__main__":
    generate_dashboard()