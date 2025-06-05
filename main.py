import re

from rapidfuzz import fuzz as rapidfuzz
from unidecode import unidecode

from conversion import music_convert, music_rename
from env import local_playlist_id, unique_playlist_id, local_music_path, removed_playlist_id
from local import read_song_files
from spotify import write_spotify_liked_to_file, update_playlist, search_for_song
from utils import print_c, print_r, file_to_array, print_b, fileSeperator, print_g, print_p
from wth import wth_print_w, wth_print_p, wth_print_y, wth_print_r, wth_print_g, set_what


def is_mix(a):
    return "remix" in a


# not to be confused with has_feet, which always returns true (˵¯͒〰¯͒˵)
def has_feat(a):
    return "feat " in a


def get_artists(a):
    return a.split(fileSeperator)[1].strip()


def get_title(a):
    return a.split(fileSeperator)[0].strip()


def get_remixer(a):
    split = a.split("remix")
    return split[0].strip()


# self-explanatory, complete waste of time to comment on, and so I will not, in fact
# I will continue to state how irrelevant it is to comment on this one function
# but also this takes a new list of artists and ... & a & b & c's appends to back of artist string
def add_to_artist(new_artists, artist, a):
    for artist_to_add in new_artists:
        if unidecode(artist_to_add) not in unidecode(artist):
            wth_print_w(f" - {artist_to_add} not in {artist}", a)
            artist += f" & {artist_to_add}"
    return artist


# just last minute sort, since either the local is dumb, or spotify is dumb with ordering
# but forced reordering removes that problem
def clean_artist(artist):
    # why lord
    artist = artist.replace("featuring", "&")

    artists = artist.split(" & ")
    artists.sort()
    return ' & '.join([a for a in artists])


# self explanatory, handle . my . junk . dammit
# also it will take title, and any relevant parts of string and tries to extract artists
# after all that fun we put title back together with whatever we don't need and peace out
def handle_title_junk(title, part, a):
    artists = []
    for junk_split in [" - ", "[", "("]:
        split_by_junk = part.split(junk_split)
        if len(split_by_junk) > 1:
            # SHOULD be feat. artist in this side
            part = split_by_junk[0].strip()
            wth_print_p(f" ---- {part}", a)
            # other junk, that if not an artist, we slap back on title
            # with remixes we keep the xyz remix part, to help keep uniqueness of song
            other = split_by_junk[1].strip()
            if is_mix(other):
                # grab remix artist and restitch xyz remix back to tile
                wth_print_y(f" ---- {other}", a)
                wth_print_y(f" ---- {get_remixer(other)}", a)
                title += f"{junk_split}{other}"
                artists.append(get_remixer(other))
            else:
                # add this back into title
                title += f"{junk_split}{other}"
                wth_print_r(f" --- \"{other}\" in {a}", a)
    # return restitched title, the relevant part we were after and any artists we slurped up
    # this would a combination of feat and remix artists
    return title, part, artists


def normalize(a):
    # first completely remove redundant phrases and lil bits, it ain't a bonus track to us :( </3
    for r in ["original mix", "original", "?", "'", ".",
              " mix", "single version" "version", "bonus track", "explicit"]:
        a = a.replace(r.lower(), "")

    # replace/normalize any similar characters since noone wants to agree on anything
    for r, c in {"; ": " & ", ", ": " & ", " and ": " & ",
                 "(with": "(feat", "ft": "feat", "- with ": "- feat "}.items():
        a = a.replace(r, c)

    title = get_title(a)
    wth_print_r(f" - {title}", a)
    artist = get_artists(a)

    # check for feature artists
    # title should be first, if not ... well good going -_-
    # artist on the right, checking first if it's not already there (like feat. or ... with)
    # extra stuff like: "xyz remix", (live), (triple j 1823 remastered vocal double mix), stitched back to title
    if has_feat(title):
        split_by_feat = title.split("feat")
        title = split_by_feat[0]

        artists_to_add = []
        for feat_a in split_by_feat[1:]:

            # pick threw the title split off the feat. point, removing feat. in the process
            new_title, new_part, remix_artists = handle_title_junk(title, feat_a, a)
            title = new_title
            feat_a = new_part

            for r in remix_artists:
                artists_to_add.append(r)

            feat_a = feat_a.strip()
            # replace ands/withs to & to collectively split later
            for r, c in {" and ": " & "}.items():
                if r in feat_a:
                    wth_print_r(f" ---- {feat_a} was nasty", a)
                feat_a = feat_a.replace(r, c)

            # split now by normalized & then clean up feature artist and add to artist on the right
            for feat_a_amp_split in feat_a.split(" & "):
                feat_a_amp_split = re.sub("\(|\)|\[|\]", "", feat_a_amp_split)
                feat_a_amp_split = feat_a_amp_split.replace("  ", " ")
                feat_a_amp_split = feat_a_amp_split.strip()

                artists_to_add.append(feat_a_amp_split)

        # add now back to artist finally, achieving peace and unity and a sense of purpose
        new_artist = add_to_artist(artists_to_add, artist, a)
        artist = new_artist
    # handling non-feat. but still remixed titles
    # since we preserve xyz remix, we just grab the artists and leave title as is
    elif is_mix(title):
        _, _, rem_artists = handle_title_junk(title, title, a)
        new_artist = add_to_artist(rem_artists, artist, a)
        artist = new_artist
    # slap em back in the old artists string
    artist = clean_artist(artist)

    # reg-lob that sucker back together
    a = f"{title} {fileSeperator} {artist}"
    wth_print_w(f"{a}", a)

    # final PROCESS step, just completely clears everything redundant
    a = re.sub("\]|\[|\)|\(|-|:|&|,|!|;|\/|'|’", "", a).strip()

    # change certain characters to normalize titles
    for r, c in {"  ": " ", " iii ": " 3 ", " feat ": " ", " ii ": " two "}.items():
        a = a.replace(r, c)
    wth_print_w(f" ----- {a}", a)
    # clear out any spaces cause im lazy
    for r, c in {"  ": " ", "   ": " "}.items():
        a = a.replace(r, c)
    wth_print_w(f" ------ {a}", a)

    return a


