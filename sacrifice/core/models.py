import io
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.files import File

from PIL import Image, ImageCms
from phonenumber_field.modelfields import PhoneNumberField

from .enums import ShareType, LogoPosition, AnimalStatus
from .validators import FileSizeValidator
from .utils import (year_choices, current_year, animal_video_path_original, animal_video_path_processed,
                    animal_video_path_cover)


class BaseModel(models.Model):
    uuid = models.UUIDField(editable=False, unique=True, db_index=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class ProcessingSettings(models.Model):
    auto_process = models.BooleanField(
        _('Otomatik İşleme'),
        default=False,
        help_text=_('Kurban videoları arkaplanda düzenli olarak işlensin mi? \
        İşaretlerseniz, "işlenmemiş" durumundaki videolar otomatik olarak arkaplanda işlenir.')
    )
    intro = models.FileField(
        _('Giriş'),
        upload_to='intros',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm']),
            FileSizeValidator(100)
        ],
        help_text=_('Giriş videosu. Maksimum dosya boyutu 100 MB.')
    )
    outro = models.FileField(
        _('Çıkış'),
        upload_to='outros',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm']),
            FileSizeValidator(100)
        ],
        help_text=_('Çıkış videosu. Maksimum dosya boyutu 100 MB.')
    )
    frame = models.ImageField(
        _('Çerçeve'),
        upload_to='frames',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
            FileSizeValidator(100)
        ],
        help_text=_('Çerçeve resmi. Maksimum dosya boyutu 100 MB.')
    )
    logo = models.ImageField(
        _('Logo'),
        upload_to='logos',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
            FileSizeValidator(100)
        ],
        help_text=_('Logo resmi. Maksimum dosya boyutu 100 MB.'),
    )
    logo_height = models.PositiveIntegerField(
        _('Logo Yükseklik'),
        default=100,
        help_text=_('Logo yüksekliği')
    )
    logo_position = models.CharField(
        _('Logo Pozisyon'),
        max_length=15,
        choices=LogoPosition,
        default=LogoPosition.LEFT_TOP,
        help_text=_('Logo pozisyonu')
    )
    logo_margin_right = models.PositiveSmallIntegerField(
        _('Logo Sağ Kenar Boşluğu'),
        default=0,
        help_text=_('Logo sağ kenar boşluğu')
    )
    logo_margin_bottom = models.PositiveSmallIntegerField(
        _('Logo Alt Kenar Boşluğu'),
        default=0,
        help_text=_('Logo alt kenar boşluğu')
    )
    logo_margin_left = models.PositiveSmallIntegerField(
        _('Logo Sol Kenar Boşluğu'),
        default=20,
        help_text=_('Logo sol kenar boşluğu')
    )
    logo_margin_top = models.PositiveSmallIntegerField(
        _('Logo Üst Kenar Boşluğu'),
        default=20,
        help_text=_('Logo üst kenar boşluğu')
    )

    class Meta:
        abstract = True


class Season(BaseModel, ProcessingSettings):
    name = models.CharField(_('İsim'), max_length=127)
    year = models.PositiveIntegerField(_('Yıl'), choices=year_choices(), default=current_year)

    def __str__(self):
        return f'{self.year} ({self.name})'

    class Meta(BaseModel.Meta):
        verbose_name = _('Sezon')
        verbose_name_plural = _('Sezonlar')


class Animal(BaseModel):
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name='animals',
        default=current_year,
        verbose_name=_('Sezon')
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Kod/Numara')
    )
    cover = models.ImageField(
        _('Kapak'),
        upload_to=animal_video_path_cover,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
            FileSizeValidator(100)
        ],
        help_text=_('Kapak resmi. Maksimum dosya boyutu 100 MB.')
    )
    status = models.PositiveSmallIntegerField(
        default=AnimalStatus.UNPROCESSED,
        verbose_name=_('Durum'),
        choices=AnimalStatus,
        help_text=_('Video işlenme durumu')
    )
    original_video = models.FileField(
        _('Orjinal Video'),
        upload_to=animal_video_path_original,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov']),
            FileSizeValidator(100)
        ],
        help_text=_('Orijinal kurban kesim videosu. Maksimum dosya boyutu 100 MB.'),
    )
    processed_video = models.FileField(
        _('İşlenmiş Video'),
        upload_to=animal_video_path_processed,
        blank=True,
        null=True,
        editable=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov']),
            FileSizeValidator(100)
        ],
        help_text=_('İşlenmiş kurban kesim videosu. Maksimum dosya boyutu 100 MB.')
    )

    def __str__(self):
        return f'{self.season.year}/{self.code}'

    class Meta(BaseModel.Meta):
        verbose_name = _('Hayvan')
        verbose_name_plural = _('Hayvanlar')
        constraints = [
            models.UniqueConstraint(fields=['season', 'code'], name='unique_animal_code_per_season')
        ]

    def save(self, *args, **kwargs):
        if self.cover:
            self.cover = self.convert_image_to_srgb(self.cover)
        super().save(*args, **kwargs)

    @staticmethod
    def convert_image_to_srgb(image_field):
        image = Image.open(image_field)

        if image.mode in ['RGB', 'RGBA']:
            return image_field

        image = image.convert('RGB')

        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        image_file = File(image_io, name=image_field.name)

        return image_file


class Share(BaseModel):
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT, related_name='shares', verbose_name=_('Hayvan'))
    name = models.CharField(max_length=127, verbose_name=_('İsim'))
    phone = PhoneNumberField(blank=True, null=True, verbose_name=_('Telefon'))
    type = models.PositiveIntegerField(choices=ShareType, default=ShareType.VACIP, verbose_name=_('Türü'))
    by = models.CharField(max_length=127, verbose_name=_('Vesile'))

    def __str__(self):
        return self.name

    class Meta(BaseModel.Meta):
        verbose_name = _('Hisse')
        verbose_name_plural = _('Hisseler')
