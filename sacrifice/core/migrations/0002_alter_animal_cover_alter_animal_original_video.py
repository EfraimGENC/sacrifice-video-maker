# Generated by Django 5.0.6 on 2024-06-15 21:54

import core.utils
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='cover',
            field=models.ImageField(blank=True, help_text='Kapak resmi', null=True, upload_to=core.utils.animal_video_path_cover, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp'])], verbose_name='Kapak'),
        ),
        migrations.AlterField(
            model_name='animal',
            name='original_video',
            field=models.FileField(blank=True, help_text='Orijinal kurban kesim videosu', null=True, upload_to=core.utils.animal_video_path_original, verbose_name='Orjinal Video'),
        ),
    ]
