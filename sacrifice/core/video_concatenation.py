from pathlib import Path

from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip


def composite_image(clip, content_path, height=None, position=('center',), mt=0, mr=0, mb=0, ml=0):
    frame = (ImageClip(content_path)
             .set_duration(clip.duration)
             .resize(height=height if height else clip.h)
             .margin(top=mt, right=mr, bottom=mb, left=ml, opacity=0)
             .set_position(position))
    return CompositeVideoClip([clip, frame])


def concatenate_clips(clips, video_path, method="chain", export_format='mp4'):
    if method not in ["chain", "compose"]:
        raise ValueError('Invalid method. Must be one of "chain" or "compose"')

    video_path = Path(video_path)
    if video_path.suffix.lower() != f'.{export_format}':
        video_path = video_path.with_suffix(f'.{export_format}')

    if method == "chain":
        min_height = min([c.h for c in clips])
        min_width = min([c.w for c in clips])
        clips = [c.resize(newsize=(min_width, min_height)) for c in clips]

    final_clip = concatenate_videoclips(clips, method)
    final_clip.write_videofile(video_path, fps=30, threads=8, preset='ultrafast', audio_codec='aac')

    for clip in clips:
        clip.close()


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
        sacrifice_clip = composite_image(sacrifice_clip, frame_path)
    if logo_path:
        sacrifice_clip = composite_image(sacrifice_clip, logo_path, height=logo_height, position=logo_position,
                                         mt=logo_margin_top, mr=logo_margin_right, mb=logo_margin_bottom,
                                         ml=logo_margin_left)

    # Outro
    outro_clip = VideoFileClip(outro_path) if outro_path else None

    clips = [intro_clip, cover_image, sacrifice_clip, outro_clip]
    clips = [clip for clip in clips if clip is not None]

    concatenate_clips(clips, video_path)
