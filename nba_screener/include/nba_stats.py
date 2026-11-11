# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# class NbaStats:
#     """Class that manages NBA team stats collecting from nba.com
#     Attributes:
#         web_driver: selenium web driver object
#     """

#     def __init__(self, web_driver):
#         self.web_driver = web_driver


#     def get_stats(self):
#         """Collects advanced stats for the last 10 games for all teams from NBA.com
#         returns:
#             dict(str, dict(str, str)): Returns a nested dictionary where the parent dict keys are the team names and the keys the child dict conatins the different stat names mapped to their values
#         """
#         stats_url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'
#         heading_selector = 'div.crom-container table thead tr th'
#         row_selector = 'div.crom-container table tbody tr'
#         value_selector = 'td'

#         # wait for table element to exist
#         self.web_driver.get(stats_url)
#         WebDriverWait(self.web_driver, 15).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
#         )
#         time.sleep(30)

#         # extract table headings
#         heading_els = self.web_driver.find_elements(By.CSS_SELECTOR, heading_selector)
#         headings = []
#         for el in heading_els:
#             text = el.text.lower().replace('\n', '_').strip()
#             if text == '':
#                 continue
#             headings.append(text)        

#         # get table body row elements
#         row_els = self.web_driver.find_elements(By.CSS_SELECTOR, row_selector)

#         # extract team stats
#         stats = {}
#         for el in row_els:
#             value_els = el.find_elements(By.CSS_SELECTOR, value_selector)[1:] # remove first element of row
#             team_name = value_els[0].text.split(' ')[-1].lower()

#             stats[team_name] = {}
#             for i in range(5, len(value_els) - 1):  # skip unneeded columns
#                 stats[team_name][headings[i]] = value_els[i].text

#         return stats

import requests

class NbaStats:
    """Class that manages NBA team stats collecting from NBA.com via direct API"""

    def __init__(self, web_driver=None):
        self.web_driver = web_driver

    def get_stats(self):
        """Fetches advanced stats for the last 10 games directly from the NBA stats API."""
        api_url = (
            "https://stats.nba.com/stats/leaguedashteamstats?"
            "Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment="
            "&LastNGames=10&LeagueID=00&Location=&MeasureType=Advanced&Month=0"
            "&OpponentTeamID=0&Outcome=&PORound=0&PacePer=Per48&PerMode=PerGame"
            "&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=Rank&Rank=NO"
            "&Season=2026-27&SeasonSegment=&SeasonType=Regular%20Season"
            "&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision="
        )

        # Full browser header profile to prevent connection drops/rate limiting
        headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }

        stats_dict = {}
        try:
            print("Fetching NBA advanced stats via direct API...")
            # Increased timeout to 45 seconds to handle cloud runner latency
            response = requests.get(api_url, headers=headers, timeout=45)
            
            if response.status_code != 200:
                print(f"API request failed with status code {response.status_code}")
                return {}

            data = response.json()
            result_sets = data.get('resultSets', [])
            if not result_sets:
                return {}

            headers_list = result_sets[0].get('headers', [])
            row_set = result_sets[0].get('rowSet', [])

            lower_headers = [h.lower() for h in headers_list]
            team_idx = lower_headers.index('team_name')

            for row in row_set:
                full_team_name = str(row[team_idx])
                team_name = full_team_name.split(' ')[-1].lower()

                team_stats = {}
                for i, header in enumerate(lower_headers):
                    if i == team_idx:
                        continue
                    clean_key = header.replace('_rating', 'rtg').replace('_', '')
                    team_stats[clean_key] = str(row[i])

                stats_dict[team_name] = team_stats

            print(f"Successfully loaded stats for {len(stats_dict)} teams.")

        except Exception as e:
            print(f"ERROR fetching NBA stats via API: {e}")

        return stats_dict