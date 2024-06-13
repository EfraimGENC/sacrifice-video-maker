import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacrifice.settings.dev')
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise Exception(
        "DJANGO_SETTINGS_MODULE must be set in the environment before running celery."
    )

app = Celery('sacrifice')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# SCHEDULED PERIODIC TASKS
###############################################################################
app.conf.beat_schedule = {
    'make_animal_video': {
        'task': 'core.tasks.make_animal_video',
        'schedule': 10
    },
}