def process(a):
    return unidecode(normalize(a.lower()))


convert = True
rename = False

def compare_song_maps(ignore_list, spotifile_dict, local_songs):
    print_p(f"{len(local_songs) - len(ignore_list)} to be linked!")
    print()
    no_match, match_ids, count = [], [], 0
    for local_song in local_songs:
        if local_song in ignore_list:
            count += 1
            continue

        normalized_local_song = process(local_song)
        wth_print_g(f" l:{normalized_local_song}", normalized_local_song)
        match = False
        for spotify_song, spotify_id in spotifile_dict.items():
            normalized_spotify_song = process(spotify_song)

            # where all the magic really happens, the lil oompa-loompa hard string matcher
            # I would use fuzzy matching but its results are not worth using without needing to check
            # instead it's better to use as a tool to tell you if your getting warmer and just clean up
            # your stank music library, I say this with love
            if normalized_local_song == normalized_spotify_song:
                print_g(f"{normalized_spotify_song} == {normalized_local_song}")
                # remove on match, faster search times, and fun to pop things
                spotifile_dict.pop(spotify_song)
                count += 1
                match = True
                match_ids.append(spotify_id)
                break
                # can replace the hard string matcher, but better to use this to see what songs
                # are not tagged/formatted correctly and knowing for sure, again with love I swear
            elif rapidfuzz.ratio(normalized_local_song, normalized_spotify_song) > 95:
                print_b(f"s:{normalized_spotify_song}\nl:{normalized_local_song}")
        if not match:
            no_match.append([local_song, normalized_local_song])

    # a hard no-no, songs must all be accounted for before loading to spotify
    # this can be removed if you are ok with "good enough"
    if len(local_songs) != count:
        print_r(f"{len(local_songs) - count} didn't match")
        for no in no_match:
            print_r(f"{no[0]}\n -- {no[1]}")
        return [], []
    else:
        # and the sausage is done
        print_g(f"all {count} songs found and linked!")
        return match_ids, list(spotifile_dict.values())

if __name__ == "__main__":
    print_c(f"Running Spotify Local/App cleanup")

    not_in_spotify = file_to_array('input/not_in_spotify.txt')
    print_r(f"spotify shame amount: {len(not_in_spotify)}")

    # convert all songs in a given path to specified format
    # this attempts to keep tags/cover art as close to original as possible
    if convert:
        print("converting!")
        # music_convert(local_music_path, ['m4a', 'mp3', 'flac'], 'm4a')
    elif rename:
        print("renaming!")
        music_rename(local_music_path, ['m4a', 'mp3', 'flac'])
    else:
        print("organizing!!!")
        # search local folder and compare with unique
        local_songs_map = read_song_files(
            local_music_path, "output/local_songs.txt", ['mp3', 'm4a'], False)

        # get and write spotify liked to file
        spotify_song_map = write_spotify_liked_to_file(
            1, 50, 5, "output/liked_songs.txt", "output/unique_liked_songs.txt")

        # string in checker, look at wth.py, checks both spotify and local songs for certain title during search
        # and prints out the matching/normalization process
        set_what("")
        # compare and return
        track_ids, removed_track_ids = compare_song_maps(not_in_spotify, spotify_song_map, local_songs_map)

        if len(removed_track_ids) != 0:
            update_playlist(removed_playlist_id, removed_track_ids)

        # create playlist with match songs
        # only if all songs were accounted for (cleaned, matched and excluded in not_in_spotify.txt)
        if len(track_ids) != 0:
            update_playlist(local_playlist_id, track_ids, 5)

        # if len(unique_liked_track_ids) != 0:
        #     if len(unique_liked_track_ids) != 0:
        #         update_playlist(unique_playlist_id, unique_liked_track_ids)
