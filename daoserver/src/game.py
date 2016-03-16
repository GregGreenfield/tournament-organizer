"""
Module for storing games.

A game is simply a match between two entries. It is played on a table.
"""
# pylint: disable=no-member

from sqlalchemy.sql.expression import and_

from db_connections.db_connection import db_conn
from entry import Entry
from models.score import RoundScore, ScoreCategory, ScoreKey, Score, db
from models.tournament_game import TournamentGame

@db_conn()
# pylint: disable=E0602
def get_game_from_score(entry_id, score_key):
    """Given an entry and score_key, you should be able to work out the game"""
    cur.execute(
        "SELECT tournament, for_round, entry_id \
        FROM player_score WHERE entry_id = %s AND key = %s",
        [entry_id, score_key])
    tournament_round_entry = cur.fetchone()

    if tournament_round_entry is None:
        return None

    cur.execute(
        "SELECT g.id, g.table_num, g.protected_object_id \
        FROM game g INNER JOIN game_entrant e ON g.id = e.game_id \
        WHERE g.tourn = %s AND g.round_num = %s AND e.entrant_id = %s",
        tournament_round_entry)
    game_id_table = cur.fetchone()

    cur.execute(
        "SELECT entrant_id FROM game_entrant WHERE game_id = %s",
        [game_id_table[0]])
    entrants = [Entry(entry_id=x[0]) for x in cur.fetchall()]
    if len(entrants) == 1:
        entrants.append('BYE')

    return Game(entrants,
                game_id=game_id_table[0],
                tournament_id=tournament_round_entry[0],
                round_id=tournament_round_entry[1],
                table_number=game_id_table[1],
                protected_object_id=tournament_round_entry[2])

# pylint: disable=undefined-variable
class Game(object):
    """
    Representation of a single match between entrants.
    This might be a BYE
    """

    #pylint: disable=R0913
    def __init__(self, entrants, game_id=None, tournament_id=None,
                 round_id=None, table_number=None, protected_object_id=None):
        self.game_id = game_id
        self.tournament_id = tournament_id
        self.round_id = round_id
        self.table_number = table_number
        self.entry_1 = None if entrants[0] == 'BYE' else entrants[0].entry_id
        self.entry_2 = None if entrants[1] == 'BYE' else entrants[1].entry_id
        self.protected_object_id = protected_object_id

    def num_entrants(self):
        """The number of entrants in the game"""
        return 1 if None in [self.entry_1, self.entry_2] else 2

    def get_dao(self):
        """Gaet DAO object for self"""
        # pylint: disable=no-member
        return TournamentGame.query.filter_by(id=self.game_id).first()

    @db_conn()
    def is_score_entered(self):
        """
        Checks if all scores for the game are entered and updates game row if
        True.

        When a score is entered we should check to see if all the scores for
        the game are entered. If yes we can update the game entry
        """

        if self.get_dao() is not None and self.get_dao().score_entered:
            return True

        scores_for_round = len(ScoreKey.query.join(RoundScore).\
            join(ScoreCategory).filter(
                and_(RoundScore.round_id == self.round_id,
                     ScoreCategory.tournament_id == self.tournament_id)).all())
        scores_entered = [x[2] for x in self.scores_entered()]

        return None not in scores_entered \
        and len(scores_entered) == (scores_for_round * self.num_entrants())

    @db_conn()
    def scores_entered(self):
        """
        Get a list of all scores entered for the game by all entrants.

        Returns:
            - a list of tuples (entry_id, score_key, score_entered)
        """

        scores_and_keys = db.session.query(Score, ScoreKey).join(ScoreKey).\
            join(RoundScore).join(ScoreCategory).filter(and_(
                ScoreCategory.tournament_id == self.tournament_id,
                RoundScore.round_id == self.round_id,
                Score.entry_id.in_((self.entry_1, self.entry_2)))).all()
        return [(x[0].entry_id, x[1].key, x[0].value) for x in scores_and_keys]
