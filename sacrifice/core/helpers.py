from django.db import transaction

from .models import Animal
from .enums import AnimalStatus


def fetch_animal_for_processing():
    animal = Animal.objects.select_for_update().filter(video__isnull=False,
                                                       status=AnimalStatus.UNPROCESSED,
                                                       season__process=True).last()
    if animal:
        with transaction.atomic():
            animal.status = AnimalStatus.PROCESSING
            animal.save()
        return animal
