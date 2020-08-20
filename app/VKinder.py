from app.functions import \
    User, get_photos, best_3_photo
from app.db import \
    create_user_matches_table, create_photos_table, add_matches, add_photo, \
    get_users_id_list, write_to_json


def VKinder(user_id):
    user1 = User(user_id)
    create_user_matches_table()
    create_photos_table()

    if user1.user_id not in get_users_id_list():
        match_photos = {}

        count_search_results = user1.count_search_matches()

        create_user_matches_table()
        create_photos_table()

        offset = 0
        while count_search_results >= offset:
            result = user1.search_matches(offset)
            for i in result:
                resp = get_photos(user1.token, i['id'])
                try:
                    match_photos[i['id']] = best_3_photo(resp['response']['items'])
                except KeyError:
                    pass

                for k, v in match_photos.items():
                    add_matches(user1.user_id, k)
                    for link in v:
                        add_photo(k, link)

            offset += 30
        write_to_json(user1.user_id)

    else:
        write_to_json(user1.user_id)
