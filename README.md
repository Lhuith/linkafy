## Linkafy ##

Small python app that process's local song files and attempts to match against your spotify account

Grabs your spotify likes list, sorts the unique ones out then matches
with local version of your songs, currently I enforce a **hard** matching 1:1 and use 
fuzzy matching (#rapidfuzz) to find and clean tags of songs that didn't match

There's also a conversion step that converts songs in specified directory (mp3 -> m4a) and such

Libs used (many thanks):
 - pydup
 - mutegen
 - pillow
 - rapidfuzz
 - joblib
 - spotipy