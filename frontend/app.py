import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import requests
import re

# Initialize the Dash app with Bootstrap theme for better styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
            dbc.Button("Submit", id="submit-button", color="primary", className="mt-2"),
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
            dbc.Button("Get Transcript", id="get-transcript-button", color="info", className="mt-2", disabled=True),
            dbc.Button("Generate Summary", id="generate-summary-button", color="success", className="mt-2 ml-2", disabled=True),
            html.Hr(),
            dcc.Loading(
                id="loading-output",
                type="default",
                children=html.Div([
                    dcc.Tabs(id='output-tabs', value='transcript-tab', children=[
                        dcc.Tab(label='Transcript', value='transcript-tab'),
                        dcc.Tab(label='Summary', value='summary-tab'),
                    ]),
                    html.Div(id='tab-content', className="mt-2")
                ])
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
        Output("get-transcript-button", "disabled"),
        Output("generate-summary-button", "disabled"),
    ],
    [Input("submit-button", "n_clicks")],
    [State("youtube-url-input", "value")],
)
def fetch_video_metadata(n_clicks, input_value):
    if not n_clicks:
        return "", "", [], None, True, True

    video_id = extract_video_id(input_value)
    if not video_id:
        return "Invalid YouTube URL or Video ID.", "", [], None, True, True

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
    
            return "", metadata_div, language_options, default_language, False, False
        elif response.status_code == 404:
            return "Video not found.", "", [], None, True, True
        else:
            return f"Error fetching metadata: {response.json().get('detail', 'Unknown error')}", "", [], None, True, True
    except Exception as e:
        return f"Error connecting to backend: {e}", "", [], None, True, True


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
    Output("tab-content", "children"),
    [
        Input('output-tabs', 'value'),
        Input('get-transcript-button', 'n_clicks'),
        Input('generate-summary-button', 'n_clicks')
    ],
    [
        State('youtube-url-input', 'value'),
        State('selected-language-store', 'data'),
        State('ollama-api-url-store', 'data')
    ]
)
def update_output(tab, transcript_click, summary_click, input_value, language, ollama_api_url):
    ctx = callback_context

    if not ctx.triggered:
        return ""

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    video_id = extract_video_id(input_value)
    if not video_id:
        return dbc.Alert("Invalid Video ID.", color="danger")

    if triggered_id == "get-transcript-button" and transcript_click:
        try:
            response = requests.get(
                f"{BACKEND_API_URL}/video_transcripts/{video_id}",
                params={"language": language}
            )
            if response.status_code == 200:
                transcript = response.text
                if tab == 'transcript-tab':
                    return html.Pre(transcript, style={"whiteSpace": "pre-wrap", "backgroundColor": "#FFF8DC", "padding": "15px", "borderRadius": "10px"})
                elif tab == 'summary-tab':
                    return dash.no_update
            else:
                return dbc.Alert(f"Error fetching transcript: {response.json().get('detail', 'Unknown error')}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Error connecting to backend: {e}", color="danger")

    elif triggered_id == "generate-summary-button" and summary_click:
        try:
            headers = {}
            if ollama_api_url:
                headers["X-Ollama-API-URL"] = ollama_api_url
            response = requests.get(
                f"{BACKEND_API_URL}/video_summary/{video_id}",
                params={"language": language},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "No summary available.")
                if tab == 'summary-tab':
                    return html.Pre(summary, style={"whiteSpace": "pre-wrap", "backgroundColor": "#FFF8DC", "padding": "15px", "borderRadius": "10px"})
                elif tab == 'transcript-tab':
                    return dash.no_update
            else:
                return dbc.Alert(f"Error generating summary: {response.json().get('detail', 'Unknown error')}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Error connecting to backend: {e}", color="danger")

    return ""


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)