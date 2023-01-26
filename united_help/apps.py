from django.apps import AppConfig


class UnitedHelpConfig(AppConfig):
    name = 'united_help'

    def ready(self):
        from united_help.scheduler import init_scheduler
        init_scheduler()
