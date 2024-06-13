import phonenumbers
from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from .models import Season, Animal, Share


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'process')
    search_fields = ('year', 'name')


@admin.register(Animal)
class AnimalAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'status', 'season', 'has_cover_image')
    search_fields = ('code', 'season__year')
    autocomplete_fields = ('season',)

    @admin.display(description='name')
    def name(self, obj):
        return f'{obj.season.year}/{obj.code}'

    @admin.display(description='Kapak Görseli Mevcut', boolean=True)
    def has_cover_image(self, obj):
        return bool(obj.cover)


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('name', 'animal', 'formatted_phone', 'type', 'by')
    list_filter = ('type', 'created_at', 'animal__season__year')
    search_fields = ('name', 'phone', 'by', 'animal__code')
    autocomplete_fields = ('animal',)

    @admin.display(description='Telefon')
    def formatted_phone(self, obj):
        if obj.phone:
            return phonenumbers.format_number(obj.phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
