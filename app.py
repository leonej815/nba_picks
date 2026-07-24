from include.db import DB
import dash
import joblib
import pandas as pd
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


# get db path and create db class instance
if os.getenv("APP_ENV") == "development":
    db_name = "data_test.sqlite"
else:
    db_name = "data.sqlite"
db_path = Path(__file__).resolve().parent/'sqlite'/db_name
db = DB(db_path)

# get today's date or yesterday's date string if it is before 8 am
tz = ZoneInfo('US/Eastern')
today = datetime.now(tz)
if today.hour < 8:
    today = today - timedelta(days=1)
date_string = today.strftime('%Y%m%d')
# date_string = "20260222" # FOR TESTING

# load model
model = joblib.load("model/nba_spread_model.joblib")
model_features = joblib.load("model/nba_spread_features.joblib")

# create app with Cyborg theme and Bootstrap
app = dash.Dash(__name__, title="NBA Spread Picks", external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

# app layout
app.layout = dbc.Container([
    # page identifier
    dcc.Location(id="url", refresh=False),

    html.H4("NBA Spread Picks", className="text-primary mb-3", style={"paddingTop": "10px"}),
     
    # container to be filled with rows of game data with callback function
    html.Div(id="rows_container")
])
    

@app.callback(Output("rows_container", "children"), Input("url", "pathname"))
def render_list(_):
    """This function creates components that go into the children propery of the rows_cointainer component. 
    Whenever the component with id "url" has its pathname property changes this function is run. 
    It goes through the list of game data and creates rows with the game info and picks using the prediction model.
    """

    # dataframe containing teams, stats, and lines
    games_df = db.select_by_date_to_df(date_string)

    # these are the offsets to apply to the home spread line
    spread_shifts = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]

    # list to hold the dash elements for each game
    game_rows = []

    for _, game in games_df.iterrows():
        # stores the Dash elements for each spread shift
        shift_elements = []

        # loop through spread shifts and find the predictions and make Dash elements
        for shift in spread_shifts:
            # copy the features and shift the home spread in the copy
            modified_features = game[model_features].copy()
            test_spread = game["home_spread"] + shift
            modified_features["home_spread"] = test_spread

            # format modified features into a 1-row dataframe for the model
            input_df = pd.DataFrame([modified_features])[model_features]

            # use the model to get the prediction, the probabilities, and the max probability
            prediction = model.predict(input_df)[0]
            probabilities = model.predict_proba(input_df)[0]
            max_probability = probabilities.max()
            
            # get the pick and spread to display for the given prediction
            if prediction == 1:
                pick_name = game["home"]
                display_spread = test_spread
                display_spread = f"{test_spread:+.1f}"
            else:
                pick_name = game["away"]
                display_spread = -test_spread
                display_spread = f"{-test_spread:+.1f}"
            if test_spread == 0:
                display_spread = "PK"

            if max_probability >= 0.55:        
                badge_color = "success"
            else:
                badge_color = "secondary"

            # Create a nice badge for this specific shift value
            shift_elements.append(
                dbc.Badge(
                    f"{display_spread}: {pick_name.capitalize()} ({max_probability:.1%})",
                    color=badge_color,
                    className="me-1 mb-1 p-2"
                )
            )

        # Build the card for this game containing all shift badges
        game_rows.append(
            dbc.Card([
                dbc.CardBody([
                    html.H5(f"{game['away'].capitalize()} at {game['home'].capitalize()}", className="card-title text-info"),
                    html.Div(shift_elements, className="d-flex flex-wrap")
                ])
            ], className="mb-3 bg-dark border-secondary")
        )

    if len(game_rows) == 0:
        content = dbc.Card([
                dbc.CardBody([
                    html.H5(f"No NBA regular season games today or no picks to show."),
                ])
            ], className="mb-3 bg-dark border-secondary")
    else:
        content = game_rows

    return content

    
if __name__ == "__main__":
    app.run(debug=False)

