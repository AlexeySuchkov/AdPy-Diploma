import psycopg2
from psycopg2 import sql

import json

DB_NAME = 'VKinder'
DB_USER = 'postgres'
USER_PASSWORD = '01101976'
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=USER_PASSWORD,
    host='localhost', port='5432')


def execute_context(query, *args):
    with conn:
        with conn.cursor() as curs:
            curs.execute(query, *args)


def create_user_matches_table():
    query = sql.SQL('CREATE TABLE IF NOT EXISTS user_matches ('
                    'id SERIAL PRIMARY KEY NOT NULL,'
                    'user_vk_id INT NOT NULL,'
                    'match_vk_id INT NOT NULL,'
                    'black_list BOOLEAN DEFAULT FALSE,'
                    'favourite_list BOOLEAN DEFAULT FALSE'
                    ')')
    execute_context(query)


def create_photos_table():
    query = sql.SQL('CREATE TABLE IF NOT EXISTS photos ('
                    'photo_id SERIAL PRIMARY KEY NOT NULL,'
                    'match_user_vk_id INT NOT NULL,'
                    'photo_url CHAR(250)'
                    ')')
    execute_context(query)


def add_matches(user_vk_id, match_vk_id):
    query = sql.SQL('INSERT INTO user_matches (user_vk_id, match_vk_id) '
                    'SELECT %s, %s '
                    'WHERE NOT EXISTS (SELECT * FROM user_matches '
                    'WHERE user_vk_id= %s AND match_vk_id= %s)')
    execute_context(query, (user_vk_id, match_vk_id, user_vk_id, match_vk_id))


def add_photo(match_user_id, photo_link):
    query = sql.SQL('INSERT INTO photos (match_user_vk_id, photo_url) '
                    'SELECT %s, %s'
                    'WHERE NOT EXISTS (SELECT * FROM photos '
                    'WHERE match_user_vk_id= %s AND photo_url= %s)')
    execute_context(query,
                    (match_user_id, photo_link, match_user_id, photo_link))


def get_match_user_id(match_user_vk_id):
    curs = conn.cursor()
    curs.execute('SELECT id FROM user_matches WHERE match_vk_id = (%s)',
                 (match_user_vk_id,))
    tmp = curs.fetchall()
    curs.close()
    return tmp[0][0]


def get_10_matches(user_vk_id):
    curs = conn.cursor()
    curs.execute('SELECT match_vk_id FROM user_matches '
                 'WHERE user_vk_id = (%s) '
                 'AND black_list = FALSE LIMIT 10',
                 (user_vk_id,))
    tmp = curs.fetchall()
    curs.close()
    matches_list = []
    for m in tmp:
        matches_list.append(m[0])
    return matches_list


def get_photos_by_id(id):
    curs = conn.cursor()
    curs.execute('SELECT photo_url FROM photos WHERE match_user_vk_id = (%s)',
                 (id,))
    tmp = curs.fetchall()
    curs.close()
    photo_list = []
    for p in tmp:
        photo_list.append(p[0])
    return photo_list


def add_to_black_list(id):
    query = sql.SQL('UPDATE user_matches SET black_list = true '
                    'WHERE match_vk_id = (%s)')
    execute_context(query, (id,))


def get_users_id_list():
    curs = conn.cursor()
    curs.execute('SELECT user_vk_id FROM user_matches')
    tmp = curs.fetchall()
    curs.close()
    users_list = []
    for u in tmp:
        users_list.append(u[0])
    return users_list


def write_to_json(user_id):
    first_10 = {}
    for u in get_10_matches(user_id):
        first_10[u] = get_photos_by_id(u)
        add_to_black_list(u)

    with open(f'files/matches_for_{user_id}.json',
              'w', encoding='utf-8-sig') as file:
        json.dump(first_10, file, indent=3)