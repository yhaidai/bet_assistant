import unittest
import re

from sport import Sport
from sample_data.dota.parimatch import sport as parimatch_dota_dict
from sample_data.dota.one_x_bet import sport as one_x_bet_dota_dict
from sample_data.dota.ggbet import sport as ggbet_dota_dict
from sample_data.dota.favorit import sport as favorit_dota_dict
from sample_data.dota.marathon import sport as marathon_dota_dict
from syntax_formatters.esports.dota.dota_parimatch_syntax_formatter import DotaParimatchSyntaxFormatter
from syntax_formatters.esports.dota.dota_one_x_bet_syntax_formatter import DotaOneXBetSyntaxFormatter
from syntax_formatters.esports.dota.dota_ggbet_syntax_formatter import DotaGGBetSyntaxFormatter
from syntax_formatters.esports.dota.dota_favorit_syntax_formatter import DotaFavoritSyntaxFormatter
from syntax_formatters.esports.dota.dota_marathon_syntax_formatter import DotaMarathonSyntaxFormatter


class TestSyntaxFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.parimatch_dota_dict = parimatch_dota_dict
        self.one_x_bet_dota_dict = one_x_bet_dota_dict
        self.ggbet_dota_dict = ggbet_dota_dict
        self.favorit_dota_dict = favorit_dota_dict
        self.marathon_dota_dict = marathon_dota_dict

        self.parimatch_syntax_formatter = DotaParimatchSyntaxFormatter()
        self.one_x_bet_syntax_formatter = DotaOneXBetSyntaxFormatter()
        self.ggbet_syntax_formatter = DotaGGBetSyntaxFormatter()
        self.favorit_syntax_formatter = DotaFavoritSyntaxFormatter()
        self.marathon_syntax_formatter = DotaMarathonSyntaxFormatter()

        self.bet_title_patterns = [
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?will (win|lose)((at least )?.+? map(s)?)?$',  # win
            r'^(\d+-(st|nd|rd|th) map: )?correct score \d+-\d+$',  # correct score
            # total over/under
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?total ((maps|kills|roshans) )(over|under) (\d+(\.\d)?)$',
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )?total( (maps|kills)) (even|odd)$',  # total even/odd
            r'^(\d+-(st|nd|rd|th) map: )?(.+? )handicap (\+|-)\d+(\.\d)? kills',  # kills handicap
            r'^(.+? )handicap (\+|-)\d+(\.\d)? maps$',  # maps handicap
            r'^\d+-(st|nd|rd|th) map: duration (over|under) \d+(\.\d)$',  # map duration
            r'^\d+-(st|nd|rd|th) map: (.+?) will make kill \d+$',  # kill number
            # first to
            r'^\d+-(st|nd|rd|th) map: (.+?) will first (kill roshan|destroy tower|lose barracks|make \d+ kills)$',
            r'^\d+-(st|nd|rd|th) map: megacreeps (yes|no)$',  # megacreeps
            r'^(.+?) first blood$',  # first blood
            ]
        self.odds_pattern = r'^\d+(\.\d+)?$'

    # @unittest.skip
    def test_parimatch_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.parimatch_dota_dict)
        sport = self.parimatch_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_one_x_bet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.one_x_bet_dota_dict)
        sport = self.one_x_bet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_ggbet_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.ggbet_dota_dict)
        sport = self.ggbet_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_favorit_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.favorit_dota_dict)
        sport = self.favorit_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    # @unittest.skip
    def test_marathon_unified_syntax_formatting(self):
        sport = Sport.from_dict(self.marathon_dota_dict)
        sport = self.marathon_syntax_formatter.apply_unified_syntax_formatting(sport)
        self._test_unified_syntax_formatting(sport)

    def _test_unified_syntax_formatting(self, sport):
        for match in sport:
            with self.subTest(match_title=match.title):
                for bet in match:
                    with self.subTest(bet_title=bet.title, odds=bet.odds):
                        if not re.match('|'.join(self.bet_title_patterns), bet.title):
                            print(bet.title)
                        self.assertRegex(bet.title, '|'.join(self.bet_title_patterns),
                                         'bet title must match its pattern')
                        self.assertRegex(bet.odds, self.odds_pattern, 'odds must match their pattern')


if __name__ == '__main__':
    unittest.main()
