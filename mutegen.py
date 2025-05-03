from mutagen.id3 import ID3
from mutagen.mp4 import MP4

from error import log_error
from utils import fileSeperator, fileNameSeperator


def build_file_name(title, artist):
    return f"{artist} {fileNameSeperator} {title}"

def build_song(title, artist):
    return f"{title} {fileSeperator} {artist}"

# splits on ext and returns a sanely (yea I know why) keyed/value dict
def mutey_get_tag(file, ext):
    title = []
    artists = []
    cover = b''
    match ext:
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
                # print(cover[0])
        case _:
            log_error("extension case error", f"extension {ext} not handled for tag reading")
    return {
        'title': title,
        'artists': artists,
        'cover': cover,
    }
