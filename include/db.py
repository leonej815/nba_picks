import sqlite3
import pandas as pd

class DB:
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_write(self, query, params=()):
        """Internal helper that handles write queries
        returns:
            cursor object after execution
        """
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query, params)
    
    def execute_fetch(self, query, params=()):
        """Helper function for SELECT queries
        returns:
            list[tuple]: list of tuples where each tuple is a row in the database
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            return cursor.execute(query, params).fetchall()

    def get_dates_that_need_scores(self):
        """returns a list of dates where there are game records without the final score added"""
        sql = "SELECT DISTINCT date FROM nba_game_data WHERE away_score IS NULL"
        rows = self.execute_fetch(sql)
        return [str(row[0]) for row in rows]
    
    def update_scores(self, date, game_scores_list):
        """Inputs scores in database for given date
        inputs:
            string date: a date string in the format yyyymmdd
            list[dict] games_scores_list: keys for dicts are away_score, home_score, away, home
        """
        for game_score_dict in game_scores_list:
            sql = "UPDATE nba_game_data SET away_score=?, home_score=? WHERE away=? AND home=? AND date=?"
            vals = (game_score_dict["away_score"], game_score_dict["home_score"], game_score_dict["away"], game_score_dict["home"], date)
            self.execute_write(sql, vals)

    def insert_line_data(self, date, line_data_list):
        """Creates a new game record with date, away team, home team, away spread, home spread, and total line
        if the record doesn't exist and if it exists already update the lines for the record.
        inputs:
            string date: a date string in the format yyyymmdd
            list[dict] line_data_list: contains the data to be inserted
        """
        for line_data in line_data_list:
            sql = """
                INSERT INTO nba_game_data(date, away, home, away_spread, home_spread, total_line)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, away, home)
                DO UPDATE SET
                    away_spread = excluded.away_spread,
                    home_spread = excluded.home_spread,
                    total_line = excluded.total_line
            """
            vals = (date, line_data["away"], line_data["home"], line_data["away_spread"], line_data["home_spread"], line_data["total_line"])
            self.execute_write(sql, vals)

    def insert_stats(self, date, stats):
        """Insert stats for records with the given date and that don't already have stats
        inputs:
            string date: date string in the format yyyymmdd
            dict[dict]: a nested dictionary where the parent dict key is the team name and the
                keys for the child dict are the different stats
        """
        records_that_need_stats = self.select_records_that_need_stats(date)
        for row in records_that_need_stats:
            away = row[0]
            home = row[1]
            sql = """
                UPDATE nba_game_data
                SET away_offrtg=?, away_defrtg=?, away_reb_percent=?, away_tov_percent=?, 
                    away_ts_percent=?, away_pace=?, away_pie=?, 
                    home_offrtg=?, home_defrtg=?, home_reb_percent=?, home_tov_percent=?, 
                    home_ts_percent=?, home_pace=?, home_pie=?
                WHERE date=? AND away=? AND home=?
            """
            vals = (                    
                stats[away]['offrtg'], stats[away]['defrtg'], stats[away]['reb%'], stats[away]['tov%'], 
                stats[away]['ts%'], stats[away]['pace'], stats[away]['pie'], 
                stats[home]['offrtg'], stats[home]['defrtg'], stats[home]['reb%'], stats[home]['tov%'], 
                stats[home]['ts%'], stats[home]['pace'], stats[home]['pie'],
                date, away, home 
            )
            self.execute_write(sql, vals)

    def select_records_that_need_stats(self, date):
        """Returns the teams of the records where stats are needed for the given date
        Input:
            string date: date string in the format yyyymmdd
        Returns:
            list[tuple]: a list of tuples where the away team is index 0 and the home team is index 1
        """
        sql = "SELECT away, home FROM nba_game_data WHERE date=? AND away_offrtg IS NULL"
        vals = (date,)
        return self.execute_fetch(sql, vals)
    
    def select_by_date_to_df(self, date):
        """Selects data from records with the given date and return the result in a dataframe
        Inputs:
            string date: date string in the format yyyymmdd
        Returns:
            dataframe
        """
        sql = """
            SELECT
                away, home, away_spread, home_spread, away_score, home_score, 
                away_offrtg, away_defrtg, home_offrtg, home_defrtg, 
                away_pace, home_pace, away_pie, home_pie
            FROM nba_game_data
            WHERE date=?
        """
        with sqlite3.connect(self.db_path) as conn:
            vals = (date,)
            return pd.read_sql_query(sql, conn, params=vals)

    def select_all_to_df(self):
        """Selects all data from the database and stores the result in a dataframe
        Returns:
            dataframe
        """
        with sqlite3.connect(self.db_path) as conn:
            sql = "SELECT * from nba_game_data"
            return pd.read_sql_query(sql, conn)