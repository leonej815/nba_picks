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
    """This is a data pipeline that collects and updates scores for previous days, and collects line data and stats for the current day if needed. The database is updated with any changes and a csv file is created"""

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
    print(f"Line data:\n{line_data}\n")
    db.insert_line_data(date_today, line_data)
    
    # get stats and update records that need stats for today's date
    stats_dict = nbaDotCom.get_stats()
    print(f"Stats:\n{stats_dict}\n")
    db.insert_stats(date_today, stats_dict)
    
    # select all data and output to csv
    df = db.select_all_to_df()
    df.to_csv(csv_path, index=False)


# def get_webdriver():
#     options = Options()
#     options.add_argument("--headless=new") # modern headless mode
#     options.add_argument("--disable-gpu") # in case Github Actions Linux machines don't have a GPU
#     options.add_argument("--no-sandbox") # essential for server environments
#     options.add_argument("--disable-dev-shm-usage") # overcomes limited resource errors
#     options.add_argument("--window-size=1920,1080") # ensures responsive sites load correctly
    
#     # crucial flags to prevent Cloudflare/bot detection in headless mode:
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
#     driver = webdriver.Chrome(options=options)
#     return driver

def get_webdriver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Critical flags to prevent bot detection in headless mode:
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    # Hide automation indicators
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    # Execute CDP command to further mask automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
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