from django.contrib import admin
from .models import Season, Animal, Share


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'process')


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'season', 'has_cover_image')

    @admin.display(description='name')
    def name(self, obj):
        return f'{obj.season.year}/{obj.code}'

    @admin.display(description='Kapak Görseli Mevcut', boolean=True)
    def has_cover_image(self, obj):
        return bool(obj.cover)


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('name', 'animal', 'phone', 'type', 'by')
    list_filter = ('type', 'created_at', 'animal__season__year')
    search_fields = ('name', 'phone', 'by', 'animal__code')
