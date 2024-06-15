import logging

from celery import shared_task

from .services import AnimalServices

logger = logging.getLogger(__name__)
animal_service = AnimalServices()


@shared_task
def make_animal_video(animal_id: int, force: bool = False):
    logger.info('make_animal_video - started')
    animal = animal_service.prepare_animal_for_processing(animal_id, force)
    if not animal:
        return

    logger.info(f'make_animal_video - animal: {animal}')
    new_video_file, processing_status = animal_service.process_animal(animal)
    logger.info(f'make_animal_video - processing is finished: {animal}')

    animal_service.finnish_animal_processing(animal_id, new_video_file, processing_status)


@shared_task
def auto_process_animals():
    logger.info('auto_process_animals - started')
    animal_ids = animal_service.fetch_animals_for_auto_processing()
    logger.info(f'auto_process_animals - animals: {animal_ids}')
    for animal_id in animal_ids:
        make_animal_video.delay(animal_id)
    logger.info('auto_process_animals - finished')
