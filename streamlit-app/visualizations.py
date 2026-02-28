import altair as alt
import pandas as pd
import pydeck as pdk
from pandas import DataFrame


def map_deck(stations: DataFrame, line_colors: dict) -> pdk.Deck:
# Pydeck map of all CTA stations colored by line.
    def hex_to_rgb(hex_color: str) -> list[int]:
        hex_color = hex_color.lstrip("#")
        return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]

    df = stations.copy()
    df["color"] = df["primary_line"].apply(
        lambda x: hex_to_rgb(line_colors.get(x, "#888888"))
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=200,
        pickable=True,
    )
    view_state = pdk.ViewState(latitude=41.85, longitude=-87.65, zoom=10)
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{LONGNAME}"},
    )


def top_stations_fig(df: DataFrame) -> alt.Chart:
# Top 10 stations by total nearby crime — main finding for the presentation.
    top = (
        df.groupby("stationname_mapped")["crime_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    return (
        alt.Chart(top)
        .mark_bar(color="#C60C30")
        .encode(
            alt.X("crime_count:Q", title="Total Crimes (2022–2026)"),
            alt.Y("stationname_mapped:N", title="Station", sort="-x"),
        )
        .properties(
            title="Top 10 CTA Stations by Nearby Crime",
            width=500,
            height=320,
        )
    )


def scatter_fig(df: DataFrame) -> alt.LayerChart:
# Crime vs ridership scatter with trendline — shows the key correlation finding.
    clean = df[["stationname_mapped", "crime_count", "rides"]].dropna()

    scatter = (
        alt.Chart(clean)
        .mark_circle(opacity=0.4, color="#555555")
        .encode(
            alt.X("crime_count:Q", title="Monthly Crime Count (within 400m)"),
            alt.Y("rides:Q", title="Monthly Rides"),
            alt.Tooltip(["stationname_mapped:N", "crime_count:Q", "rides:Q"]),
        )
    )

    trendline = (
        alt.Chart(clean)
        .transform_regression("crime_count", "rides")
        .mark_line(color="#C60C30", strokeDash=[4, 4])
        .encode(
            alt.X("crime_count:Q"),
            alt.Y("rides:Q"),
        )
    )

    return (
        (scatter + trendline)
        .properties(
            title="Monthly Crime Count vs. Ridership per Station",
            width=500,
            height=320,
        )
    )


def dual_axis_trend_fig(df: DataFrame) -> alt.LayerChart:
# Crime and ridership plotted on the same timeline with independent y-axes.
    agg = (
        df.groupby(["year", "month"])
        .agg(crime_count=("crime_count", "sum"), rides=("rides", "sum"))
        .reset_index()
    )
    agg["date"] = pd.to_datetime(agg[["year", "month"]].assign(day=1))

    crime_line = (
        alt.Chart(agg)
        .mark_line(color="#C60C30")
        .encode(
            alt.X("date:T", title="Month"),
            alt.Y("crime_count:Q", title="Total Crime Incidents", axis=alt.Axis(titleColor="#C60C30")),
        )
    )

    rides_line = (
        alt.Chart(agg)
        .mark_line(color="#00A1DE", strokeDash=[4, 4])
        .encode(
            alt.X("date:T"),
            alt.Y("rides:Q", title="Total Rides", axis=alt.Axis(titleColor="#00A1DE")),
        )
    )

    return (
        alt.layer(crime_line, rides_line)
        .resolve_scale(y="independent")
        .properties(title="Crime vs. Ridership Over Time", width=700, height=320)
    )


def crime_trend_fig(df: DataFrame) -> alt.Chart:
# Monthly crime trend over time — shows overall pattern across the system.
    monthly = (
        df.groupby(["year", "month"])["crime_count"]
        .sum()
        .reset_index()
    )
    monthly["date"] = pd.to_datetime(monthly[["year", "month"]].assign(day=1))

    return (
        alt.Chart(monthly)
        .mark_line(color="#C60C30")
        .encode(
            alt.X("date:T", title="Month"),
            alt.Y("crime_count:Q", title="Crime Count"),
        )
        .properties(
            title="Total Monthly Crime Near CTA Stations",
            width=500,
            height=280,
        )
    )
