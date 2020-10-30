import requests
import time
import datetime
from urllib.parse import urlencode

OAUTH_URL = 'https://oauth.vk.com/authorize'
OAUTH_PARAMS = {
    'client_id': '7571903',
    'display': 'page',
    'scope': 'friends,photos,offline,groups,wall',
    'response_type': 'code'
}
VK_VERSION = 5.122
CLIENT_ID = '7571903'
CLIENT_SECRET = 'MTYf9MDHeMvtfwAEDj1k'


def get_token():
    code_link = '?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS)))
    print(code_link)
    code = input('Пройдите по ссылке и скопируйте код'
                 ' "https://oauth.vk.com/blank.html#code=[ ВАШ КОД ]": ')
    token_params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code
    }
    resp = requests.get(
        'https://oauth.vk.com/access_token', params=token_params
    )

    return resp.json()['access_token']


def make_request(method, new_params):
    print('Делаем запрос')
    params = {
        'v': VK_VERSION
    }
    params.update(new_params)
    response = requests.get(
        f'https://api.vk.com/method/{method}', params=params
    )
    time.sleep(0.3)
    return response


def get_user_info(user_id, token):
    print('Получаем информацию о пользователе')
    result = make_request('users.get', {
        'user_ids': user_id,
        'access_token': token,
        'fields': 'bdate,sex,country,city,interests',
    }).json()['response']

    return result[0]


def get_age(bdate):
    print('Указываем возраст')
    birthday = datetime.datetime.strptime(bdate, '%d.%m.%Y')
    today = datetime.date.today()
    age = today.year - birthday.year
    if today.month < birthday.month:
        age -= 1
    elif today.month == birthday.month and today.day < birthday.day:
        age -= 1
    return age


class User:

    def __init__(self, user_id, token=None):
        if token is None:
            self.token = get_token()
        if isinstance(user_id, str) and not user_id.isdigit():
            get_data = {'user_ids': user_id, 'access_token': self.token}
            resp = make_request('users.get', get_data).json()
            self.user_id = resp['response'][0]['id']

        else:
            self.user_id = user_id
        user_info = get_user_info(self.user_id, self.token)
        try:
            self.bdate = user_info['bdate']
        except KeyError:
            self.bdate = input('Введите дату рождения в формате D.M.YYYY: ')
        self.city_id = user_info['city']['id']
        self.country_id = user_info['country']['id']
        self.user_sex = user_info['sex']

    def get_group_list(self):
        print('Получаем список групп')
        result = make_request('groups.get', {
            'user_id': self.user_id,
            'access_token': self.token,
            'extended': 0
        }).json()

        return result['response']['items']

    def count_search_matches(self):
        print('Подбираем варианты и получаем информацию')
        search_sex = '1'
        if self.user_sex == '1':
            search_sex = '2'

        search_conditions = {
            'access_token': self.token,
            'sort': '0',
            'city': self.city_id,
            'country': self.country_id,
            'sex': search_sex,
            'status': ['1', '6'],
            'age_from': get_age(self.bdate) - 2,
            'age_to': get_age(self.bdate) + 2,
            'has_photo': '1'
        }

        result = make_request('users.search', search_conditions
                              ).json()['response']['count']
        return result

    def search_matches(self, offset):
        search_sex = '1'
        if self.user_sex == '1':
            search_sex = '2'

        search_conditions = {
            'access_token': self.token,
            'count': 50,
            'offset': offset,
            'sort': '0',
            'city': self.city_id,
            'country': self.country_id,
            'sex': search_sex,
            'status': ['1', '6'],
            'age_from': get_age(self.bdate) - 2,
            'age_to': get_age(self.bdate) + 2,
            'has_photo': '1'
        }
        result = make_request('users.search', search_conditions
                              ).json()['response']['items']
        return result


def get_photos(token, owner_id):
    print('Получаем фото')
    return make_request('photos.get', {
        'access_token': token,
        'owner_id': owner_id,
        'album_id': 'profile',
        'extended': 'likes',
    }).json()


def best_3_photo(photo_list):
    print('Выбираем 3 лучших фото')
    tmp = {}
    for p in photo_list:
        tmp[p['likes']['count']] = p['sizes']

    list_keys = list(tmp.keys())
    list_keys.sort(reverse=True)
    result = []
    for i in list_keys[:3:]:
        result.append(tmp[i][-1]['url'])
    return result


def like_photo(token, owner_id, item_id):
    make_request('likes.add', {
        'type': 'photo',
        'access_token': token,
        'owner_id': owner_id,
        'item_id': item_id
    })