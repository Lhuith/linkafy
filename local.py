import glob

from joblib import Parallel, delayed

from error import log_error
from mutegen import mutey_get_tag, build_song
from utils import print_b, file_to_array, \
    print_g, print_r, extSeperator

tag_parse_error = "tag parsing error"


def mutugen_handle(ext_path):
    [ext, path] = ext_path.split(extSeperator)
    try:
        tags = mutey_get_tag(path, ext)
        return build_song(tags['title'][0], tags['artists'][0])
    except:
        log_error(tag_parse_error, f"error parsing {ext} for {path}")
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
