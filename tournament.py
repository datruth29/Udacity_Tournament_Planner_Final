#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import itertools


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament_id=None):
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()

    if not tournament_id:
        query = "select tournament_id from tournament order by tournament_id desc limit 1"
        cursor.execute(query)
        tournament_id = cursor.fetchall()[0][0]

    cursor.execute("delete from game where tournament_id = %s", (tournament_id, ))
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()

    query = "delete from player;"
    cursor.execute(query)

    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()

    query = "select count(player_id) from player;"
    cursor.execute(query)
    players = cursor.fetchall()[0][0]

    conn.commit()
    conn.close()

    return players


def createPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        name: the player's full name (need not be unique).

    Returns:
        player_id: id of the newly created player.
    """
    conn = connect()
    cursor = conn.cursor()

    firstname, lastname = name.split()
    cursor.execute("""insert into player (firstname, lastname) values (%s, %s)
                   returning player_id;""",
                   (firstname, lastname,))
    result = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return result


def registerPlayer(player_id, tournament_id):
    """
    Registers a player to a specified tournament.

    The database assigns a unique serial id number for the player in regards to their
    registration to a tournament.

    Args:
        player_id: The unique id of the player
        tournament_id: The unique id of the tournament
    """
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("insert into registrations (player_id, tournament_id) values (%s, %s);",
                   (player_id, tournament_id,))

    conn.commit()
    conn.close()


def listPlayers():
    """
    Generates a list of all players

    Displays a list of all players, including their unique id.
    """
    conn = connect()
    cursor = conn.cursor()

    query = "select * from player;"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()

    query = """select player_id, concat(firstname, ' ' , lastname) as name,
                wins, wins+loses+draws as matches
                from tournament_standings;"""

    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results


def createMatch(player1_id, player2_id, tournament_id, current_round):
    """Creates a match between players for a given tournament id and round

    Args:
        player1_id: id of the first player
        player2_id: id of the second player
        tournament_id: id of the tournament the match is being played in
        current_round: the round of the tournament the match is being played in

    Returns:
        game_id: id of the game that was just created
    """
    conn = connect()
    cursor = conn.cursor()

    query = """insert into game (tournament_id, player1_id, player2_id, round)
                values (%s, %s, %s, %s)
                returning game_id;"""
    cursor.execute(query, (tournament_id, player1_id, player2_id, current_round,))
    game_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return game_id


def reportMatch(winner_id, loser_id, match_id, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner_id:  the id number of the player who won.
      loser_id:  the id number of the player who lost.
      match_id: the id number of the match.
      draw: set if the match was a draw. Default = False
    """
    winner_outcome = 'win'
    loser_outcome = 'lose'

    if draw:
        winner_outcome, loser_outcome = ('draw', 'draw')
    else:
        winner_outcome, loser_outcome = ('win', 'lose')

    conn = connect()
    cursor = conn.cursor()

    query = cursor.mogrify("""insert into game_result (game_id, player_id, result)
                            values (%s, %s, %s), (%s, %s, %s);""",
                           (match_id, winner_id, winner_outcome,
                            match_id, loser_id, loser_outcome))
    cursor.execute(query)
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # TODO: Make this work for odd number of players
    # TODO: Make sure this adds players correctly
    # TODO: Ensure that rematches aren't made
    # TODO: Try to implement this into the database
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""select player_id, concat(firstname, ' ' , lastname) as name
                   from tournament_standings order by draws, wins desc""")
    standings = cursor.fetchall()

    result = [tuple(itertools.chain(*standings[n:n+2]))
              for n in range(0, len(standings), 2)]

    conn.commit()
    conn.close()

    return result
