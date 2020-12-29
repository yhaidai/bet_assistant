import re

from sport import Sport
from syntax_formatters.esports.csgo.csgo_abstract_syntax_formatter import CSGOAbstractSyntaxFormatter
from syntax_formatters.esports.esports_marathon_syntax_formatter import EsportsMarathonSyntaxFormatter as MSF
from sample_data.csgo import marathon
import os.path


class CSGOMarathonSyntaxFormatter(CSGOAbstractSyntaxFormatter, MSF):
    def _format_teams(self):
        return self._move_teams_left()

    def _format_handicap(self):
        formatted_title = MSF._format_handicap(self)
        if 'handicap' in formatted_title and ' maps' not in formatted_title:
            formatted_title += ' rounds'

        return formatted_title


if __name__ == '__main__':
    formatter = CSGOMarathonSyntaxFormatter()
    sport = Sport.from_dict(marathon.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\marathon.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
