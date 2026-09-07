import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Weather App", page_icon="🌤️")

st.title("🌤️ Weather App")

# Search
city = st.text_input("🔍 Search City", "Karachi")

if st.button("Get Weather"):

    # City Search
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "format": "json"}
    ).json()

    if "results" not in geo:
        st.error("❌ City not found")
        st.stop()

    loc = geo["results"][0]
    lat = loc["latitude"]
    lon = loc["longitude"]

    # Weather API
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 3,
            "timezone": "auto"
        }
    ).json()

    # Current Weather
    current = weather["current"]

    st.subheader(
        f"📍 {loc['name']}, {loc['country']}"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🌡️ Temperature",
        f"{current['temperature_2m']} °C"
    )

    c2.metric(
        "💧 Humidity",
        f"{current['relative_humidity_2m']}%"
    )

    c3.metric(
        "💨 Wind",
        f"{current['wind_speed_10m']} km/h"
    )

    # 3 Day Forecast
    st.subheader("📅 3 Days Forecast")

    d = weather["daily"]

    df = pd.DataFrame({
        "Date": d["time"],
        "Max 🌡️": d["temperature_2m_max"],
        "Min 🌡️": d["temperature_2m_min"],
        "Rain 🌧️": d["precipitation_sum"]
    })

    st.dataframe(
        df,
        use_container_width=True
    )

    # Map
    st.subheader("🗺️ Location")

    st.map(
        pd.DataFrame({
            "lat": [lat],
            "lon": [lon]
        })
    )

    