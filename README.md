# MG4 Audio Playlist Copier

## Description

The MG4 infotainment system is pretty dumb when it comes to reading audio files. It Actually reads the track titles and sort them alphabetically with no regard for the track number or the file name.

This script address that issue by modifying the track metadata and file name of the tracks in a playlist to force the MG4 to keep the same exact order.

I made the script for myself, if there is demand I might make it easier to use for non python inclined users. 

## MG4's Infotainment System Tips

Here are some tips and info I gathered while tinkering with the car's infotainment system.

Usage tips:
- If you use the USB stick for other purpose than music, hide the folder by naming them with a leading dot (`.example`) anything with a leading dot should be ignored by the car track search.
- Reducing the number of tracks visible by hiding your full library might help the car not block when searching for tracks.
- USB sticks might not be read if they are already plugged in when you start the car, unplug it and plug it in again should work.
- If your USB stick is not recognized in one port, try the other, you never know.
- If the car get stuck reading a USB stick the USB port used will probably become unusable for media until the next power cycle, but the other port should work.
- If the sound randomly glitch, it is probably a faulty USB stick.
- exFAT works fine.

Technical tips:
- The car seems to read metadata as encoded in ISO-8859-1, any other encoding with mutagen leads to mojibake on the car.

## Features

- Read .m3u, .m3u8 and .xspf playlists
- Copy playlist to given destination path
- Not user friendly
- No GUI
- May work on Windows

## Installation

Install required packaged:
```python -m pip install -r requirements.txt```

## Usage

```python copy_playlist.py <playlist_path> <destination_folder>```