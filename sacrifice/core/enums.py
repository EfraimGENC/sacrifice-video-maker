from django.db import models
from django.utils.translation import gettext_lazy as _


class ShareType(models.IntegerChoices):
    VACIP = 1, _("Vacip")
    SUKUR = 2, _("Şükür")
    AKIKA = 3, _("Akika")
    ADAK = 4, _("Adak")


class LogoPosition(models.TextChoices):
    LEFT_TOP = 'left-top', _("Sol Üst")
    LEFT_BOTTOM = 'left-bottom', _("Sol Alt")
    RIGHT_TOP = 'right-top', _("Sağ Üst")
    RIGHT_BOTTOM = 'right-bottom', _("Sağ Alt")
    CENTER = 'center', _("Orta")


class AnimalStatus(models.IntegerChoices):
    UNPROCESSED = 1, _("İşlenmemiş")
    PROCESSING = 2, _("İşleniyor")
    PROCESSED = 3, _("İşlenmiş")
    ERROR = 4, _("Hata")
