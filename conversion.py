import base64
import glob
import io
import os

from PIL import Image
from joblib import Parallel, delayed
from mutagen.flac import Picture
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from pydub import AudioSegment
from pydub.utils import mediainfo

from error import log_error
from mutegen import mutey_get_tag, build_file_name
from utils import extSeperator, print_b


def build_file_path(output_folder, title, artist, to):
    return output_folder + "/" + f"{build_file_name(title, artist)}.{to}"


def pydub_handle(ext_path, folder_path, output_folder, to):
    [ext, path] = ext_path.split(extSeperator)
    print(ext, path, folder_path, output_folder, to)
    song = None
    new_name = path.replace(folder_path + "/", "")

    mutegen_tags = mutey_get_tag(path, ext)
    cover = mutegen_tags['cover']
    match ext:
        case 'mp3':
            song = AudioSegment.from_mp3(path)
        case 'm4a':
            song = AudioSegment.from_file(path, format='mp4')
        case _:
            log_error("extension case error", f"extension {ext} not handled for conversion")

    new_name = new_name.replace(f".{ext}", f".{to}")
    if song is None:
        log_error("song conversion failed", f"{path} failed to be read in")
        return

    # original tags, no album art :(
    tags = mediainfo(path).get('TAG', {})
    new_file_path = build_file_path(output_folder, tags['title'], tags['artist'], to)
    print(new_file_path)
    match to:
        case 'mp3':
            song.export(new_file_path, format=to, bitrate='320k', tags=tags)
            if cover != b'':
                img = Image.open(io.BytesIO(bytes(cover)))
                # https://stackoverflow.com/questions/47346399/how-do-i-add-cover-image-to-a-mp3-file-using-mutagen-in-python
                # tanks harshil9968
                song_mp3 = MP3(new_file_path, ID3=ID3)
                song_mp3.tags.add(
                    APIC(
                        encoding=3,  # 3 is for utf-8
                        mime=img.get_format_mimetype(),  # image/jpeg or image/png
                        type=3,  # 3 is for the cover image
                        desc=u'Cover',
                        data=cover
                    )
                )
                song_mp3.save()
        case 'ogg':
            song.export(new_file_path, format=to, bitrate='320k', tags=tags)
            if cover != b'':
                song_ogg = OggVorbis(new_file_path)
                img = Image.open(io.BytesIO(bytes(cover)))
                flac_image = Picture()
                flac_image.width = img.width
                flac_image.height = img.height
                flac_image.data = cover
                flac_image.mime = img.get_format_mimetype()
                flac_image.mode = img.mode
                flac_image.desc = 'Cover'
                flac_image.type = 3
                song_ogg["metadata_block_picture"] = [base64.b64encode(flac_image.write()).decode("ascii")]
                song_ogg.save()
        case 'm4a':
            song.export(new_file_path, format='ipod', bitrate='320k', tags=tags)

            # https://stackoverflow.com/questions/37897801/embedding-album-cover-in-mp4-file-using-mutagen
            # seriously thank you, Simon Kirsten
            if cover != b'':
                # grab new song and add cover picture back, im sure there's an easier way to do this
                song_mp4 = MP4(new_file_path)
                song_mp4['covr'] = [MP4Cover(bytes(cover), imageformat=MP4Cover.FORMAT_JPEG)]
                song_mp4.save()
        case _:
            log_error("to case error", f"conversion to extension {to} handled")


# takes a collection of music and to'afies them to your desired format, thus making them superior in every way
def music_convert(folder_path, extensions, to):
    # set output path if not exist already
    output_folder = folder_path + f"/Conversion/{to.lower()}"
    if os.path.exists(output_folder):
        print("output path exists")
    else:
        os.makedirs(output_folder)

    local_paths = [f"{ext}{extSeperator}{g}"
                   for ext in extensions for g in glob.glob(folder_path + f'/*.{ext}')]

    print_b(f'# of files are {len(local_paths)}')

    Parallel(n_jobs=-1)(delayed(pydub_handle)(path, folder_path, output_folder, to) for path in local_paths)
