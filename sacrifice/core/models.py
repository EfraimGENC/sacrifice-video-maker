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
    name = models.CharField(max_length=127)
    year = models.PositiveIntegerField(choices=year_choices(), default=current_year)

    def __str__(self):
        return f'{self.year} ({self.name})'

    class Meta(BaseModel.Meta):
        verbose_name = _('Season')
        verbose_name_plural = _('Seasons')


class Animal(BaseModel):
    season = models.ForeignKey(Season, on_delete=models.PROTECT, default=current_year)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta(BaseModel.Meta):
        verbose_name = _('Animal')
        verbose_name_plural = _('Animals')
        constraints = [
            models.UniqueConstraint(fields=['season', 'code'], name='unique_animal_code_per_season')
        ]


class Share(BaseModel):
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    name = models.CharField(max_length=127)
    phone = PhoneNumberField(blank=True)
    type = models.PositiveIntegerField(choices=ShareType, default=ShareType.VACIP)
    by = models.CharField(max_length=127)

    def __str__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Share')
        verbose_name_plural = _('Shares')
