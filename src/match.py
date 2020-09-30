from datetime import datetime
from pprint import pformat
import re

from src.bet import Bet
from src.match_title import MatchTitle


class Match:
    def __init__(self, title: MatchTitle, url: str, date_time: datetime, scraper, bets=None):
        if bets is None:
            bets = []
        self.title = title
        self.url = url
        self.date_time = date_time
        self.scraper = scraper
        self.bets = bets

    @classmethod
    def from_dict(cls, match_dict):
        url = None
        date_time = None
        title = None
        key = list(match_dict.keys())[0]
        found = re.search(r'^(https://.+?) (.+?): (.+?)$', key)
        if found:
            url = found.group(1)
            date_time = datetime.fromisoformat(found.group(2))
            title = MatchTitle.from_str(found.group(3))

        bets_dict = list(match_dict.values())[0][0]
        bets = [Bet.from_dict({bet_title: odds}) for bet_title, odds in bets_dict.items()]

        return cls(title, url, date_time, None, bets)

    def to_dict(self):
        result = {}
        for bet in self.bets:
            value = str(bet.odds) + '(' + str(bet.bookmaker) + ' - ' + str(bet.url) + ')'

            result.setdefault(bet.title, []).append(value)

        return result

    def __iter__(self):
        return iter(self.bets)

    def __next__(self):
        return next(self.bets)

    def __len__(self):
        return len(self.bets)

    def __eq__(self, other):
        return (self.url == other.url and self.title == other.title and
                self.date_time == other.date_time and self.scraper == other.scraper)

    def __hash__(self):
        return hash(self.url + str(self.date_time) + str(self.title) + self.scraper.get_name())

    def __getitem__(self, item: int):
        return self.bets[item]

    def __repr__(self):
        date_time_str = ''
        url_str = ''
        if self.date_time:
            date_time_str = str(self.date_time) + ': '
        if self.url:
            url_str = self.url + ' '
        return pformat({url_str + date_time_str + str(self.title): self.to_dict()}, width=300)


if __name__ == '__main__':
    b1 = Bet('Total Over 2.5', '2.77', 'sample_bookmaker', 'https://sample_bet1_url.domain')
    b2 = Bet('Total Under 2.5', '1.45', 'sample_bookmaker', 'https://sample_bet2_url.domain')
    mt = MatchTitle.from_str('astralis - g2 - cloud9')
    dt = datetime(2020, 12, 23, 14, 0, 0)
    m = Match(mt, 'https://sample_match_url.domain', dt, None, [b1, b2])
    print(m)
    print(m.to_dict())
    print(m.__dict__)
