import os
import subprocess

from firebase_admin import messaging
from rest_framework.utils import json
import requests
import urllib.parse

from united_help.models import User


COUNTRY_NAME = 'Украина'


def send_topic_push(topic, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
    )
    messaging.send(message)


def send_token_push(title, body, tokens):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=tokens,
    )
    messaging.send_multicast(message)


def get_fine_location(city: str, string_location: str):

    is_three_word_location = True
    separator = '.'

    if len(string_location.split()) == 3 or len(string_location.split('.')) == 3:
        if len(string_location.split()) == 3:
            separator = ' '

        for word in string_location.split(separator):
            if not word.isalpha():
                is_three_word_location = False
                break
    else:
        is_three_word_location = False

    if is_three_word_location:
        three_word_location = '.'.join(string_location.split(separator))
        url = f'https://w3w.co/{three_word_location}?alias={three_word_location}'
        response = requests.get(url).text
        start = response.find('https://mapapi.what3words.com/map/minimap?lat=') + len(
                                                'https://mapapi.what3words.com/map/minimap?')
        finish = start + 50
        parse_text = response[start: finish]
        lat = parse_text[parse_text.find('lat=')+4: parse_text.find('&')]
        lon_start = parse_text.find('lng=')
        lon = parse_text[lon_start+4: parse_text[lon_start:].find('&') + lon_start]
        display_location_prestart = response.find('og:description') + len('og:description"')
        display_location_start = response[display_location_prestart:].find('"') + display_location_prestart + 1
        display_location_finish = response[display_location_start:].find('"') + display_location_start
        display_location = response[display_location_start: display_location_finish]
    else:
        URL = 'https://nominatim.openstreetmap.org/search/{}?format=json'
        url = URL.format(urllib.parse.quote(f'{COUNTRY_NAME} {city} {string_location}'))
        response = requests.get(url).json()
        if not response:
            url = URL.format(urllib.parse.quote(f'{COUNTRY_NAME} {string_location}'))
            response = requests.get(url).json()

        lat = response[0]["lat"]
        lon = response[0]["lon"]
        display_location = response[0]["display_name"]
    return lat, lon, display_location


def send_firebase_multiple_messages(title: str, message: str, users: list[User] | str, **kwargs):
    devices_tokens = []
    batch_size = 500
    # firebase multicastmessage отправляет за раз не более чем 500 сообщений

    if users == 'all':
        users = User.objects.all()

    # если же мне пришли юзеры в виде списка
    elif isinstance(users, list) and isinstance(users[0], int):
        users = User.objects.all()

    for user in users:
        # for notification in notifications_list:
        #     if not getattr(user, notification):
        #         break
        # else:
        if user.firebase_tokens:
            tokens = user.firebase_tokens.split()
            devices_tokens += tokens
            print(f'send message to {user.username} {user.email} with token {user.firebase_tokens} ')
    if devices_tokens:
        success_count = 0
        all_users_whom_sended = [f"  {u.pk} {u.email}" for u in users]

        for i in range(len(devices_tokens) // batch_size + 1):
            data = {
                'title': str(title),
                'text': str(message),
                # for ios
                'content-available': '1',
                'aps': json.dumps({
                    'category': 'player',
                })
            }
            for key, val in kwargs.items():
                if key == 'text' or key == 'title':
                    continue
                data[str(key)] = str(val)
            image = data['image'] if 'image' in data else '0'

            fire_message = messaging.MulticastMessage(
                notification=messaging.Notification(title=title, body=message, image=image),
                tokens=devices_tokens[i * batch_size: min(len(devices_tokens), (i + 1) * batch_size)],
                data=data,
            )
            response = messaging.send_multicast(fire_message)

            all_tokens = len(devices_tokens[i * batch_size: min(len(devices_tokens), (i + 1) * batch_size)])
            users_whom_sended = all_users_whom_sended[i * batch_size: min(len(devices_tokens), (i + 1) * batch_size)]
            print(
                f'[FIREBASE] {response.success_count}/{all_tokens} messages were sent successfully ({users_whom_sended})')
            success_count += response.success_count
        return {'success_count': success_count, 'len_devices_tokens': len(devices_tokens)}
    else:
        print('[FIREBASE] tokens are empty')
        return {'success_count': 0, 'len_devices_tokens': 0}


def get_workers_pids(_list=None, __list=[]):
    if (__list!=[]):
        print('list was mutated')
        return False
    print('get_workers_pids')

    '''
    Для работы этой функции в енвайронментах конфига систмд сервиса должна быть строка пути
    (путь в конфиги - nano /etc/systemd/system/fyuzd-auth.service.d/env.conf)
    Environment="PATH=/home/fyuzd/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
    должна быть установлена тулза jc: pip3 install jc
    путь должен быть в перечне путей
    ln -s /var/lib/fyuzd/venv/bin/jc /usr/local/bin/jc
    в /home/fyuzd должен быть process.sh c пермишенами на исполнение:
    #!/bin/bash
    #jc ps -ef
    ps -ef |grep gunicorn

    суть в том, чтобы получить список процесс_ид все воркеров гуникорна, и также получить свой процесс_ид текущего воркера
    если текущий воркер является первым в списке (т.е. минимальным) - то в нем запускается листенер
    '''
    try:
        if _list is None:
            _list = '/home/fyuzd/process.sh'
        process = subprocess.Popen(_list,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   )
        stdout, _ = process.communicate()
        list_stdout = str(stdout).split('united-help ')
        pids = []
        for _stdout in list_stdout:
            _s = _stdout.split()
            if len(_s) > 1 and str(_s[1]) != '1':
                pids.append(_s[0])

        pid = os.getpid()
        pids.sort()
        print(f'{pid=}')
        print(f'{pids=}')
        listener = False
        if len(pids) > 0 and str(pid) == pids[0]:
            listener = True
        elif len(pids) == 0:
            listener = True
        return listener
    except Exception as e:
        print(e)
        # если возник ексепшн, то скорее всего гуникорн не используется - существует только один воркер
        return True
