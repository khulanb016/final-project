import altair as alt
import pandas as pd
import pydeck as pdk

# Pydeck map of all CTA stations colored by line.
def map_deck(stations, line_colors):
    def hex_to_rgb(hex_color):         
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

# Top 10 stations by total nearby crime
def top_stations_fig(df):
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
            alt.X("crime_count:Q", title="Total Crimes"),
            alt.Y("stationname_mapped:N", title="Station", sort="-x"),
        )
        .properties(
            title="Top 10 CTA Stations by Nearby Crime",
            width=500,
            height=320,
        )
    )

# Top 10 crime types near CTA stations — companion to top_stations_fig.
def crime_type_fig(df):
    top = (
        df.groupby("Primary Type")["crime_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    return (
        alt.Chart(top)
        .mark_bar(color="#522398")
        .encode(
            alt.X("crime_count:Q", title="Total Count"),
            alt.Y("Primary Type:N", title="Crime Type", sort="-x"),
        )
        .properties(
            title="Top 10 Crime Types Near CTA Stations",
            width=500,
            height=320,
        )
    )


# Scatter of total crime vs total ridership per station, colored by line.
def correlation_scatter_fig(df, line_colors):
    agg = (
        df.groupby(["stationname_mapped", "primary_line"])
        .agg(crime_count=("crime_count", "sum"), rides=("rides", "sum"))
        .reset_index()
    )

    domain = list(line_colors.keys())
    range_ = list(line_colors.values())

    scatter = (
        alt.Chart(agg)
        .mark_circle(opacity=0.7, size=80)
        .encode(
            alt.X("crime_count:Q", title="Total Crime Incidents"),
            alt.Y("rides:Q", title="Total Rides"),
            alt.Color(
                "primary_line:N",
                scale=alt.Scale(domain=domain, range=range_),
                title="Line",
            ),
            alt.Tooltip(["stationname_mapped:N", "primary_line:N", "crime_count:Q", "rides:Q"]),
        )
    )

    trendline = (
        alt.Chart(agg)
        .transform_regression("crime_count", "rides")
        .mark_line(color="#555555", strokeDash=[4, 4])
        .encode(
            alt.X("crime_count:Q"),
            alt.Y("rides:Q"),
        )
    )

    return (
        (scatter + trendline)
        .properties(
            title="Total Crime vs. Total Ridership by Station",
            width=700,
            height=400,
        )
    )

# Crime and ridership plotted on the same timeline with independent y-axes.
def dual_axis_trend_fig(df):
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
