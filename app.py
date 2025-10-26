import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
from datetime import datetime
import os
from mqtt_client import start_mqtt_connection, get_sensor_data, get_latest_reading

# Initialize MQTT connection
mqtt_client = start_mqtt_connection()

# Initialize Dash app
app = dash.Dash(__name__, assets_folder="assets")
app.title = "IoT Dashboard - DHT11 Sensor"

# Custom CSS variables for dark theme
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #0f172a; color: #f1f5f9;">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout
app.layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=3000,  # Update every 3 seconds
            n_intervals=0,
        ),
        
        # Header section
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "🌡️ IoT Dashboard",
                            style={
                                "margin": 0,
                                "color": "#f1f5f9",
                                "fontSize": "2.5rem",
                                "fontWeight": "700",
                            },
                        ),
                        html.P(
                            "Real-time DHT11 Sensor Monitoring via MQTT",
                            style={
                                "margin": "0.5rem 0 0 0",
                                "color": "#cbd5e1",
                                "fontSize": "1rem",
                            },
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            id="live-clock",
                            style={
                                "fontSize": "1.25rem",
                                "color": "#f1f5f9",
                                "fontWeight": "500",
                            },
                        ),
                    ],
                    style={
                        "textAlign": "right",
                    },
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "padding": "2rem",
                "borderBottom": "2px solid #1e293b",
                "backgroundColor": "#0f172a",
            },
        ),

        # Stats section
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            "🌡️",
                                            style={
                                                "fontSize": "2rem",
                                                "marginRight": "0.5rem",
                                            },
                                        ),
                                        html.Span(
                                            "Temperature",
                                            style={
                                                "color": "#94a3b8",
                                                "fontSize": "0.875rem",
                                                "fontWeight": "500",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "0.75rem",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            id="temp-value",
                                            children="-- ",
                                            style={
                                                "fontSize": "2rem",
                                                "fontWeight": "700",
                                                "color": "#f1f5f9",
                                            },
                                        ),
                                        html.Span(
                                            "°C",
                                            style={
                                                "fontSize": "1.5rem",
                                                "color": "#94a3b8",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "alignItems": "baseline"},
                                ),
                            ],
                            style={
                                "backgroundColor": "#1e293b",
                                "padding": "1.5rem",
                                "borderRadius": "0.75rem",
                                "border": "1px solid #334155",
                            },
                        ),
                    ],
                    style={"flex": "1", "marginRight": "1rem"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            "💧",
                                            style={
                                                "fontSize": "2rem",
                                                "marginRight": "0.5rem",
                                            },
                                        ),
                                        html.Span(
                                            "Humidity",
                                            style={
                                                "color": "#94a3b8",
                                                "fontSize": "0.875rem",
                                                "fontWeight": "500",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "0.75rem",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            id="humidity-value",
                                            children="-- ",
                                            style={
                                                "fontSize": "2rem",
                                                "fontWeight": "700",
                                                "color": "#f1f5f9",
                                            },
                                        ),
                                        html.Span(
                                            "%",
                                            style={
                                                "fontSize": "1.5rem",
                                                "color": "#94a3b8",
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "alignItems": "baseline"},
                                ),
                            ],
                            style={
                                "backgroundColor": "#1e293b",
                                "padding": "1.5rem",
                                "borderRadius": "0.75rem",
                                "border": "1px solid #334155",
                            },
                        ),
                    ],
                    style={"flex": "1"},
                ),
            ],
            style={
                "display": "flex",
                "padding": "2rem",
                "gap": "1rem",
            },
        ),

        # Charts section
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="temperature-chart",
                            style={"height": "400px"},
                            config={"responsive": True, "displayModeBar": False},
                        ),
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "0.75rem",
                        "border": "1px solid #334155",
                        "padding": "1.5rem",
                        "marginRight": "1rem",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="humidity-chart",
                            style={"height": "400px"},
                            config={"responsive": True, "displayModeBar": False},
                        ),
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "0.75rem",
                        "border": "1px solid #334155",
                        "padding": "1.5rem",
                    },
                ),
            ],
            style={
                "display": "flex",
                "padding": "0 2rem 2rem 2rem",
                "gap": "1rem",
            },
        ),

        # Footer
        html.Div(
            [
                html.Span(
                    "Last Updated: ",
                    style={"color": "#94a3b8"},
                ),
                html.Span(
                    id="last-update",
                    children="--:--:--",
                    style={"color": "#f1f5f9", "fontWeight": "500"},
                ),
                html.Span(
                    " | MQTT Broker: broker.emqx.io",
                    style={"color": "#94a3b8", "marginLeft": "1rem"},
                ),
            ],
            style={
                "textAlign": "center",
                "padding": "1.5rem",
                "borderTop": "1px solid #334155",
                "backgroundColor": "#0f172a",
                "color": "#64748b",
                "fontSize": "0.875rem",
            },
        ),
    ],
    style={
        "fontFamily": "'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Helvetica Neue', sans-serif",
        "backgroundColor": "#0f172a",
        "minHeight": "100vh",
        "color": "#f1f5f9",
    },
)


@callback(
    Output("live-clock", "children"),
    Input("interval-component", "n_intervals"),
)
def update_clock(n):
    """Update live clock."""
    return datetime.now().strftime("%H:%M:%S")


@callback(
    [
        Output("temp-value", "children"),
        Output("humidity-value", "children"),
        Output("last-update", "children"),
    ],
    Input("interval-component", "n_intervals"),
)
def update_stats(n):
    """Update stats cards with latest readings."""
    latest = get_latest_reading()
    return (
        f"{latest['temperature']:.1f} ",
        f"{latest['humidity']:.1f} ",
        latest["timestamp"],
    )


@callback(
    Output("temperature-chart", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_temperature_chart(n):
    """Update temperature chart."""
    data = get_sensor_data()
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=data["timestamps"],
            y=data["temperature"],
            mode="lines+markers",
            name="Temperature",
            line=dict(color="#f97316", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(249, 115, 22, 0.1)",
        )
    )
    
    fig.update_layout(
        title="Temperature Over Time",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#1e293b",
        font=dict(color="#f1f5f9", family="Arial, sans-serif", size=12),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#334155",
            showline=True,
            linewidth=1,
            linecolor="#334155",
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#334155",
            showline=True,
            linewidth=1,
            linecolor="#334155",
        ),
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    return fig


@callback(
    Output("humidity-chart", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_humidity_chart(n):
    """Update humidity chart."""
    data = get_sensor_data()
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=data["timestamps"],
            y=data["humidity"],
            mode="lines+markers",
            name="Humidity",
            line=dict(color="#06b6d4", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(6, 182, 212, 0.1)",
        )
    )
    
    fig.update_layout(
        title="Humidity Over Time",
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
        hovermode="x unified",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#1e293b",
        font=dict(color="#f1f5f9", family="Arial, sans-serif", size=12),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#334155",
            showline=True,
            linewidth=1,
            linecolor="#334155",
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#334155",
            showline=True,
            linewidth=1,
            linecolor="#334155",
            range=[0, 100],
        ),
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    return fig


if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8050))
    
    # Run the app
    app.run_server(
        debug=False,
        host="0.0.0.0",
        port=port,
    )
