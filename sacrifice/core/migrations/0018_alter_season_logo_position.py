# Generated by Django 5.0.6 on 2024-06-15 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_season_logo_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='logo_position',
            field=models.CharField(choices=[('left-top', 'Sol Üst'), ('left-bottom', 'Sol Alt'), ('right-top', 'Sağ Üst'), ('right-bottom', 'Sağ Alt'), ('center', 'Orta')], default='left-top', help_text='Logo pozisyonu', max_length=15, verbose_name='Logo Pozisyon'),
        ),
    ]
