import re
import os.path

from sport import Sport
from syntax_formatters.esports.lol.lol_abstract_syntax_formatter import LoLAbstractSyntaxFormatter
from syntax_formatters.esports.esports_parimatch_syntax_formatter import EsportsParimatchSyntaxFormatter as PSF
from sample_data.lol import parimatch


class LoLParimatchSyntaxFormatter(LoLAbstractSyntaxFormatter, PSF):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the parimatch website
    """

    def _format_total(self):
        formatted_title = self.bet_title.lower()
        if 'total' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, ' ')
        match = re.search('total (over|under)', formatted_title)
        if match:
            if 'map' in formatted_title:
                formatted_title = formatted_title.replace('total', 'total kills')
            else:
                formatted_title = formatted_title.replace('total', 'total maps')

        return formatted_title

    def _format_handicap(self):
        formatted_title = self.bet_title.lower()

        if 'handicap' in formatted_title:
            formatted_title = self._swap_substrings(formatted_title, '. ', 1, 2, '')
            formatted_title = formatted_title.replace('handicap value', '', 1).replace('coefficient', '', 1)

            if 'map:' in formatted_title:
                formatted_title = formatted_title.replace('handicap ', '')
                words = re.split(' ', formatted_title)
                formatted_title = ''
                for i in range(len(words) - 1):
                    formatted_title += words[i] + ' '
                formatted_title += 'handicap ' + words[-1] + ' kills'
            else:
                formatted_title += ' maps'

        return formatted_title


if __name__ == '__main__':
    formatter = LoLParimatchSyntaxFormatter()
    sport = Sport.from_dict(parimatch.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\parimatch.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
