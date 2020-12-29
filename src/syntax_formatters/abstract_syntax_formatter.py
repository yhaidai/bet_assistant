import re
from abc import ABC, abstractmethod

from match import Match
from singleton import ABCMetaSingleton
from sport import Sport


class AbstractSyntaxFormatter(ABC, metaclass=ABCMetaSingleton):
    """
    Class that is used for applying unified syntax formatting to all betting
    related information scraped from the websites
    """
    def format_match(self, match):
        # print(match.title.similarities)
        # print(match.title.raw_teams)
        # print(match.title.teams)
        match = self.apply_unified_syntax_formatting(Sport('', [match])).matches[0]
        self._format_bet_titles_teams(match)
        return match

    @staticmethod
    def _format_bet_titles_teams(match: Match) -> None:
        try:
            for bet in match:
                for raw_team, unified_team in match.title.similarities.items():
                    bet.title = bet.title.replace(raw_team, unified_team)
        except AttributeError:
            return

    def apply_unified_syntax_formatting(self, sport: Sport):
        """
        Apply unified syntax formatting to the given sport

        :param sport: sport to format
        :type sport: Sport
        """
        sport = self._format_before(sport)

        sport = self._update(sport, self._format_uncommon_chars)
        sport = self._update(sport, self._format_total)
        sport = self._update(sport, self._format_handicap)
        sport = self._update(sport, self._format_correct_score_complete)
        sport = self._update(sport, self._format_win)

        sport = self._format_after(sport)

        sport = self._format_odds(sport)
        # sport = self._format_titles(sport)

        return sport

    def _format_before(self, sport):
        """
        Apply unified syntax formatting to the given bets dict before obligatory updates are run. Subclass specific

        :param sport: sport to format
        :type sport: Sport
        :return: formatted sport
        :rtype: Sport
        """
        return sport

    def _format_after(self, sport):
        """
        Apply unified syntax formatting to the given bets dict after obligatory updates are run. Subclass specific

        :param sport: sport to format
        :type sport: Sport
        :return: formatted sport
        :rtype: Sport
        """
        return sport

    @abstractmethod
    def _get_name(self):
        pass

    def _get_invalid_bet_titles(self):
        return ()

    def _get_invalid_match_titles(self):
        return ()

    def _update(self, sport, _callable):
        """
        Update self.bets and given bets dictionaries according to _callable method

        :param sport: bets dictionary to format
        :type sport: Sport
        :param _callable: method to be called to get formatted bet title
        :type _callable: method
        :return: updated sport
        :rtype: Sport
        """
        invalid_bet_titles = self._get_invalid_bet_titles()
        invalid_match_titles = self._get_invalid_match_titles()

        for match in list(sport):
            self.match_title = match.title
            for bet in list(match):
                self.bet_title = bet.title
                formatted_title = _callable()
                bet.title = formatted_title

                if self.bet_title in invalid_bet_titles:
                    match.bets.remove(bet)

            if self.match_title in invalid_match_titles:
                sport.matches.remove(match)

        return sport

    @staticmethod
    def _format_odds(sport):
        """
        Remove empty odds bet titles

        :param sport: sport to format
        :type sport: Sport
        :return: updated sport
        :rtype: Sport
        """
        for match in sport:
            for bet in list(match):
                if not bet.title:
                    print('Odds: ', bet.odds, ';')
                if not bet.odds or bet.odds == '':
                    match.bets.remove(bet)

        return sport

    def _format_win(self):
        return self.bet_title.lower()

    def _format_total(self):
        return self.bet_title.lower()

    def _format_handicap(self):
        return self.bet_title.lower()

    def _format_correct_score_complete(self):
        formatted_bet_title = self._format_correct_score()
        formatted_bet_title = self._fix_teams_order_in_correct_score(formatted_bet_title)
        return formatted_bet_title

    def _format_correct_score(self):
        return self.bet_title.lower()

    def _fix_teams_order_in_correct_score(self, bet_title):
        formatted_title = bet_title.lower()
        found = re.search('correct score ((\d+)-(\d+))$', formatted_title)
        if found:
            try:
                raw_teams = self.match_title.raw_teams
            except AttributeError:
                return formatted_title

            teams = self.match_title.teams
            for raw_team in raw_teams:
                # find changed team
                changed_team = raw_team
                if raw_team in self.match_title.similarities:
                    changed_team = self.match_title.similarities[raw_team]

                if raw_teams.index(raw_team) != teams.index(changed_team):
                    formatted_title = formatted_title[:-len(found.group(1))]
                    formatted_title += found.group(3) + '-' + found.group(2)
                    break

        return formatted_title

    def _format_uncommon_chars(self):
        return self.bet_title.lower()

    def swap_teams(self, title):
        teams = self.match_title.get_teams()

        if teams[0] in title:
            title = title.replace(teams[0], teams[1])
        else:
            title = title.replace(teams[1], teams[0])
        return title

    def _move_teams_left(self, formatted_title=None):
        if not formatted_title:
            formatted_title = self.bet_title.lower()
        teams = self.match_title.get_teams()

        for team in teams:
            if team in formatted_title:
                match = re.search(r'^' + team, formatted_title)
                if match:
                    break
                formatted_title = formatted_title.replace(' ' + team, '')
                match = re.search(r'(\d+-(st|nd|rd|th) (map:|half))', formatted_title)
                if match:
                    formatted_title = formatted_title.replace(match.group(1), match.group(1) + ' ' + team)
                else:
                    formatted_title = team + ' ' + formatted_title
                break

        return formatted_title
