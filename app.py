import json
import os

import dash
from dash import Input, Output, callback, dcc, html
from dotenv import load_dotenv

from mqtt_client import get_recent_messages, publish_message, start_mqtt_connection

# Load environment variables from .env file
load_dotenv()

# Initialize MQTT connection
mqtt_client = start_mqtt_connection()

# Initialize Dash app
app = dash.Dash(__name__, assets_folder="assets")
app.title = os.getenv("TITLE", "IoT Message Viewer")

UPDATE_INTERVAL_MS = int(os.getenv("UPDATE_INTERVAL_MS", "3000"))
MQTT_TOPIC_DHT = os.getenv("MQTT_TOPIC_DHT", "sic/dibimbing/weresick/fadil/pub/dht")
MQTT_TOPIC_LED = os.getenv("MQTT_TOPIC_LED", "sic/dibimbing/weresick/fadil/pub/led")

# App layout focusing on incoming MQTT messages
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    os.getenv("TITLE", "IoT Message Viewer"),
                    style={
                        "margin": 0,
                        "color": "#f1f5f9",
                        "fontSize": "2rem",
                        "fontWeight": "700",
                    },
                ),
                html.P(
                    os.getenv("SUBTITLE", "Realtime MQTT message stream"),
                    style={
                        "margin": "0.5rem 0 0 0",
                        "color": "#cbd5e1",
                        "fontSize": "1rem",
                    },
                ),
                html.P(
                    f"DHT Topic: {MQTT_TOPIC_DHT} | LED Topic: {MQTT_TOPIC_LED}",
                    style={
                        "margin": "0.75rem 0 0 0",
                        "color": "#94a3b8",
                        "fontSize": "0.95rem",
                    },
                ),
            ],
            style={
                "padding": "2rem",
                "borderBottom": "1px solid #1e293b",
                "backgroundColor": "#0f172a",
            },
        ),
        # LED Control Panel
        html.Div(
            [
                html.Div(
                    [
                        html.Span(
                            "💡 LED Control",
                            style={
                                "fontSize": "1.1rem",
                                "fontWeight": "600",
                                "color": "#f1f5f9",
                                "marginRight": "1rem",
                            },
                        ),
                        html.Button(
                            "🔴 LED ON",
                            id="btn-led-on",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#10b981",
                                "color": "#fff",
                                "border": "none",
                                "padding": "0.5rem 1rem",
                                "borderRadius": "0.5rem",
                                "marginRight": "0.5rem",
                                "cursor": "pointer",
                                "fontWeight": "600",
                            },
                        ),
                        html.Button(
                            "⚫ LED OFF",
                            id="btn-led-off",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#ef4444",
                                "color": "#fff",
                                "border": "none",
                                "padding": "0.5rem 1rem",
                                "borderRadius": "0.5rem",
                                "cursor": "pointer",
                                "fontWeight": "600",
                            },
                        ),
                        html.Span(
                            id="led-status",
                            children="--",
                            style={
                                "marginLeft": "1rem",
                                "color": "#94a3b8",
                                "fontSize": "0.9rem",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "padding": "1rem",
                        "backgroundColor": "#1e293b",
                        "borderRadius": "0.75rem",
                        "border": "1px solid #334155",
                    },
                ),
            ],
            style={
                "padding": "2rem 2rem 1rem 2rem",
                "backgroundColor": "#0f172a",
            },
        ),
        dcc.Interval(
            id="interval-component",
            interval=UPDATE_INTERVAL_MS,
            n_intervals=0,
        ),
        html.Div(
            [
                html.Div(
                    id="message-feed",
                    children=html.Div(
                        "Belum ada pesan MQTT yang diterima.",
                        style={
                            "padding": "1rem",
                            "color": "#94a3b8",
                        },
                    ),
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "0.75rem",
                    },
                ),
            ],
            style={
                "padding": "1rem 2rem 2rem 2rem",
                "backgroundColor": "#0f172a",
                "minHeight": "calc(100vh - 250px)",
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


@callback(Output("message-feed", "children"), Input("interval-component", "n_intervals"))
def update_message_feed(_):
    """Refresh message feed with the latest MQTT payloads."""
    messages = get_recent_messages()

    if not messages:
        return html.Div(
            "Belum ada pesan MQTT yang diterima.",
            style={
                "padding": "1rem",
                "color": "#94a3b8",
            },
        )

    display_messages = list(reversed(messages[-50:]))
    
    # Separate messages by topic
    dht_messages = [m for m in display_messages if "dht" in m.get("topic", "").lower()]
    led_messages = [m for m in display_messages if "led" in m.get("topic", "").lower()]
    
    cards = []
    
    # DHT Section
    if dht_messages or led_messages:  # Show section headers if any messages exist
        cards.append(
            html.Div(
                [
                    html.H3(
                        "📊 DHT11 Temperature & Humidity",
                        style={
                            "margin": "0 0 1rem 0",
                            "color": "#f1f5f9",
                            "fontSize": "1.1rem",
                            "fontWeight": "600",
                            "borderBottom": "2px solid #06b6d4",
                            "paddingBottom": "0.5rem",
                        },
                    ),
                ],
                style={
                    "marginTop": "0.5rem" if not cards else "1.5rem",
                },
            )
        )
    
    if dht_messages:
        for message in dht_messages:
            payload = message.get("payload")
            topic = message.get("topic", "unknown")

            if isinstance(payload, dict):
                payload_text = json.dumps(payload, indent=2, ensure_ascii=False)
            else:
                payload_text = str(payload)

            cards.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    message.get("timestamp", "--:--:--"),
                                    style={
                                        "fontWeight": "600",
                                        "color": "#f1f5f9",
                                    },
                                ),
                                html.Span(
                                    f" · {topic}",
                                    style={
                                        "color": "#94a3b8",
                                        "marginLeft": "0.25rem",
                                    },
                                ),
                            ]
                        ),
                        html.Pre(
                            payload_text,
                            style={
                                "backgroundColor": "#1e293b",
                                "padding": "0.75rem",
                                "borderRadius": "0.5rem",
                                "margin": "0.5rem 0 0 0",
                                "whiteSpace": "pre-wrap",
                                "wordBreak": "break-word",
                                "fontSize": "0.9rem",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#1e293b",
                        "border": "2px solid #06b6d4",
                        "borderRadius": "0.75rem",
                        "padding": "1rem",
                    },
                )
            )
    else:
        cards.append(
            html.Div(
                "Belum ada data DHT",
                style={
                    "padding": "1rem",
                    "color": "#64748b",
                    "fontSize": "0.9rem",
                },
            )
        )
    
    # LED Section
    cards.append(
        html.Div(
            [
                html.H3(
                    "💡 LED Control Messages",
                    style={
                        "margin": "1.5rem 0 1rem 0",
                        "color": "#f1f5f9",
                        "fontSize": "1.1rem",
                        "fontWeight": "600",
                        "borderBottom": "2px solid #f97316",
                        "paddingBottom": "0.5rem",
                    },
                ),
            ],
        )
    )
    
    if led_messages:
        for message in led_messages:
            payload = message.get("payload")
            topic = message.get("topic", "unknown")

            if isinstance(payload, dict):
                payload_text = json.dumps(payload, indent=2, ensure_ascii=False)
            else:
                payload_text = str(payload)

            cards.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    message.get("timestamp", "--:--:--"),
                                    style={
                                        "fontWeight": "600",
                                        "color": "#f1f5f9",
                                    },
                                ),
                                html.Span(
                                    f" · {topic}",
                                    style={
                                        "color": "#94a3b8",
                                        "marginLeft": "0.25rem",
                                    },
                                ),
                            ]
                        ),
                        html.Pre(
                            payload_text,
                            style={
                                "backgroundColor": "#1e293b",
                                "padding": "0.75rem",
                                "borderRadius": "0.5rem",
                                "margin": "0.5rem 0 0 0",
                                "whiteSpace": "pre-wrap",
                                "wordBreak": "break-word",
                                "fontSize": "0.9rem",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "#1e293b",
                        "border": "2px solid #f97316",
                        "borderRadius": "0.75rem",
                        "padding": "1rem",
                    },
                )
            )
    else:
        cards.append(
            html.Div(
                "Belum ada pesan LED",
                style={
                    "padding": "1rem",
                    "color": "#64748b",
                    "fontSize": "0.9rem",
                },
            )
        )

    return cards


@callback(
    [Output("led-status", "children"), Output("led-status", "style")],
    [Input("btn-led-on", "n_clicks"), Input("btn-led-off", "n_clicks")],
)
def control_led(on_clicks, off_clicks):
    """Handle LED control button clicks."""
    if on_clicks + off_clicks == 0:
        return ("--", {"marginLeft": "1rem", "color": "#94a3b8", "fontSize": "0.9rem"})

    # Determine which button was clicked last
    ctx = dash.callback_context
    if not ctx.triggered:
        return ("--", {"marginLeft": "1rem", "color": "#94a3b8", "fontSize": "0.9rem"})

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "btn-led-on":
        message = json.dumps({"action": "on", "status": True})
        status_text = "✓ Mengirim: ON"
        status_color = "#10b981"
    else:
        message = json.dumps({"action": "off", "status": False})
        status_text = "✓ Mengirim: OFF"
        status_color = "#ef4444"

    # Publish to LED topic
    publish_message(MQTT_TOPIC_LED, message)

    return (
        status_text,
        {
            "marginLeft": "1rem",
            "color": status_color,
            "fontSize": "0.9rem",
            "fontWeight": "600",
        },
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    app.run_server(
        debug=debug,
        host="0.0.0.0",
        port=port,
    )
