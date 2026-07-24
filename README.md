# Value Stocks
This project is a DASH web app that scrapes NBA stats, scores and lines from the web and uses a model to predict what side to pick against the spread for regular season NBA games.

## Core Functionality
* create_model.py uses the stored data in the database to create a binary classification model to pick NBA games against the spread.
* run_daily.py runs nba_screener every morning to collect the stats and update the scores of NBA games. The stats are based on the previous 10 games played.
* app.py is the web application file. It loads the model and the games for the current data and displays the models pick and confidence level at various lines in case the line moves.

## Deployment
* The app is currently hosted at https://nba-picks-4r5x.onrender.com
* Automated Data Pipeline: A GitHub Actions workflow is configured to trigger run_daily.py every morning. The screener gets lines and stats for the current days games and updates the scores for any previous days where they are needed. The data is stored in the sqlite database.

## Tech Stack
* Frontend: Dash, Dash Bootstrap Components, HTML/CSS
* Backend: Python 3.11
* Database: SQLite3
* Data Sources: espn.com and nba.com
* Automation: GitHub Actions, Render (Web Service)

## Project Structure
```text
Value-Stocks/
├── app.py              # Dash application and UI layout
├── data_manager.py     # SQL logic and data transformation
├── include/            # contains class to manage database interactions
├── nba_screener/       # web scraper and data pipeline
├── model/              # model file and model features file
├── scripts/            # scripts to create database, and to create model
├── sqlite/             # SQLite database storage
├── csv/                # database data in csv form
├── .github/            # Contains the yaml file for github action that runs the web scraper
├── assets/             # favicon
└── requirements.txt    # Project dependencies
```