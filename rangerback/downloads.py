import os
import requests
import zipfile
from requests.exceptions import ChunkedEncodingError, ConnectionError
import time
import re
import pathlib
from yt_dlp import YoutubeDL
import subprocess

def download(url, **kwargs):
    if kwargs.get("dir", None) == None:
        dl_location = os.path.join(os.getcwd(), os.path.basename(url))
    else:
        dl_location = os.path.join(kwargs.get("dir"), os.path.basename(url))
    
    if _is_youtube_video_regex(url):
        dl_location = dl_youtube_video(url, os.path.dirname(dl_location))
    elif _is_peertube_video_regex(url):
        dl_location = dl_peertube_video(url, os.path.dirname(dl_location))
    else:
        _download_online_file(url, dl_location, kwargs.get("range", None))
    
    return dl_location

class QuietLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

def dl_peertube_video(url, path):
    final_file = None

    def hook(d):
        nonlocal final_file
        if d['status'] == 'finished':
            # Construct final merged filename manually
            base = pathlib.Path(d['filename']).with_suffix('')  # remove extension
            final_file = str(base.with_suffix('.mp4'))  # add correct merged format

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'progress_hooks': [hook],
        'logger': QuietLogger(),
        'quiet': True, 
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return final_file

def dl_youtube_video(url, path):
    path = pathlib.Path(path)
    path.mkdir(parents=True, exist_ok=True)

    # This will hold the output file name
    output_template = path / '%(title)s.%(ext)s'
    final_file = None

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': str(output_template),
        'merge_output_format': 'mkv',  # use .mkv to preserve all streams
        'quiet': True,
        'no_warnings': True,
        'logger': None,  # Disables yt-dlp's internal logger completely
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = pathlib.Path(ydl.prepare_filename(info)).with_suffix('.mkv')

    # Re-encode to a truly compatible MP4 (H.264 + AAC)
    reencoded_file = downloaded_file.with_suffix('.mp4')

    # Suppress ffmpeg output by redirecting stdout and stderr to DEVNULL
    subprocess.run([
        'ffmpeg',
        '-y',
        '-i', str(downloaded_file),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-movflags', '+faststart',
        str(reencoded_file)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Optionally delete original
    downloaded_file.unlink()

    return str(reencoded_file)

def _is_youtube_video_regex(url):
    YOUTUBE_VIDEO_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    )
    return bool(YOUTUBE_VIDEO_REGEX.match(url))

def _is_peertube_video_regex(url):
    PEERTUBE_REGEX_1 = re.compile(
        r'https?://[^/]+/videos/watch/[\w\-]+'
    )
    PEERTUBE_REGEX_2 = re.compile(
        r'https?://[^/]+/w/[\w\-]+'
    )
    PEERTUBE_REGEX_3 = re.compile(
        r'https?://[^/]+/videos/embed/[\w\-]+'
    )

    return bool(PEERTUBE_REGEX_1.match(url) or PEERTUBE_REGEX_2.match(url) or PEERTUBE_REGEX_3.match(url))
    
# def _download_online_file(url, path, range):
#     """Download a file to base colab directory."""
#     if range == None:
#         response = requests.get(url, stream=True)
#     else:
#         response = requests.get(url, headers={'Range': f'bytes={range}'}, stream=True)
#     if response.status_code == 206 or response.status_code == 200:
#         with open(path, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=1024):
#                 file.write(chunk)
def _download_online_file(url, path, range=None, retries=3, backoff=2):
    """Download a file to base colab directory with retries on failures."""
    headers = {'Range': f'bytes={range}'} if range else {}
    
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code in (200, 206):
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive chunks
                            file.write(chunk)
                return  # Success!
            else:
                print(f"Unexpected status code: {response.status_code}")
                break  # Don't retry on bad status codes
        except (ChunkedEncodingError, ConnectionError, requests.exceptions.ReadTimeout) as e:
            attempt += 1
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < retries:
                time.sleep(backoff * attempt)
            else:
                raise  # Let the final failure raise an error

def download_zip(url, path):
    """Download a zip file and unpack it's contents at the given path (a folder of the filename will be created)."""
    
    # Download file:
    response = requests.get(url)
    temp_zip = os.path.join(path, os.path.basename(url))
    with open(temp_zip, 'wb') as file:
        file.write(response.content)

    # Create the output folder:
    if os.path.isdir(path) == False:
        os.makedirs(path)

    # Unzip:
    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
        zip_ref.extractall(path)
    
    # Remove temporary zip file:
    os.remove(temp_zip)