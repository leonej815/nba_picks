from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class BrStats:
    TEAM_SYMBOL_TO_NAME = {
        'atl': 'hawks', 'bos': 'celtics', 'brk': 'nets', 'cho': 'hornets', 'chi': 'bulls', 'cle': 'cavaliers', 
        'dal': 'mavericks', 'den': 'nuggets', 'det': 'pistons', 'gsw': 'warriors', 'hou': 'rockets', 
        'ind': 'pacers', 'lac': 'clippers', 'lal': 'lakers', 'mem': 'grizzlies', 'mia': 'heat', 
        'mil': 'bucks', 'min': 'timberwolves', 'nop': 'pelicans', 'nyk': 'knicks', 'okc': 'thunder', 
        'orl': 'magic', 'phi': '76ers', 'pho': 'suns', 'por': 'blazers', 'sac': 'kings', 'sas': 'spurs', 
        'tor': 'raptors', 'uta': 'jazz', 'was': 'wizards'
    }
    BR_TO_NBADOTCOM_STAT_SYMBOLS = {
        'ortg': 'offrtg', 'drtg': 'defrtg', 'trb%': 'reb_percent', 'tov%': 'tov_percent', 
        'ts%': 'ts_percent', 'pace': 'pace'
    }


    def __init__(self, web_driver):
        self.web_driver = web_driver


    def get_stats(self):
        """Collects advanced stats for the last 10 games for all teams from NBA.com
        returns:
            dict(str, dict(str, str)): Returns a nested dictionary where the parent dict keys are the team names and the keys the child dict conatins the different stat names mapped to their values
        """

        for team_symbol in self.TEAM_SYMBOL_TO_NAME.keys():
            stats_url = f'https://www.basketball-reference.com/teams/{team_symbol}/2027/gamelog-advanced/'
            heading_selector = '#team_game_log_adv_reg thead tr:nth-child(2) th'
            row_selector = '#team_game_log_adv_reg tbody tr'
            value_selector = 'td'

            # wait for table element to exist
            self.web_driver.get(stats_url)
            WebDriverWait(self.web_driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#team_game_log_adv_reg"))
            )
            time.sleep(5)

            # get table body row elements
            row_els = self.web_driver.find_elements(By.CSS_SELECTOR, row_selector)

            # remove extra label row
            game_rows = []
            for row_el in row_els:
                if row_el.text[0].isdigit() == False:
                    continue
                game_rows.append(row_el)
            
            for row in game_rows:
                print(row.text)
            exit()

        # extract table headings
        heading_els = self.web_driver.find_elements(By.CSS_SELECTOR, heading_selector)
        headings = []
        for el in heading_els:
            text = el.text.lower().replace('\n', '_').strip()
            if text == '':
                continue
            headings.append(text)        



        # extract team stats
        stats = {}
        for el in row_els:
            value_els = el.find_elements(By.CSS_SELECTOR, value_selector)[1:] # remove first element of row
            team_name = value_els[0].text.split(' ')[-1].lower()

            stats[team_name] = {}
            for i in range(5, len(value_els) - 1):  # skip unneeded columns
                stats[team_name][headings[i]] = value_els[i].text

        return stats