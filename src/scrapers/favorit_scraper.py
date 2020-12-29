import os.path
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bet import Bet
from date_time import DateTime
from match import Match
from match_title import MatchTitle
from sport import Sport
from abstract_scraper import AbstractScraper
from constants import SPORT_NAME

tournament_names = None
country_names = None


class FavoritScraper(AbstractScraper):
    _NAME = 'favorit'
    _BASE_URL = 'https://old.favorit.com.ua/en/bets/#'
    _LIVE_URL = 'https://old.favorit.com.ua/en/live/'
    _ICONS = {
        'football': 'Soccer',
        'csgo': 'Cybersports',
        'dota': 'Cybersports',
        'lol': 'Cybersports',
        }
    _SUBMENU = {
        'football': None,
        'csgo': 'Counter-Strike: Global Offensive',
        'dota': 'Dota 2',
        'lol': 'League of Legends'
        }
    _SKIP_TITLES = ['1X2 and Total Goals', '1X2 and Both teams to Score',
                    'Both Teams To Score and Total Goals', 'Correct Score',
                    'Goal method of first goal', '(3way)', 'Winning Margin',
                    'not to lose and Total', 'Goal Range', 'Goal method of first goal',
                    'HT/FT', 'HT or FT and Total Goals', 'Both Teams To Score and Total Goals']

    def get_name(self) -> str:
        return self._NAME

    def get_sport_bets(self, sport_name):
        """
        Scrapes betting data for a given sport type

        :param sport_name: sport type to scrape betting data for
        :type sport_name: str
        """
        sport_bets = []
        subsections = self.get_subsections(sport_name)

        # subsections = [subsections[6]]

        for subsection in subsections:

            print('subsection', subsections.index(subsection) + 1, '/', len(subsections))

            tournaments = self.get_subsection_tournaments(subsection)
            for tournament in tournaments:

                print(' ' * 1, 'tournament', tournaments.index(tournament) + 1, '/', len(tournaments))

                events = self.get_events_from_tournament(tournament)
                for event in events:

                    print(' ' * 4, 'match', events.index(event) + 1, '/', len(events))

                    match_bets = self._get_bets(event)
                    if match_bets:
                        sport_bets.append(match_bets)
                    break
                break
            self.renderer.click(subsection)
            time.sleep(1)

        sport = Sport(sport_name, sport_bets)
        return sport

    def get_match_buttons(self, subsection):
        self.renderer.click(subsection)
        time.sleep(1)
        main_table = self.renderer.find_element_by_class_name('column--container')
        time.sleep(1)
        buttons = main_table.find_elements_by_class_name('event--more')
        return buttons

    @staticmethod
    def get_match_buttons_from_tournament(tournament):
        buttons = tournament.find_elements_by_class_name('event--more')
        return buttons

    @staticmethod
    def get_events_from_tournament(tournament):
        events = tournament.find_elements_by_class_name('event--head-block')
        return events

    def get_events(self, subsection):
        self.renderer.click(subsection)
        time.sleep(1)
        main_table = self.renderer.find_element_by_class_name('column--container')
        time.sleep(1)
        events = main_table.find_elements_by_class_name('event--head-block')
        return events

    def get_subsection_tournaments(self, subsection):
        self.renderer.click(subsection)
        time.sleep(2)
        try:
            tournaments = self.renderer.find_element_by_class_name('sport--list').find_elements_by_class_name(
                'category--block')
        except NoSuchElementException:
            return self.get_subsection_tournaments(subsection)
        if self._ICONS[SPORT_NAME] != 'Cybersports':
            if tournament_names:
                for t in list(tournaments):
                    for name in tournament_names:
                        if name not in t.find_element_by_class_name('category--name').text.lower():
                            tournaments.remove(t)
        return tournaments

    def get_subsections(self, sport_name):
        """
        Scrape match buttons for a given sport type
        """
        self.renderer.get('https://www.google.com/')
        self.renderer.get(self._BASE_URL)
        time.sleep(0.25)

        sports_list = self.renderer.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'sprt')))
        icon = sports_list[0].find_element_by_class_name('sport--name--head')

        for sport in sports_list:
            if sport.find_element_by_class_name('ttt').text == self._ICONS[sport_name]:
                icon = sport.find_element_by_class_name('sport--name--head')
                break

        time.sleep(0.25)
        self.renderer.click(icon)
        time.sleep(0.25)

        drop_down_menu = icon.parent.find_element_by_class_name('slideInDown')
        checkboxes = drop_down_menu.find_elements_by_tag_name('b')
        titles = drop_down_menu.find_elements_by_class_name('ttt')
        print('favorit scraping', len(checkboxes), 'subsections')

        if self._SUBMENU[sport_name]:
            for i in range(len(checkboxes)):
                if titles[i].text == self._SUBMENU[sport_name]:
                    return [checkboxes[i]]

        if self._ICONS[sport_name] != 'Cybersports':
            if country_names:
                for checkbox in list(checkboxes):
                    b = False
                    for country_name in country_names:
                        if country_name in checkbox.find_element_by_xpath('..').text.lower():
                            b = True
                            break
                    if not b:
                        checkboxes.remove(checkbox)

        return checkboxes

    def _get_bets(self, event):
        bets = []
        # time.sleep(0.1)
        match = self._get_match_basic_data(event)
        match_button = event.find_element_by_class_name('event--more')
        self.renderer.click(match_button)
        time.sleep(0.1)

        if int(match_button.text) > 3:  # otherwise no need to click it
            time.sleep(1)
            try:
                element = self.renderer.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
                self.renderer.click(element)
            except Exception:
                pass

        time.sleep(0.5)
        self._parse_marketblocks(bets, match.url)

        match.bets = bets
        return match

    def _parse_marketblocks(self, bets, url):
        soup = self.renderer.soup()
        market_blocks = soup.find_all(class_='markets--block')
        try:
            for mb in market_blocks:
                block_title_head = mb.find(class_='markets--head').text

                b = True
                for s in FavoritScraper._SKIP_TITLES:
                    if s in block_title_head:
                        b = False
                        break
                if not b:
                    # print(block_title_head)
                    continue
                # print(block_title_head)
                sub_block_titles = mb.find_all(class_='result--type--head')
                sub_blocks = mb.find_all(class_='outcome--list')
                for sub_block in sub_blocks:
                    block_title_tail = ' ' + sub_block_titles[sub_blocks.index(sub_block)].find('span').text
                    block_title = block_title_head + block_title_tail
                    block = sub_block

                    if mb.find_all(class_='mtype--7'):
                        break
                    else:
                        labels = block.find_all('label')
                        for label in labels:
                            if label.get('class') == 'outcome--empty':
                                continue
                            bet_type = label.find('span').get('title')
                            bet_title = block_title + ' ' + bet_type
                            button = label.find('button')
                            odds = button.text
                            bet = Bet(bet_title, odds, FavoritScraper._NAME, url)
                            bets.append(bet)
        except StaleElementReferenceException:
            self._parse_marketblocks(bets, url)

    def _parse_live_marketblocks(self, bets, url):
        market_blocks = self.renderer.find_elements_by_class_name('markets--block')
        for mb in market_blocks:
            try:
                block_title_head = mb.find_element_by_class_name('markets--head').get_attribute('innerHTML')

                b = True
                for s in self._SKIP_TITLES:
                    if s in block_title_head:
                        b = False
                        break
                if not b:
                    # print(block_title_head)
                    continue
                print(market_blocks.index(mb))
                sub_block_titles = mb.find_elements_by_class_name('result--type--head')
                sub_blocks = mb.find_elements_by_class_name('outcome--list')
                for sub_block in sub_blocks:
                    block_title_tail = ' ' + sub_block_titles[sub_blocks.index(sub_block)].find_element_by_tag_name(
                        'span').get_attribute('innerHTML')
                    block_title = block_title_head + block_title_tail
                    block = sub_block

                    if mb.find_elements_by_class_name('mtype--7'):
                        break
                    else:
                        labels = block.find_elements_by_tag_name('label')
                        for label in labels:
                            if label.get_attribute('class') == 'outcome--empty':
                                continue
                            bet_type = label.find_element_by_tag_name('span').get_attribute('title')
                            bet_title = block_title + ' ' + bet_type
                            button = label.find_element_by_tag_name('button')
                            odds = button.text
                            bet = Bet(bet_title, odds, self._NAME, url)
                            bets.append(bet)
            except Exception:
                pass
        return bets

    def _get_bets_from_url(self, match_url):
        self.renderer.get(match_url)
        bets = []
        basic_info = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sticky-inner-wrapper')))
        # basic_info = self.renderer.find_element_by_class_name('sticky-inner-wrapper')

        date = basic_info.find_element_by_class_name('event--date--1').text.lower()
        date = self._format_date(date)
        teams = [el.text for el in
                 basic_info.find_element_by_class_name('event--name').find_elements_by_tag_name('span')]
        match = Match(MatchTitle(teams), match_url, date, self)
        element = self.renderer.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'slick-block')))
        element = self.renderer.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
        try:
            self.renderer.click(element)
        except Exception:
            print('ne mogu nazhat na all')

        time.sleep(0.5)
        self._parse_marketblocks(bets, match_url)

        match.bets = bets
        return match

    def scrape_match_bets(self, match):
        t = time.time()
        self.renderer.get('https://www.google.com/')
        self.renderer.get(match.url)

        wait = WebDriverWait(self.renderer, 3)

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'title_text')))
            return match
        except TimeoutException:
            pass

        try:
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slick-block')))
            self.renderer.click(element)
        except TimeoutException:
            pass

        time.sleep(0.5)
        self._parse_marketblocks(match.bets, match.url)
        print(self._NAME, time.time() - t)
        return match

    def _get_bets_from_live_match_with_basic_data(self, match):
        self.renderer.get(match.url)
        time.sleep(0.5)
        while True:
            bets = []
            self._parse_live_marketblocks(bets, match.url)
            match.bets = bets
            # print_variable('live', self._NAME, 'match = ', match)
            time.sleep(0.5)

    def get_matches_info_sport(self, sport_name):
        matches = []
        subsections = self.get_subsections(sport_name)
        for subsection in subsections:
            tournaments = self.get_subsection_tournaments(subsection)
            time.sleep(1)
            print('favorit subsection:', subsections.index(subsection) + 1)
            for tournament in tournaments:
                events = tournament.find_elements_by_class_name('event--head-block')
                for event in events:
                    matches.append(self._get_match_basic_data(event))
                    # break
            self.renderer.click(subsection)
            time.sleep(1)

        return Sport(sport_name, matches)

    def _get_match_basic_data(self, event):
        date = event.find_element_by_class_name('event--date').text
        time = event.find_element_by_class_name('event--time').text
        date_time_str = date + time
        date_time = DateTime.from_favorit_str(date_time_str)
        name = event.find_element_by_class_name('long--name').text.lower()
        button = event.find_element_by_class_name('event--more')
        self.renderer.click(button)
        url = self.renderer.current_url
        return Match(MatchTitle(name.split(' - ')), url, date_time, self)

    def _get_bets_one_by_one(self, sport_name):
        sport_bets = []
        matches = self.get_matches_info_sport(sport_name).matches

        for match in matches:
            self.renderer.get('https://www.google.com/')
            print('match', matches.index(match) + 1, '/', len(matches))
            print(match.date)
            match_bets = self.scrape_match_bets(match)
            if match_bets:
                sport_bets.append(match_bets)
            break
        sport = Sport(sport_name, sport_bets)
        return sport

    def get_live_matches_info_sport(self, sport_name):
        matches = []
        self.renderer.get(self._LIVE_URL)
        events = []
        events_ = [1, 2]
        time.sleep(2)

        while len(events) != len(events_):
            events = []
            events_ = None
            menu = self.renderer.find_element_by_class_name('sportslist')
            list_of_sports = menu.find_elements_by_class_name('sprt')
            sport = None
            for _sport in list_of_sports:
                if _sport.find_element_by_class_name('sprtnm').text == self._ICONS[sport_name]:
                    sport = _sport
                    break
            events_ = sport.find_elements_by_class_name('sp-mn-ev')
            for el in events_:
                try:
                    events.append(el.find_element_by_tag_name('div'))
                except Exception:
                    pass
            print(len(events_), len(events))

        for event in events:
            try:
                matches.append(self.get_live_match_basic_data(event))
            except Exception:
                pass
        return Sport(sport_name, matches)

    def get_live_match_basic_data(self, event):
        self.renderer.click(event)
        teams = [name.text for name in event.find_elements_by_tag_name('span')]
        match_url = self.renderer.current_url

        return Match(MatchTitle(teams), match_url, '', self)


if __name__ == '__main__':
    t = time.time()
    scraper = FavoritScraper()
    sport = scraper.get_matches_info_sport(SPORT_NAME)
    # for match in sport:
    #     scraper.scrape_match_bets(match)
    print(sport)
    scraper.renderer.quit()
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\' + SPORT_NAME + '\\' + scraper.get_name()
    sport.serialize(path)
    with open(path + '.py', 'w', encoding='utf-8') as f:
        print('sport =', sport, file=f)

    print(time.time() - t)
