from selenium.webdriver.common.by import By

class NbaStats:
    def __init__(self, web_driver):
        self.web_driver = web_driver


    def get_stats(self):
        """Collects advanced stats for the last 10 games for all teams from NBA.com
        returns:
            dict[dict]: Returns a nested dictionary where the parent dict key is the team name and the
                keys for the child dict are the different stats
        """
        stats_url = 'https://www.nba.com/stats/teams/advanced?PerMode=PerGame&LastNGames=10'
        heading_selector = '.Crom_container__C45Ti.crom-container .Crom_table__p1iZz .Crom_headers__mzI_m th'
        row_selector = '.Crom_body__UYOcU tr'
        value_selector = 'td'

        self.web_driver.get(stats_url)

        # extract table headings
        heading_els = self.web_driver.find_elements(By.CSS_SELECTOR, heading_selector)
        row_els = self.web_driver.find_elements(By.CSS_SELECTOR, row_selector)

        headings = []
        for el in heading_els:
            text = el.text.lower().replace('\n', '_')
            headings.append(text)

        # extract team stats
        stats = {}
        for el in row_els:
            value_els = el.find_elements(By.CSS_SELECTOR, value_selector)
            team_name = value_els[1].text.split(' ')[-1].lower()

            stats[team_name] = {}
            for i in range(6, len(value_els) - 1):  # Skip unneeded columns
                stats[team_name][headings[i]] = value_els[i].text

        return stats