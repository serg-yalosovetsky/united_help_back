import datetime

from django.db.models import Q
from django.utils.timezone import make_aware

from united_help.models import Event, Profile
from datetime import date



from united_help.services import send_firebase_multiple_messages
from united_help.settings import BASE_URL
from united_help.views import finish_event
#
#
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#
#     # Executes every Monday morning at 7:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=0, minute=10,),
#         event_start_tomorrow.s(),
#     )
#     sender.add_periodic_task(300.0, event_finished.s(), name='check finished events')


# @shared_task
def event_start_tomorrow():
    print('event_start_tomorrow')
    tomorrow = make_aware(date.today() + datetime.timedelta(days=1))
    after_tomorrow = make_aware(date.today() + datetime.timedelta(days=2))
    events = Event.objects.filter(
        Q(active=True) & Q(start_time__range=(tomorrow, after_tomorrow))
    )
    for event in events:
        send_firebase_multiple_messages(
            f'Event {event.name} by {event.owner.organization} started tomorrow',
            f'Event planned from {event.start_time} to {event.end_time}',
            [participant.user for participant in event.participants],
            notify_type='start',
            to_profile=Profile.Roles.labels[event.to].capitalize(),
            event_id=event.id,
            image=f'{BASE_URL}{event.image.url}',
            event_name=event.name,
            actor_name=event.owner.user.username,
            actor_profile_id=event.owner.id,
        )
        send_firebase_multiple_messages(
            f'Your event {event.name} started tomorrow',
            f'Event planned from {event.start_time} to {event.end_time}',
            [event.owner.user],
            notify_type='start',
            to_profile=Profile.Roles.organizer.name.capitalize(),
            event_id=event.id,
            image=f'{BASE_URL}{event.image.url}',
            event_name=event.name,
            actor_name=event.owner.user.username,
            actor_profile_id=event.owner.id,
        )


# @shared_task
def event_finished():
    print('event_finished')
    now = make_aware(datetime.datetime.now())
    now_plus_6_min = make_aware(datetime.datetime.now() + datetime.timedelta(minutes=6))
    events = Event.objects.filter(
        Q(active=True) & Q(end_time__range=(now, now_plus_6_min))
    )
    for event in events:
        finish_event(event, event_url=f'{BASE_URL}{event.image.url}')
