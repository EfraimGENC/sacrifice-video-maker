from django.db import transaction
from django.db.models import Q

from .models import Animal
from .enums import AnimalStatus


def fetch_animal_for_processing():
    with transaction.atomic():
        animal = Animal.objects.select_for_update(skip_locked=True).filter(
            status=AnimalStatus.UNPROCESSED, season__process=True).exclude(Q(video='') | Q(video__isnull=True)).last()
        if animal:
            animal.status = AnimalStatus.PROCESSING
            animal.save()
            return animal
