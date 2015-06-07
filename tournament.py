#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


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

    query = """select player_id, firstname, wins, wins+loses+draws as matches
                from tournament_standings;"""

    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results


def reportMatch(winner_id, loser_id, match_id, draw=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """


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
