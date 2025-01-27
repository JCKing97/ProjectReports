"""A module for which contains functionality for converting tournaments and matched for storage in the database"""

from app import db, create_app
from app.models import Match, Round, Player, Action, Tournament, TournamentPlayer
import axelrod as axl

app = create_app()
app.app_context().push()


def match_result_to_database(results, players):
    """Store the data for a match that has run in the database"""
    # Add match and players into database
    m = Match()
    db.session.add(m)
    db.session.flush()
    players = [Player(id=i, match_id=m.id, strategy=players[i].name) for i in range(0, 2)]
    db.session.add_all(players)
    db.session.flush()
    i = 1
    # Add actions into database
    for round in results:
        r = Round(num=i, match_id=m.id)
        db.session.add(r)
        db.session.flush()
        for j in range(0, 2):
            a = Action(round_num=r.num, match_id=m.id, player_id=players[j].id, cooperate=(round[j]==axl.Action.C))
            db.session.add(a)
        i += 1
    db.session.commit()
    return m.id


def tournament_run(players, tournament_id):
    """Store the data of a tournament that has run in the database, can be run in a Redis queue"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    try:
        results = axl.Tournament(players).play()
        tournament_players = []
        for i in range(0, len(players)):
            tournament_players.append(TournamentPlayer(id=i, tournament_id=tournament_id, strategy=players[i].name,
                                                       score=results.scores[i][0], rank=results.ranking[i],
                                                       cooperation_rating=results.cooperating_rating[i],
                                                       wins=results.wins[i][0]))
        db.session.add_all(tournament_players)
        tournament.completed = True
        db.session.commit()
    except:
        app.logger.error("Error")
        tournament.error = True
        db.session.commit()
