import os
import logging
import traceback

from django.db import transaction
from django.conf import settings

from celery import shared_task

from .models import Animal
from .enums import AnimalStatus, LogoPosition
from .helpers import fetch_animal_for_processing
from .video_concatenation import concatenate_sacrifice_clips


logger = logging.getLogger(__name__)


@shared_task
def make_animal_video():
    logger.info('make_animal_video - started')
    animal = fetch_animal_for_processing()
    logger.info(f'make_animal_video - animal: {animal}')
    if not animal:
        return

    new_video_path = None
    try:
        logger.info(f'make_animal_video - processing: {animal}')

        new_video_path = concatenate_sacrifice_clips(
            animal.video.path,
            animal.cover.path if animal.cover else None,
            animal.season.intro.path if animal.season.intro else None,
            animal.season.outro.path if animal.season.outro else None,
            animal.season.frame.path if animal.season.frame else None,
            animal.season.logo.path if animal.season.logo else None,
            animal.season.logo_height,
            LogoPosition.convert_for_moviepy(animal.season.logo_position),
            animal.season.logo_margin_top,
            animal.season.logo_margin_right,
            animal.season.logo_margin_bottom,
            animal.season.logo_margin_left
        )
    except Exception as e:
        logger.info(f'make_animal_video - error {e} {animal}:')
        traceback.print_exc()
        processing_status = AnimalStatus.ERROR
    else:
        processing_status = AnimalStatus.PROCESSED

    logger.info(f'make_animal_video - processing is finished: {animal}')
    with transaction.atomic():
        animal = Animal.objects.select_for_update().get(pk=animal.pk)
        animal.status = processing_status
        if new_video_path is not None and processing_status == AnimalStatus.PROCESSED:
            relative_file_path = os.path.relpath(new_video_path, settings.MEDIA_ROOT)
            logger.info(f'make_animal_video - new video path: {relative_file_path}')
            animal.video.name = relative_file_path
        animal.save()
        logger.info(f'make_animal_video - marked as processed: {animal}')
