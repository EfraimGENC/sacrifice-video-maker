from django.db import models
from django.utils.translation import gettext_lazy as _


class ShareType(models.IntegerChoices):
    VACIP = 1, _("Vacip")
    SUKUR = 2, _("Şükür")
    AKIKA = 3, _("Akika")
    ADAK = 4, _("Adak")
