import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from .enums import ShareType
from .utils import year_choices, current_year


class BaseModel(models.Model):
    uuid = models.UUIDField(editable=False, unique=True, db_index=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Season(BaseModel):
    name = models.CharField(_('İsim'), max_length=127)
    year = models.PositiveIntegerField(_('Yıl'), choices=year_choices(), default=current_year)

    def __str__(self):
        return f'{self.year} ({self.name})'

    class Meta(BaseModel.Meta):
        verbose_name = _('Sezon')
        verbose_name_plural = _('Sezonlar')


class Animal(BaseModel):
    season = models.ForeignKey(Season, on_delete=models.PROTECT, default=current_year, related_name='animals', verbose_name=_('Sezon'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Kod/Numara'))

    def __str__(self):
        return self.code

    class Meta(BaseModel.Meta):
        verbose_name = _('Hayvan')
        verbose_name_plural = _('Hayvanlar')
        constraints = [
            models.UniqueConstraint(fields=['season', 'code'], name='unique_animal_code_per_season')
        ]


class Share(BaseModel):
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name='shares', verbose_name=_('Hayvan'))
    name = models.CharField(max_length=127, verbose_name=_('İsim'))
    phone = PhoneNumberField(blank=True, verbose_name=_('Telefon'))
    type = models.PositiveIntegerField(choices=ShareType, default=ShareType.VACIP, verbose_name=_('Türü'))
    by = models.CharField(max_length=127, verbose_name=_('Kimin'))

    def __str__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Hisse')
        verbose_name_plural = _('Hisseler')
