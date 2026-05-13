from fastapi import APIRouter, Form
import os
import shutil
import uuid
import subprocess
import csv
from .downloads import download
router = APIRouter()

@router.post("/local-processing/audio-id")
async def identify_birds(audio_src: str = Form(...)):
    uid = str(uuid.uuid4())

    TEMP_DIR = os.path.join(os.getcwd(), ".TEMP")
    os.makedirs(TEMP_DIR, exist_ok = True)

    output_path = os.path.join(TEMP_DIR, f"{uid}.csv")

    input_path = download(audio_src, dir = TEMP_DIR)
    input_path = video_to_wav(input_path)

    try:
        subprocess.run(
            [   
                os.path.join(os.getcwd(), "venv", "bin", "python"), 
                os.path.join(os.getcwd(), "workers", "ornithology_birdnet_worker.py"), 
                input_path, output_path],
            check = True,
            timeout = 120
        )

        result = read_csv(output_path)

    finally:
        shutil.rmtree(os.path.join(os.getcwd(), ".TEMP"))

    return {"predictions_csv": result}

def video_to_wav(input_path, output_path=None, sample_rate=44100):
    """
    Convert a video file to a WAV audio file using ffmpeg.

    Args:
        input_path (str): Path to the input video file
        output_path (str, optional): Path to output WAV file
        sample_rate (int): Audio sample rate (default 44100 Hz)

    Returns:
        str: Path to the generated WAV file
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".wav"

    command = [
        "ffmpeg",
        "-y",                 # overwrite output
        "-i", input_path,     # input file
        "-vn",                # no video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", str(sample_rate), # sample rate
        "-ac", "2",           # stereo
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

    return output_path

def read_csv(path : str, delimiter : str = ',', quotechar : str = '"') -> list[list]:
    """Read a csv file and return 2D list."""
    if os.path.isfile(path):
        if os.path.splitext(path)[1].lower() == ".csv":
            content = []
            with open(path, 'r') as f:
                csv_reader = csv.reader(f, delimiter = delimiter, quotechar = quotechar)
                for row in csv_reader:
                    content.append(row)
            return content
        else:
            print(f"{path} is not a csv file.")
            return None
    else:
        print(f"{path} doesn't exist.")
        return None