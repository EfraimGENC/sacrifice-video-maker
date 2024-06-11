from .models import Animal


def fetch_unprocessed_animal():
    return Animal.objects.filter(processed=False).first()
