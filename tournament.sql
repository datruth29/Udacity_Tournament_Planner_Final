-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS tournament, player, registrations, game, game_result CASCADE;
DROP VIEW IF EXISTS registered_players CASCADE;
DROP TYPE IF EXISTS game_result_types;

CREATE TYPE game_result_types as ENUM ('win', 'draw', 'lose');


-- TABLES

CREATE TABLE tournament(
    tournament_id serial primary key not null,
    name text,
    created timestamp default current_timestamp
);

CREATE TABLE player(
    player_id serial primary key not null,
    firstname text not null,
    middlename text,
    lastname text not null
);

CREATE TABLE registrations(
    player_id integer REFERENCES player ON DELETE CASCADE,
    tournament_id integer REFERENCES tournament ON DELETE CASCADE,
    registeration_num serial primary key not null,
    UNIQUE (player_id, tournament_id)
);

CREATE TABLE game(
    game_id serial primary key not null,
    tournament_id integer REFERENCES tournament,
    player1_id integer REFERENCES player,
    player2_id integer REFERENCES player,
    round integer not null
);

CREATE TABLE game_result(
    game_result_id serial primary key not null,
    game_id integer REFERENCES game ON DELETE CASCADE,
    player_id integer REFERENCES player,
    result game_result_types
);

-- VIEWS

CREATE VIEW registered_players AS
    SELECT player.firstname, player.lastname, tournament.name
    FROM registrations
        INNER JOIN player ON registrations.player_id = player.player_id
        INNER JOIN tournament ON registrations.tournament_id = tournament.tournament_id;

CREATE VIEW tournament_standings AS
    SELECT  player.player_id, player.firstname, player.lastname,
            sum(CASE WHEN game_result.result = 'win' THEN 1 ELSE 0 END) as Wins,
            sum(CASE WHEN game_result.result = 'lose' THEN 1 ELSE 0 END) as Loses,
            sum(CASE WHEN game_result.result = 'draw' THEN 1 ELSE 0 END) as Draws
    FROM player
    LEFT JOIN game_result ON player.player_id = game_result.player_id
    GROUP BY player.player_id;

-- INSERTS

INSERT INTO tournament (name, created) VALUES ('Test tournament', DEFAULT);
INSERT INTO player (firstname, middlename, lastname) VALUES
    ('Adam', 'Juan', 'Collado'),
    ('Jaymes', 'S', 'Soto');
INSERT INTO registrations (tournament_id, player_id) VALUES
    (1, 1),
    (1, 2);
