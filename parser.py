import subprocess
import json
from pathlib import Path
from decimal import Decimal
from typing import Any

def extract_images(video_url: str, name: str) -> list[str]:
    """
    video_url: input/videos/pigeon.mp4
    """
    output_folder = Path("input/images/pigeon")
    output_folder.mkdir(parents=True, exist_ok=True)


    cmd = ["ffmpeg",
           "-i", 
           video_url,
            str(output_folder / "img%04d.png")
           ]
    # Call ffmpeg and exports into folder of images.
    subprocess.run(cmd)

    image_paths = sorted(output_folder.glob("img*.png"))

    image_path_strs = [str(image_path_str) for image_path_str in image_paths]

    return image_path_strs

def extract_metadata(video_url: str, name: str) -> dict:
    """
    video_url: input/videos/pigeon.mp4
    """
    output_path = Path(f"input/metadata/{name}.json")

    # Create a folder for the output if it doesn't already exist.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffprobe", 
        "-v", "quiet",
        "-print_format", 
        "json", 
        "-show_format", 
        video_url
    ]

    # Call ffprobe and export metadata to output path.
    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)

    metadata = json.loads(result.stdout)

    processed_metadata = _process_metadata(metadata=metadata)

    return processed_metadata

def _process_metadata(metadata: dict) -> dict[Any]:
    format = metadata["format"]

    creation_time = format["tags"]["creation_time"]

    location = format["tags"]["location"]
    latitude, longitude = _parse_location(location=location)

    return {
        "creation_time": creation_time, 
        "latitude": latitude, 
        "longitude": longitude
        }
    

def _parse_location(location: str) -> tuple[Decimal, Decimal]:
    """
    location = "+51.5162-000.1402/"
    """
    coord_str = location.strip('/')

    # Skip the first +- and find the second sign.
    for i in range(1, len(coord_str)):
        if coord_str[i] in '+-':
            latitude = Decimal(coord_str[:i])
            longitude = Decimal(coord_str[i:])
            return latitude, longitude
    
    raise ValueError("Invalid coordinate format")

def process_video(video_url: str, name: str):
    images = extract_images(video_url=video_url, name=name)
    metadata = extract_metadata(video_url=video_url, name=name)

    for image in images:
        # Call Claudio.
        print("Processed image - uploading to db...")


process_video(video_url="input/videos/pigeon.mp4", name="pigeon")