import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import requests
import re

# Initialize the Dash app with Bootstrap theme for better styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="YT-TL;DR",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "YouTube TL;DR - Summarize videos quickly!"}
        ]
    )
server = app.server  # Expose the server variable for deployments

# Backend API URL (service name defined in docker-compose)
BACKEND_API_URL = "http://localhost:8000"

# Layout of the Dash app
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="YT TL;DR",  # Updated App Name
        brand_href="#",
        color="warning",  # Bootstrap 'warning' color is a warm yellowish tone
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Settings", href="#", id="settings-link")),
        ],
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Settings")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Ollama API URL", html_for="ollama-api-url-input"),
                        dbc.Input(
                            id="ollama-api-url-input",
                            type="url",
                            placeholder="http://localhost:11434",
                            value="http://localhost:11434",  # Updated default
                        ),
                        dbc.FormText("Enter the URL where your Ollama instance is running."),
                    ], width=12),
                ]),
                dbc.Button("Check Connectivity", id="check-ollama-connection", color="secondary", className="mt-2"),
                html.Div(id="ollama-connection-status", className="mt-2"),
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-settings", className="ml-auto")
            ),
        ],
        id="settings-modal",
        is_open=False,
    ),
    dbc.Row([
        dbc.Col([
            html.H1("YouTube TL;DR"),  # Updated App Name in the Body
            html.P("Only interested in the gist of the video and no time to watch? Use Youtube TL;DR to get the summary ;-)"),
            dbc.Input(
                id="youtube-url-input",
                placeholder="Enter YouTube URL or Video ID",
                type="text",
            ),
            dbc.Button("Search for Video", id="submit-button", color="primary", className="mt-2"),
            html.Div(id="error-message", className="text-danger mt-2"),
            html.Hr(),
            html.Div(id="video-metadata", className="mt-2"),
            # Language Selection Dropdown
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select Language"),
                    dcc.Dropdown(
                        id="language-dropdown",
                        options=[],  # To be populated dynamically
                        value=None,
                        placeholder="Select a language",
                    ),
                ], width=12),
            ], className="mt-2"),
            dbc.Button("Generate Summary", id="generate-summary-button", color="success", className="mt-2 ml-2", disabled=True),
            html.Hr(),
            dcc.Loading(
                id="loading-output",
                type="default",  # Default spinner type
                children=html.Div(
                    id="shared-results",
                    className="mt-2",
                    style={
                        "border": "2px solid #ddd",  # Light grey border
                        "borderRadius": "10px",     # Rounded corners
                        "padding": "15px",          # Padding inside the box
                        "backgroundColor": "#FFF8DC",  # Light cream background
                        "minHeight": "100px",       # Ensure it is visible by default
                    },
                ),
            )

                    ], width=6)
                ], justify="center"),
                # Hidden store components to keep settings and selected language
                dcc.Store(id='ollama-api-url-store', data="http://localhost:11434"),
                dcc.Store(id='selected-language-store', data=None),
            ])


def extract_video_id(input_str):
    """
    Extracts the YouTube video ID from a URL or returns the input if it's already an ID.
    """
    # Regular expression to extract video ID from URL
    regex = (
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    )
    match = re.search(regex, input_str)
    if match:
        return match.group(1)
    elif re.match(r'^[0-9A-Za-z_-]{11}$', input_str):
        return input_str
    else:
        return None


