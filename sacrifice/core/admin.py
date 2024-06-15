import phonenumbers
from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages


from .models import Season, Animal, Share
from .tasks import make_animal_video


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'auto_process')
    search_fields = ('year', 'name')


@admin.register(Animal)
class AnimalAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'status', 'season', 'has_cover_image')
    list_filter = ('status', 'created_at')
    readonly_fields = ('video_player',)
    search_fields = ('code', 'season__year')
    autocomplete_fields = ('season',)
    actions = ['process_video']

    @admin.display(description='name')
    def name(self, obj):
        return f'{obj.season.year}/{obj.code}'

    @admin.display(description='Kapak Görseli Mevcut', boolean=True)
    def has_cover_image(self, obj):
        return bool(obj.cover)

    @admin.display(description='Video Oynatıcı')
    def video_player(self, obj):
        if obj.original_video:
            return format_html(
                '<video id="{}" height="300" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>',
                obj.uuid,
                obj.original_video.url
            )
        return "No video available"

    def process_video(self, request, queryset):
        ids = queryset.values_list('id', flat=True).order_by('id') or None
        if not ids:
            self.message_user(request, _("Seçili hayvan içerisinde işlenmeye uygun olan bulunamadı."), messages.ERROR)
            return
        for animal_id in ids:
            make_animal_video.delay(animal_id, force=True)
        self.message_user(request, _(f'{len(ids)} kurban videosu başarıyla işlendi.'), messages.SUCCESS)


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
