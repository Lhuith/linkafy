import os
from io import BytesIO

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

from mutagen.mp4 import MP4, MP4Cover
from pydub import AudioSegment
from mutagen.mp3 import MP3
from error import log_error
from mutegen import mutey_get_tag
from utils import get_files_by_ext, print_g, print_r
from pydub.utils import mediainfo
from PIL import Image


# takes a collection of music and oggafies them, this making them superior
def music_convert(folder_path, extensions, to):
    output_folder = folder_path + f"/Conversion/{to.lower()}"
    if os.path.exists(output_folder):
        print("output path exists")
    else:
        os.makedirs(output_folder)

    for ext in extensions:
        for file in get_files_by_ext(folder_path, [ext]):
            song = None
            new_name = file.replace(folder_path + "/", "")
            cover = b''
            match ext:
                case 'mp3':
                    mutegen_tags = mutey_get_tag(file, ext)
                    coverdata = mutegen_tags[]
                    song = AudioSegment.from_mp3(file)
                case 'm4a':
                    mutegen_tags = mutey_get_tag(file, ext)
                    song = AudioSegment.from_file(file, format='mp4')
                case _:
                    new_name = ''

                    log_error("extension case error", f"extension {ext} not handled for conversion")

            new_name = new_name.replace(f".{ext}", f".{to}")

            if song is None or new_name == '':
                log_error("song conversion failed", f"{file} failed to be read in")
                return

            # original tags, no album art :(
            tags = mediainfo(file).get('TAG', {})

            match to:
                case 'mp3':
                    print("to be added I swear")
                case 'ogg':
                    print("yay ogg")
                    # song.export(output_folder+"/"+new_name, format=to, bitrate='320k', tags=mediainfo(file).get('TAG', {}))
                case 'mp4':
                    print("yay mp4")
                    # song.export(output_folder + "/" + new_name, format=to, bitrate='320k', tags=mediainfo(file).get('TAG', {}))
                case 'm4a':
                    print("yay m4a")
                    song.export(output_folder + "/" + new_name, format='ipod', bitrate='320k', tags=tags)

                    song = MP4(output_folder + "/" + new_name)
                    # https://stackoverflow.com/questions/37897801/embedding-album-cover-in-mp4-file-using-mutagen
                    # seriously thank you, Simon Kirsten
                    if cover != b'':
                        song['covr'] = [MP4Cover(bytes(cover), imageformat=MP4Cover.FORMAT_JPEG)]
                    song.save()
                case _:
                    log_error("to case error", f"conversion to extension {to} not handled")
