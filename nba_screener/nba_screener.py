from include.espn_scoreboard import EspnScoreboard
from include.nba_stats import NbaStats
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import os
from dotenv import load_dotenv
load_dotenv()

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from include.db import DB

def nba_screener():
    if os.getenv("APP_ENV") == "development":
        db_name = "data_test.sqlite"
        csv_name = "data_test.csv"
    else:
        db_name = "data.sqlite"
        csv_name = "data.csv"
    db_path = Path(__file__).resolve().parent.parent/'sqlite'/db_name
    csv_path = Path(__file__).resolve().parent.parent/'csv'/csv_name
    date_today = get_date_str()
    # date_today = "20260224" # COMMENT OUT, JUST TESTING
    webdriver = get_webdriver()
    db = DB(db_path)
    espn = EspnScoreboard(webdriver)
    nbaDotCom = NbaStats(webdriver)

    # get list of dates that have games that need the scores filled in and add scores
    dates_that_need_scores = db.get_dates_that_need_scores()
    for date in dates_that_need_scores:
        scores_data_list = espn.get_scores(dates_that_need_scores)
        db.update_scores(date, scores_data_list)

    # retrieve today's line data and either insert or update into the database
    line_data = espn.get_line_data(date_today)
    db.insert_line_data(date_today, line_data)

    # get stats and update records that need stats for today's date
    stats_dict = nbaDotCom.get_stats()
    db.insert_stats(date_today, stats_dict)

    # select all data and output to csv
    df = db.select_all_to_df()
    df.to_csv(csv_path, index=False)


def get_webdriver():
    """Returns headless selenium webdriver object"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox") # Essential for server environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource errors
    chrome_options.add_argument("--window-size=1920,1080")  # Ensures responsive sites load correctly
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_date_str():
    """Returns the current date or the previous date if it is before 4 am because games might be going on past midnight. Uses EST time zone.
    returns:
        str: the date in the format yyyymmdd
    """
    tz = ZoneInfo('US/Eastern')
    today = datetime.now(tz)
    if today.hour < 4:
        today = today - timedelta(days=1)
    return today.strftime('%Y%m%d')


if __name__ == "__main__":
    nba_screener()