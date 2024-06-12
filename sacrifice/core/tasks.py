from django.db import transaction

from celery import shared_task

from .models import Animal
from .enums import AnimalStatus
from .helpers import fetch_animal_for_processing
from .video_concatenation import concatenate_sacrifice_clips


@shared_task
def make_animal_video():
    animal = fetch_animal_for_processing()
    if not animal:
        return

    concatenate_sacrifice_clips(
        animal.video.path,
        animal.cover.path if animal.cover else None,
        animal.season.intro.path if animal.season.intro else None,
        animal.season.outro.path if animal.season.outro else None,
        animal.season.frame.path if animal.season.frame else None,
        animal.season.logo.path if animal.season.logo else None,
        animal.season.logo_height,
        animal.season.logo_position,
        animal.season.logo_margin_top,
        animal.season.logo_margin_right,
        animal.season.logo_margin_bottom,
        animal.season.logo_margin_left
    )

    animal = Animal.objects.select_for_update().get(pk=animal.pk)
    with transaction.atomic():
        animal.status = AnimalStatus.PROCESSING
        animal.save()
