from firebase_admin import messaging
from rest_framework.utils import json

from united_help.models import User


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
