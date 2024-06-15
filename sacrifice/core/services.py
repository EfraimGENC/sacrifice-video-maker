import os
import logging
import traceback
import tempfile

from django.db import transaction
from django.db.models import Q
from django.core.files import File

from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip


from .models import Animal
from .enums import AnimalStatus, LogoPosition
from .utils import get_random_string

logger = logging.getLogger(__name__)

non_video_query = Q(original_video='') | Q(original_video__isnull=True)


class VideoConcatenationService:
    @staticmethod
    def composite_image(clip, content_path, height=None, position='center', mt=0, mr=0, mb=0, ml=0):
        logger.info(f'composite_image - content_path: {content_path} {position}')
        frame = (
            ImageClip(content_path)
            .set_duration(clip.duration)
            .resize(height=height if height else clip.h)
            .margin(top=mt, right=mr, bottom=mb, left=ml, opacity=0)
            .set_position(position)
        )
        return CompositeVideoClip([clip, frame])

    @staticmethod
    def concatenate_clips(clips, method="chain"):
        if method not in ["chain", "compose"]:
            raise ValueError('Invalid method. Must be one of "chain" or "compose"')

        if method == "chain":
            min_height = min([c.h for c in clips])
            min_width = min([c.w for c in clips])
            logger.info(f'Clips will be resized to {min_width}x{min_height}')
            clips = [c.resize((min_width, min_height)) for c in clips]

        final_clip = concatenate_videoclips(clips, method)

        # Geçici bir dosya oluştur
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_video_path = temp_video.name
        temp_video.close()  # Dosyayı kapatmadan önce yolu al ve ardından dosyayı kapat

        # Videoyu geçici dosyaya yaz
        final_clip.write_videofile(temp_video_path, codec='libx264', audio_codec='aac')

        # Geçici dosyayı Django'nun FileField'ına yüklemek için aç
        f = open(temp_video_path, 'rb')
        django_file = File(f, name='processed_video.mp4')

        for clip in clips:
            clip.close()

        return django_file, temp_video_path

    @staticmethod
    def concatenate_sacrifice_clips(video_path, cover_path, intro_path, outro_path, frame_path, logo_path, logo_height,
                                    logo_position, logo_margin_top, logo_margin_right, logo_margin_bottom,
                                    logo_margin_left):
        # Intro
        intro_clip = VideoFileClip(intro_path) if intro_path else None

        # Cover
        cover_image = ImageClip(cover_path).set_duration(2) if cover_path else None

        # Clip
        sacrifice_clip = VideoFileClip(video_path)
        if frame_path:
            sacrifice_clip = VideoConcatenationService.composite_image(sacrifice_clip, frame_path)
        if logo_path:
            sacrifice_clip = VideoConcatenationService.composite_image(
                sacrifice_clip, logo_path, height=logo_height, position=logo_position,
                mt=logo_margin_top, mr=logo_margin_right, mb=logo_margin_bottom, ml=logo_margin_left)

        # Outro
        outro_clip = VideoFileClip(outro_path) if outro_path else None

        clips = [intro_clip, cover_image, sacrifice_clip, outro_clip]
        clips = [clip for clip in clips if clip is not None]

        processed_video_file, temp_video_path = VideoConcatenationService.concatenate_clips(clips)

        return processed_video_file, temp_video_path


class AnimalServices:
    @staticmethod
    def prepare_animal_for_processing(animal_id, force=False) -> Animal | None:
        with transaction.atomic():
            filter_query = Q(id=animal_id) & ~Q(status=AnimalStatus.PROCESSING)
            if not force:
                filter_query &= Q(status=AnimalStatus.UNPROCESSED)

            animal = Animal.objects\
                .select_for_update(skip_locked=True)\
                .filter(filter_query)\
                .exclude(non_video_query)\
                .first()

            if animal is None:
                return None

            animal.status = AnimalStatus.PROCESSING
            animal.save()
            return animal

    @staticmethod
    def finnish_animal_processing(animal_id, processed_video_file, temp_video_path, processing_status):
        with transaction.atomic():
            animal = Animal.objects.select_for_update().get(pk=animal_id)
            animal.status = processing_status
            if processed_video_file:
                animal.processed_video.save('processed_video.mp4', processed_video_file, save=False)
                processed_video_file.close()
            if temp_video_path:
                os.remove(temp_video_path)
            animal.save()

    @staticmethod
    def fetch_animals_for_auto_processing() -> list[int]:
        available_animals_query = Q(status=AnimalStatus.UNPROCESSED, season__auto_process=True)
        return Animal.objects.filter(available_animals_query).exclude(non_video_query).values_list('id', flat=True)

    @staticmethod
    def process_animal(animal: Animal):
        processed_video_file: File | None = None
        temp_video_path: str | None = None
        try:
            logger.info(f'make_animal_video - processing: {animal}')

            processed_video_file, temp_video_path = VideoConcatenationService.concatenate_sacrifice_clips(
                animal.original_video.path,
                animal.cover.path if animal.cover else None,
                animal.season.intro.path if animal.season.intro else None,
                animal.season.outro.path if animal.season.outro else None,
                animal.season.frame.path if animal.season.frame else None,
                animal.season.logo.path if animal.season.logo else None,
                animal.season.logo_height,
                LogoPosition.convert_for_moviepy(animal.season.logo_position),
                animal.season.logo_margin_top,
                animal.season.logo_margin_right,
                animal.season.logo_margin_bottom,
                animal.season.logo_margin_left
            )
        except Exception as e:
            logger.info(f'make_animal_video - error {e} {animal}:')
            traceback.print_exc()
            processing_status = AnimalStatus.ERROR
        else:
            processing_status = AnimalStatus.PROCESSED

        return processed_video_file, temp_video_path, processing_status
