import glob
import sys

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4

from joblib import Parallel, delayed

from error import log_error
from utils import fileSeperator, print_b, file_to_array, \
    print_g, print_r, extSeperator

import pickle

tag_parse_error = "tag parsing error"


def build_song(title, artist):
    return f"{title} {fileSeperator} {artist}"


def mutugen_handle(ext_path):
    [ext, path] = ext_path.split(extSeperator)
    match ext:
        case 'mp3':
            try:
                tags = EasyID3(path)
                return build_song(tags['title'][0], tags['artist'][0])
            except:
                log_error(tag_parse_error, f"error parsing {ext} for {path}")
        case 'm4a':
            try:
                tags = MP4(path)
                # \xa9nam = title, \xa9ART = artist
                return build_song(tags['\xa9nam'][0], tags['\xa9ART'][0])
            except:
                log_error(tag_parse_error, f"error parsing {ext} for {path}")
        case _:
            log_error(tag_parse_error, f"extension not implemented or not supported for {ext} for {path}")
            return ""


# Reads song files from the specified folder
def read_song_files(folder_path, local_song_path, extensions, skip_read):

    if skip_read:
        read_in = file_to_array(local_song_path)
        if len(read_in) != 0:
            return read_in

    local_paths = [f"{ext}{extSeperator}{g}"
                   for ext in extensions for g in glob.glob(folder_path + f'/*.{ext}')]

    print_b(f'# of files are {len(local_paths)}')

    songs = Parallel(n_jobs=-1)(delayed(mutugen_handle)(path) for path in local_paths)

    f = open(local_song_path, "w", encoding="utf-8")
    for s in songs:
        f.write(s + '\n')
    f.close()

    if len(songs) == len(local_paths):
        print_g(f"all songs gotten {len(songs)} == {len(local_paths)}")
    else:
        print_r(f"failed to get all songs gotten {len(songs)} != {len(local_paths)}")

    return songs
