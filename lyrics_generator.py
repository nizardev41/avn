import os
import whisper
from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator


def transcribe_audio(audio_path):
    """Transcribe the audio file using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result['segments']


def translate_to_malayalam(text):
    """Translate a piece of text to Malayalam."""
    translator = Translator()
    translated = translator.translate(text, dest='ml')
    return translated.text


def create_video_with_lyrics(audio_path, segments):
    """Create a lyric video showing each line at the right time."""
    audio_clip = AudioFileClip(audio_path)
    width, height = 1280, 720
    clips = []

    for seg in segments:
        start = seg['start']
        end = seg['end']
        text = translate_to_malayalam(seg['text'])
        txt_clip = TextClip(
            text,
            fontsize=40,
            color='white',
            size=(width - 100, None),
            method='caption',
        ).set_position(('center', 'bottom')).set_start(start).set_end(end)
        clips.append(txt_clip)

    video = CompositeVideoClip(clips, size=(width, height))
    video = video.set_audio(audio_clip)
    output_path = 'lyrics_video.mp4'
    video.write_videofile(output_path, fps=24)
    return output_path


def create_image_with_lyrics(segments):
    """Create an image showing the entire song's lyrics in Malayalam."""
    lyrics_ml = "\n".join(translate_to_malayalam(seg['text']) for seg in segments)
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype('arial.ttf', 24)
    except OSError:
        font = ImageFont.load_default()
    draw.multiline_text((10, 10), lyrics_ml, fill='white', font=font)
    output_path = 'lyrics_image.png'
    image.save(output_path)
    return output_path


def main(audio_path):
    segments = transcribe_audio(audio_path)
    video = create_video_with_lyrics(audio_path, segments)
    image = create_image_with_lyrics(segments)
    print(f"Video saved to {video}")
    print(f"Image saved to {image}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python lyrics_generator.py <audio_file>")
    else:
        main(sys.argv[1])
