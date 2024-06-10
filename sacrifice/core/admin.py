from django.contrib import admin
from .models import Season, Animal, Share


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    pass


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    pass

