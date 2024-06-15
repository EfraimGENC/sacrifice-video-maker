import os
import logging
import traceback
from pathlib import Path

from django.db import transaction
from django.db.models import Q
from django.conf import settings

from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip


from .models import Animal
from .enums import AnimalStatus, LogoPosition

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
    def concatenate_clips(clips, video_path, method="chain", export_format='mp4'):
        if method not in ["chain", "compose"]:
            raise ValueError('Invalid method. Must be one of "chain" or "compose"')

        video_path = Path(video_path)
        if video_path.suffix.lower() != f'.{export_format}':
            video_path = video_path.with_suffix(f'.{export_format}')
        video_path = str(video_path)

        if method == "chain":
            min_height = min([c.h for c in clips])
            min_width = min([c.w for c in clips])
            logger.info(f'Clips will be resized to {min_width}x{min_height}')
            clips = [c.resize((min_width, min_height)) for c in clips]

        final_clip = concatenate_videoclips(clips, method)
        final_clip.write_videofile(video_path, fps=30, threads=8, preset='ultrafast', audio_codec='aac')

        for clip in clips:
            clip.close()

        return video_path

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

        new_video_path = VideoConcatenationService.concatenate_clips(clips, video_path)

        return new_video_path


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
    def finnish_animal_processing(animal_id, new_video_path, processing_status):
        with transaction.atomic():
            animal = Animal.objects.select_for_update().get(pk=animal_id)
            animal.status = processing_status
            if new_video_path is not None and processing_status == AnimalStatus.PROCESSED:
                relative_file_path = os.path.relpath(new_video_path, settings.MEDIA_ROOT)
                animal.original_video.name = relative_file_path
            animal.save()

    @staticmethod
    def fetch_animals_for_auto_processing() -> list[int]:
        available_animals_query = Q(status=AnimalStatus.UNPROCESSED, season__auto_process=True)
        return Animal.objects.filter(available_animals_query).exclude(non_video_query).values_list('id', flat=True)

    @staticmethod
    def process_animal(animal: Animal):
        new_video_path: str | None = None
        try:
            logger.info(f'make_animal_video - processing: {animal}')

            new_video_path = VideoConcatenationService.concatenate_sacrifice_clips(
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

        return new_video_path, processing_status
