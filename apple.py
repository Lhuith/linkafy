import subprocess

playlist_name = "TEST PLAYLIST"

script = f'''
tell application "Music"
    if not (exists user playlist "{playlist_name}") then
        make new user playlist with properties {{name:"{playlist_name}"}}
    end if

    set thePlaylist to user playlist "{playlist_name}"
end tell
'''
subprocess.run(["osascript", "-e", script])
