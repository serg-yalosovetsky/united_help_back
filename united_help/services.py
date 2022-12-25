from firebase_admin import messaging


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