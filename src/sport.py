from datetime import datetime
from pprint import pformat

from src.bet import Bet
from src.match import Match
from src.match_title import MatchTitle


class Sport:
    def __init__(self, name: str, matches: list):
        self.name = name
        self.matches = matches

    @classmethod
    def from_dict(cls, sport_dict):
        matches_dict = list(sport_dict.values())[0]
        matches = [Match.from_dict({match_title: bets}) for match_title, bets in matches_dict.items()]

        return cls(list(sport_dict.keys())[0], matches)

    def to_dict(self):
        result = {}
        for match in self.matches:
            date_time_str = ''
            url_str = ''
            if match.date_time:
                date_time_str = str(match.date_time) + ': '
            if match.url:
                url_str = match.url + ' '
            key = url_str + date_time_str + str(match.title)
            result.setdefault(key, []).append(match.to_dict())
        return result

    def __iter__(self):
        return iter(self.matches)

    def __next__(self):
        return next(self.matches)

    def __repr__(self):
        return pformat({self.name: self.to_dict()}, width=300)

    def __eq__(self, other):
        return self.name == other.name and self.matches == other.matches

    def __len__(self):
        return len(self.matches)

    def __getitem__(self, item: int):
        return self.matches[item]


if __name__ == '__main__':
    b11 = Bet('Total Over 2.5', '2.87', 'sample_bookmaker', 'https://sample_bet11_url.domain')
    b12 = Bet('Total Under 2.5', '1.41', 'sample_bookmaker', 'https://sample_bet12_url.domain')
    mt1 = MatchTitle.from_str('astralis - g2')
    dt1 = datetime(2020, 12, 23, 14, 0, 0)
    m1 = Match(mt1, 'https://sample_match1_url.domain', dt1, None, [b11, b12])
    b21 = Bet('Total Over 2.5', '2.77', 'sample_bookmaker', 'https://sample_bet21_url.domain')
    b22 = Bet('Total Under 2.5', '1.46', 'sample_bookmaker', 'https://sample_bet22_url.domain')
    mt2 = MatchTitle.from_str('virtus.pro - cloud9')
    dt2 = datetime(2020, 11, 12, 22, 30, 0)
    m2 = Match(mt2, 'https://sample_match2_url.domain', dt2, None, [b21, b22])
    sport = Sport('csgo', [m1, m2])
    print(sport)
