from mutagen.id3 import ID3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from error import log_error
from utils import fileSeperator, fileNameSeperator, print_w


# build file name output (as opposed to the tags within the metadata)
def build_file_name(title, artist):
    return f"{artist} {fileNameSeperator} {title}"


# used and read within the app for sorting and matching
def build_song(title, artist):
    return f"{title} {fileSeperator} {artist}"


# splits on ext and returns a sanely (yea I know why) keyed/value dict
def mutey_get_tag(file, ext):
    title = []
    artists = []
    cover = b''
    match ext:
        case 'flac':
            tags = FLAC(file)
            title = tags['title']
            artists = tags['artist']
            if len(tags.pictures) != 0:
                cover = tags.pictures[0].data
        case 'mp3':
            tags = ID3(file)
            title = tags['TIT2'].text
            artists = tags['TPE1'].text
            if 'APIC:' in tags:
                cover = tags['APIC:'].data
        case 'm4a':
            tags = MP4(file)
            title = tags['\xa9nam']
            artists = tags['\xa9ART']
            if 'covr' in tags:
                cover = tags['covr'][0]
        case _:
            log_error("extension case error", f"extension {ext} not handled for tag reading")
    return {
        'title': title,
        'artists': artists,
        'cover': cover,
    }