@app.callback(
    [
        Output("error-message", "children"),
        Output("video-metadata", "children"),
        Output("language-dropdown", "options"),
        Output("language-dropdown", "value"),
        Output("generate-summary-button", "disabled"),
    ],
    [Input("submit-button", "n_clicks")],
    [State("youtube-url-input", "value")],
)
def fetch_video_metadata(n_clicks, input_value):
    if not n_clicks:
        return "", "", [], None, True

    video_id = extract_video_id(input_value)
    if not video_id:
        return "Invalid YouTube URL or Video ID.", "", [], None, True

    try:
        response = requests.get(f"{BACKEND_API_URL}/video_metadata/{video_id}")
        if response.status_code == 200:
            data = response.json()
            metadata_items = [
                html.Img(src=data["thumbnail_url"], style={"maxWidth": "100%", "borderRadius": "10px"}),
                html.H4(data["title"]),
            ]
            if data.get("upload_date"):
                metadata_items.append(html.P(f"Uploaded on: {data['upload_date']}"))
            else:
                metadata_items.append(html.P("Upload date not available."))
            metadata_div = html.Div(metadata_items, style={"backgroundColor": "#F5DEB3", "padding": "15px", "borderRadius": "10px"})
    
            # Prepare language options
            languages = data.get("supported_languages", [])
            language_options = [{"label": lang["name"], "value": lang["code"]} for lang in languages]
    
            # Default to first language if not previously selected
            default_language = languages[0]["code"] if languages else None
    
            return "", metadata_div, language_options, default_language, False
        elif response.status_code == 404:
            return "Video not found.", "", [], None, True
        else:
            return f"Error fetching metadata: {response.json().get('detail', 'Unknown error')}", "", [], None, True
    except Exception as e:
        return f"Error connecting to backend: {e}", "", [], None, True


@app.callback(
    Output('selected-language-store', 'data'),
    [Input('language-dropdown', 'value')]
)
def store_selected_language(selected_language):
    return selected_language


@app.callback(
    Output('ollama-api-url-store', 'data'),
    [Input('ollama-api-url-input', 'value')]
)
def store_ollama_api_url(ollama_api_url):
    return ollama_api_url


@app.callback(
    Output('settings-modal', 'is_open'),
    [Input("settings-link", "n_clicks"), Input("close-settings", "n_clicks")],
    [State("settings-modal", "is_open")],
)
def toggle_settings_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("ollama-connection-status", "children"),
    [Input("check-ollama-connection", "n_clicks")],
    [State("ollama-api-url-input", "value")],
)
def check_ollama_connection(n_clicks, ollama_api_url):
    if not n_clicks:
        return ""
    try:
        response = requests.get(f"{ollama_api_url}/health")  # Assuming Ollama has a health endpoint
        if response.status_code == 200:
            return dbc.Alert("Connected to Ollama API successfully.", color="success")
        else:
            return dbc.Alert(f"Failed to connect to Ollama API. Status Code: {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Error connecting to Ollama API: {e}", color="danger")

@app.callback(
    Output("shared-results", "children"),  # Changed to update the children of shared-results
    [
        Input("generate-summary-button", "n_clicks"),
    ],
    [
        State("youtube-url-input", "value"),
        State("selected-language-store", "data"),
        State("ollama-api-url-store", "data"),
    ]
)
def update_output(summary_click, input_value, language, ollama_api_url):
    ctx = callback_context

    if not ctx.triggered:
        return html.Pre(
            "No results yet.",
            style={"whiteSpace": "pre-wrap"},
        )

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    video_id = extract_video_id(input_value)
    if not video_id:
        return html.Pre(
            "**Error:** Invalid Video ID.",
            style={"color": "red", "whiteSpace": "pre-wrap"},
        )

    if triggered_id == "generate-summary-button" and summary_click:
        try:
            headers = {}
            if ollama_api_url:
                headers["X-Ollama-API-URL"] = ollama_api_url
            response = requests.get(
                f"{BACKEND_API_URL}/video_summary/{video_id}",
                params={"language": language},
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "No summary available.")
                return html.Pre(
                    summary,
                    style={"whiteSpace": "pre-wrap"},
                )
            else:
                return html.Pre(
                    f"**Error generating summary:** {response.json().get('detail', 'Unknown error')}",
                    style={"color": "red", "whiteSpace": "pre-wrap"},
                )
        except Exception as e:
            return html.Pre(
                f"**Error connecting to backend:** {e}",
                style={"color": "red", "whiteSpace": "pre-wrap"},
            )

    return html.Pre(
        "No results available.",
        style={"whiteSpace": "pre-wrap"},
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)