import sqlite3
from pathlib import Path
import os

def main():
    # get db path depending on environment
    if os.getenv("APP_ENV") == "development":
        db_path = Path(__file__).resolve().parent.parent / "sqlite" / "data_test.sqlite"
    else:
        db_path = Path(__file__).resolve().parent.parent / "sqlite" / "data.sqlite"

    # make directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS nba_game_data(
                    date INTEGER, 
                    away TEXT, 
                    home TEXT, 
                    away_spread REAL, 
                    home_spread REAL, 
                    total_line REAL, 
                    away_score INTEGER, 
                    home_score INTEGER, 
                    away_offrtg REAL, 
                    away_defrtg REAL, 
                    away_reb_percent REAL, 
                    away_tov_percent REAL, 
                    away_ts_percent REAL, 
                    away_pace REAL, 
                    away_pie REAL, 
                    home_offrtg REAL, 
                    home_defrtg REAL, 
                    home_reb_percent REAL, 
                    home_tov_percent REAL, 
                    home_ts_percent REAL, 
                    home_pace REAL, 
                    home_pie REAL, 
                    UNIQUE(date, away, home)
                )
            ''')
            conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    main()