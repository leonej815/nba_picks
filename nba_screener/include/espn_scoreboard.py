from selenium.webdriver.common.by import By

class EspnScoreboard:
    """Class to manage the retrieval of data from the NBA scoreboard page at espn.com
    Attributes:
        TEAM_NAME_TO_SYMBOL (dict(str, str)): keys are team names and values are team abbreviations
        MIN_GAME_COUNT (int): this is set to 10 since this program uses a rolling 10 game window of previous game stats
        MAX_GAME_COUNT (int): this is set to 81 to avoid collecting data for playoff games
        web_driver: selenium web driver object
    """

    TEAM_NAME_TO_SYMBOL = {
        'celtics':'bos', 'warriors':'gs', 'cavaliers':'cle', 'grizzlies':'mem', 'nets':'bkn', 'lakers':'lal',
        'hawks':'atl', 'kings':'sac', 'bulls':'chi', 'nuggets':'den', 'magic':'orl', 'thunder':'okc',
        'bucks':'mil', 'suns':'phx', 'mavericks':'dal', 'wizards':'wsh', 'knicks':'ny', 'hornets':'cha',
        'raptors':'tor', 'timberwolves':'min', 'clippers':'lac', '76ers':'phi', 'rockets':'hou', 'pacers':'ind',
        'pelicans':'no', 'blazers':'por', 'pistons':'det', 'spurs':'sa', 'heat':'mia', 'jazz':'utah'
    }
    MIN_GAME_COUNT = 10
    MAX_GAME_COUNT = 81
            
    def __init__(self, web_driver):
        """Creates web_driver attribute
        Inputs:
            selenium web driver object
        """

        self.web_driver = web_driver


    def open_scoreboard(self, date):
        """Uses webdriver to open the Espn NBA scoredboard page at given date
        Inputs:
            date (str): date string in the format yyyymmdd
        """

        url = f"https://www.espn.com/nba/scoreboard/_/date/{date}"
        self.web_driver.get(url)


    def get_scores(self, date):
        """Uses selenium web driver to open the NBA scoreboard at the given date and collect all the scores and store them in a list
        Inputs:
            date (str): date string with format yyyymmdd
        Outputs:
            list[dict(str, str)]: list containing dictionaries of score data with keys away, home, away_score, home_score
        """

        team_selector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        score_selector = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        scoreboard_selector = '.Scoreboard__RowContainer'
        progress_selector = '.ScoreCell__Time'

        self.open_scoreboard(date)

        scoreboard_els = self.driver.find_elements(By.CSS_SELECTOR, scoreboard_selector)

        score_data = []
        for scoreboard_el in scoreboard_els:
            # skip games that aren't finished yet
            game_progress = scoreboard_el.find_element(By.CSS_SELECTOR, progress_selector).text.split("/")[0].lower()
            if game_progress != "final":
                continue

            # extract team names and scores
            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            score_els = scoreboard_el.find_elements(By.CSS_SELECTOR, score_selector)
            away_score = score_els[0].text
            home_score = score_els[1].text

            # compile score data
            game_data = {
                'away': away_team,
                'home': home_team,
                'away_score': away_score,
                'home_score': home_score
            }
            score_data.append(game_data)

        return score_data


    def get_line_data(self, date):
        """Uses selenium web driver to open the NBA scoreboard at the given date and collect line data and store it in a list
        Inputs:
            date (str): date string with format yyyymmdd
        Outputs:
            list[dict(str, str)]: list containing dictionaries of score data with keys away, home, away_spread, home_spread, total_line
        """

        scoreboard_selector = '.Scoreboard__RowContainer'
        team_selector = '.ScoreCell__TeamName.ScoreCell__TeamName--shortDisplayName'
        line_selector = '.rIczU.iygLn'
        record_selector = '.ScoreboardScoreCell__Record'

        self.open_scoreboard(date)
        scoreboard_els = self.web_driver.find_elements(By.CSS_SELECTOR, scoreboard_selector)

        game_data_arr = []
        for scoreboard_el in scoreboard_els:
            # skip games with fewer than 10 games played by either team
            record_els = scoreboard_el.find_elements(By.CSS_SELECTOR, record_selector)
            away_game_count = sum([int(x) for x in record_els[0].text.split('-')])
            home_game_count = sum([int(x) for x in record_els[2].text.split('-')])
            if away_game_count < self.MIN_GAME_COUNT or home_game_count < self.MIN_GAME_COUNT:
                print('Not enough games played')
                continue
            if away_game_count > self.MAX_GAME_COUNT and home_game_count > self.MAX_GAME_COUNT:
                print('Regular season is over')
                continue           

            # extract team names
            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            # skip games with no betting lines
            line_els = scoreboard_el.find_elements(By.CSS_SELECTOR, line_selector)
            if not line_els:
                print(f'Couldn\'t find lines for {away_team} at {home_team}')
                continue        

            # extract betting line data
            favored_team_symbol = line_els[0].text.split(' ')[0].lower()
            spread = line_els[0].text.split(' ')[-1]
            total = line_els[1].text

            # determine spread for home and away teams
            home_spread = spread if favored_team_symbol == self.TEAM_NAME_TO_SYMBOL[home_team] else str(float(spread) * -1)

            # compile game data
            game_data = {
                'away': away_team,
                'home': home_team,
                'away_spread': str(float(home_spread) * -1),
                'home_spread': home_spread,
                'total_line': total
            }
            game_data_arr.append(game_data)

        return game_data_arr  


        
