import math
import threading
import urllib
import urllib.parse
from unidecode import unidecode

from env import username, sp
from error import log_error
from mutegen import build_song
from threads import NewThread
from utils import fileSeperator, print_b, file_to_array, print_g, print_r, print_c, dicSeperator, file_to_dict, print_y, \
    print_p, print_w

spotify_fetch_error = "spotify fetch error"


# oompa loompa job that does the actual processing of spotify json madness
def read_spotify_results(start, end, pageSize):
    tracks = []
    for i in range(end - start):
        for item in sp.current_user_saved_tracks(pageSize, (i + start) * pageSize)['items']:
            track = item['track']
            title = track['name']
            if title == "":
                log_error(spotify_fetch_error, f"track name is empty!! ~ spotify:track:{track['id']} \n{track}")
                continue
            artists = ' & '.join(n['name'] for n in track['artists'])
            if artists == "":
                log_error(spotify_fetch_error, f"artist array is empty!! ~ spotify:track:{track['id']} \n{track}")
                continue

            tracks.append([f"{title} {fileSeperator} {artists}", track['id']])
    print_b("thread done")
    return tracks


# grab users liked song list (can be generalized maybe) and dumps/stores song names and ids to a
# unique and normal liked dict/list/file that we use to compare with later and extract ids stored in said dict
def write_spotify_liked_to_file(cap, page_size, total_threads, write_to_liked_path, write_to_unique):
    likeSpotifyList = file_to_array(write_to_liked_path)
    spotifyUniqueSongListFromFile = file_to_dict(write_to_unique)

    # magic black box that gives you everything you ever wanted
    # from the users spotify liked playlist that is
    results = sp.current_user_saved_tracks()
    total = results['total']

    # don't need to update cache
    # this is safer to use/check as since the data on spotify's said hardly changes
    # usually only the length of lists
    if len(likeSpotifyList) == total:
        print_g(f"SPOTIFY CACHE DOESN'T NEED UPDATING! {len(likeSpotifyList)} == {total}")
        # return unique list, not the full list, as we need to compare what we don't have
        return spotifyUniqueSongListFromFile
    else:
        print_r(f"SPOTIFY NEED UPDATING! {len(likeSpotifyList)} != {total}")

    # break work out into "sets" as reading from spotify is limited to 50 results
    print_r(f"Total songs is: {total}")
    sets = math.ceil(results['total'] / page_size)
    print_r(f"total page sets ({page_size}) are: {sets}")

    # break the work set size across total threads provided
    workSize = math.ceil(sets / total_threads)
    print_r(f"total work/{total_threads} is {workSize}")

    threads = []
    # sound out the little monkey squad to get them sweet sweet likes songs and ids
    for i in range(total_threads):
        threads.append(NewThread(target=read_spotify_results,
                                 args=(i * workSize, (i + 1) * workSize, page_size)))

    # begins a quantum entanglement process, where it processes the question "Life, the Universe,
    # and Everything?" its 42, and then it starts the above threads
    for t in threads:
        t.start()

    results = []
    # not 100% how to safely do this, look in threads.py, where it constructs helper functions to have a thread
    # return its value, which I append to the above result array to further process below, what could possibly go wrong
    for t in threads:
        results += t.join()

    if len(results) == total:
        print_g(f"all songs gotten {len(results)} == {total}")
    else:
        print_r(f"failed to get all songs gotten {len(results)} != {total}")

    f = open(write_to_liked_path, "w", encoding="utf-8")
    uniqueMap = dict()
    for song in results:
        # add songs to list to make sure we don't have duplicates (hopefully)
        uniqueMap[song[0]] = song[1]
        # write out to write_to_liked_path txt file,
        f.write(song[0] + '\n')
    f.close()

    print_c(f"total of unique songs gotten {len(uniqueMap)}")

    f = open(write_to_unique, "w", encoding="utf-8")
    for song, song_id in uniqueMap.items():
        f.write(f"{song} {dicSeperator} {song_id}\n")
    f.close()

    return uniqueMap


lock = threading.Lock()


# lil oompa-oompa thread worker job that takes slices from track_ids and dumps to playlist
# please note the max slice size is 100, anymore then that and spotify calls the http police
def add_songs(start, end, pl_id, track_ids, page_size):
    lock.acquire()
    for i in range(end - start):
        s = (i + start) * page_size
        e = s + page_size

        if e > len(track_ids):
            e = len(track_ids)
        sp.playlist_add_items(pl_id, ["spotify:track:" + trackId for trackId in track_ids[s:e]])
    lock.release()
    print_b(f"thread ended")


# if so inclined, generate a playlist from code, but outside runtime tracking of the id, I wish thy luck, or im dumb
# fun fact: spotify doesn't tell you if a playlist is deleted as far as im aware
def create_play_list(name, description):
    return sp.user_playlist_create(username, name, description=description)


# update a playlist, using playlist id and track_ids[] passed in, also an option
# to change tread count and page size
def update_playlist(playlist_id, track_ids, total_threads=5, page_size=100):
    sp.playlist_replace_items(playlist_id, [])
    print_g(f"")
    print_b(f" -- # of songs to add {len(track_ids)} to {playlist_id}")

    if playlist_id == '':
        log_error("blank playlist id", "something went wrong when getting playlist ID")
        return

    sets = math.ceil(len(track_ids) / page_size)
    workSize = math.ceil(sets / total_threads)
    print_y(f"total sets:{sets} work over threads:{total_threads} is {workSize}")

    threads = []
    # break out into threads here
    for i in range(total_threads):
        end = (i + 1) * workSize
        if end > sets:
            end = sets

        threads.append(
            NewThread(target=add_songs, args=(i * workSize, end, playlist_id, track_ids, page_size)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def query_builder(title, artist):
    # https://developer.spotify.com/documentation/web-api/reference/search
    # ':' = %3A, ' ' = %20
    # note: %2520 is encoding for '%20' as in ' ' -> %20 -> '%2520'
    # I dont know if the example is wrong, but it would suggest they are doing double encoding
    # or got the example wrong or my brain smol
    # example: track%3ADoxy%2520artist%3AMiles%2520Davis

    extra = []
    if 'remix' in title.lower():
        extra.append('remix ')

    query = f"{' '.join([e for e in extra])}track:{title} artist:{artist}".replace(' ', '%20')
    return urllib.parse.quote(query)


def search_for_song(songs_list):
    for song in songs_list:
        [title, artist] = song.split(fileSeperator)
        q = query_builder(title.strip(), artist.strip())

        res = sp.search(q, type="track", limit=20, offset=0)

        print_w(q)
        print_b(build_song(title, artist))
        for t in res['tracks']['items']:
            print_p(f"'title' -- {t['name']}")
        # for t in res['artists']['items']:
        #     print_g(f"'artist' -- {t['name']}")
        # artists = []

        # for a in res['artists']:
        #     artists.append(a['name'])

        # print_p(f" -- {build_song(res['name'], ', '.join([a for a in artists]))}")
