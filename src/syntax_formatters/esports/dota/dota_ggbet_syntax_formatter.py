import re

from sport import Sport
from syntax_formatters.esports.dota.dota_abstract_syntax_formatter import DotaAbstractSyntaxFormatter
from syntax_formatters.esports.esports_ggbet_syntax_formatter import EsportsGGBetSyntaxFormatter as GSF
from scrapers.sample_data.dota import ggbet
import os.path


class DotaGGBetSyntaxFormatter(DotaAbstractSyntaxFormatter, GSF):
    def _format_total(self):
        formatted_title = GSF._format_total(self)
        if 'total roshans slain' in formatted_title:
            formatted_title = formatted_title.replace('slain ', '')
        return formatted_title

    def _format_specific_kill(self):
        formatted_title = self.bet_title.lower()
        match = re.search(r'((\d+)th kill )', formatted_title)
        if match:
            formatted_title = formatted_title.replace(match.group(1), '')
            formatted_title += ' will make kill ' + match.group(2)
        return formatted_title

    def _format_individual_total_kills(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_first_to_make_number_of_kills(self):
        formatted_title = self.bet_title.lower()
        if 'race to kills' in formatted_title:
            formatted_title = formatted_title.replace('race to kills ', '')
            words = re.split(' ', formatted_title)
            formatted_title = ''
            for i in range(len(words)-1):
                formatted_title += words[i] + ' '
            formatted_title += 'will first make ' + words[-1] + ' kills'
        return formatted_title

    def _format_first_to_destroy_tower(self):
        formatted_title = self.bet_title.lower()
        if 'destroy first tower' in formatted_title:
            formatted_title = formatted_title.replace('destroy first tower ', '')
            formatted_title += ' will first destroy tower'
        return formatted_title

    def _format_first_to_kill_roshan(self):
        formatted_title = self.bet_title.lower()
        if 'kill first roshan' in formatted_title:
            formatted_title = formatted_title.replace('kill first roshan ', '')
            formatted_title += ' will first kill roshan'
        return formatted_title

    def _format_most_kills(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_draw(self):
        formatted_title = self.bet_title.lower()
        return formatted_title

    def _format_first_kill(self):
        formatted_title = self.bet_title.lower()
        if 'first blood' in formatted_title:
            formatted_title = formatted_title.replace('first blood ', '')
            formatted_title += ' first blood'
        return formatted_title

    def _format_map_duration(self):
        formatted_title = self.bet_title.lower()
        if 'map duration' in formatted_title:
            formatted_title = formatted_title.replace('map duration', 'duration')
            formatted_title = formatted_title.replace(' minutes', '')
        return formatted_title

    def _remove_full_time(self):
        formatted_title = self.bet_title.lower()
        if 'full time' in formatted_title:
            formatted_title = formatted_title.replace('full time ', '')
        for c in ['(', ')', '- ']:
            formatted_title = formatted_title.replace(c, '')
        return formatted_title

    def _format_before(self, bets):
        bets = self._update(bets, self._remove_full_time)
        bets = self._update(bets, self._format_whitespaces)
        return bets

    def _format_whitespaces(self):
        formatted_title = self.bet_title.lower()
        formatted_title = ' '.join(formatted_title.split())
        formatted_title = formatted_title.strip()
        return formatted_title

if __name__ == '__main__':
    formatter = DotaGGBetSyntaxFormatter()
    sport = Sport.from_dict(ggbet.sport)
    formatted_sport = formatter.apply_unified_syntax_formatting(sport)
    print(formatted_sport)
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + '\\sample_data\\ggbet.py'
    with open(path, 'w', encoding='utf-8') as f:
        print('sport =', formatted_sport, file=f)
