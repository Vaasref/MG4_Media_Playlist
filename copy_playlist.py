import os
import shutil
import sys
from lxml import etree
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TRCK, TT2
import urllib.parse
import re
from tqdm import tqdm

def clean_path_list(file_paths):
    for index, file_path in enumerate(file_paths):
        file_path = file_path.replace('file://', '/')
        file_path = file_path.replace('//', '/')
        file_paths[index] = urllib.parse.unquote(file_path) # Decode encoded special characters
    return file_paths

def parse_m3u(m3u_path):
    with open(m3u_path, 'r') as file:
        lines = file.readlines()
        # Get the absolute path of the playlist file
        playlist_dir = os.path.dirname(os.path.abspath(m3u_path))
        # Filter lines that are not comments
        path_list = [f"{playlist_dir}/{line.strip()}" for line in lines if not line.startswith('#')]
        path_list = clean_path_list(path_list)
        return path_list

def parse_xspf(xspf_path):
    tree = etree.parse(xspf_path)
    root = tree.getroot()
    # Namespace handling for XSPF files
    ns = {'xspf': 'http://xspf.org/ns/0/'}
    locations = root.findall('.//xspf:location', namespaces=ns)
    path_list = [location.text for location in locations]
    path_list = clean_path_list(path_list)
    return path_list

def update_metadata(file_path, track_number, total_tracks):
    try:
        audio = MP3(file_path)
        audio_tags = audio.tags
    except ID3NoHeaderError:
        audio = MP3(file_path)
        audio_tags = ID3()
        audio.tags = audio_tags
    current_title = os.path.basename(file_path)
    if 'TIT2' in audio_tags:
        current_title = audio_tags['TIT2'].text[0]
    leading_zeros = len(str(total_tracks))
    new_title = f"{track_number:0{leading_zeros}d} {current_title}"
    audio_tags.add(TT2(encoding=0, text=new_title)) # Encoding 0 for ISO-8859-1, it's needed because the MG4 infortainment system always reads the title as ISO-8859-1
    audio_tags.add(TRCK(encoding=0, text=str(track_number)))
    audio.save()

def get_new_filename(file_path, track_number, total_tracks):
    file_name = os.path.basename(file_path)

    # Regex to remove any track number prefix anything with digit and followed with space, dot, or dash
    cleaned_file_name = re.sub(r'^[0-9-_ ]*[-_ ]+', '', file_name)

    leading_zeros = len(str(total_tracks))
    formatted_file_name = f"{track_number:0{leading_zeros}d} {cleaned_file_name}"
    return formatted_file_name

def copy_files(file_paths, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    total_tracks = len(file_paths)
    longer_path = len(max(file_paths, key=len))
    
    progress = tqdm(file_paths, desc="Copying modified files", unit="file", unit_scale=True)
    for index, file_path in enumerate(progress):
        if os.path.isfile(file_path):
            file_name = get_new_filename(file_path, index+1, total_tracks)
            new_file_path = os.path.join(destination_folder, file_name)
            shutil.copy(file_path, new_file_path)
            update_metadata(new_file_path, index+1, total_tracks)
            tqdm.write(f'{file_path:<{longer_path}} to {new_file_path}')
        else:
            tqdm.write(f'File not found: {file_path}')

def main(playlist_path, destination_folder):
    if not os.path.isfile(playlist_path):
        print(f"Playlist file not found: {playlist_path}")
        return
    
    file_ext = os.path.splitext(playlist_path)[1].lower()
    if file_ext == '.m3u' or file_ext == '.m3u8':
        audio_files = parse_m3u(playlist_path)
    elif file_ext == '.xspf':
        audio_files = parse_xspf(playlist_path)
    else:
        print("Unsupported playlist format. Only M3U, M3U8, and XSPF are supported.")
        return
    
    copy_files(audio_files, destination_folder)
    print("Playlist copied and modified completed.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <playlist_path> <destination_folder>")
    else:
        playlist_path = sys.argv[1]
        destination_folder = sys.argv[2]
        main(playlist_path, destination_folder)
