import subprocess
import json
import os

from pathlib import Path
from decimal import Decimal
from typing import Any


def process_videos(video_directory: str) -> dict:
    """
    - Extracts a video into a folder of images
    - Extracts relevant metadata for each video and stores it in each
    image folder as a .json file
    """
    video_files = os.listdir(video_directory)

    video_urls = [
        os.path.join(video_directory, file)
        for file in video_files
        if file.lower().endswith((".mp4", ".mov"))
    ]

    for video_url in video_urls:
        _get_sighting_data(video_url=video_url)


def _get_sighting_data(video_url: str) -> dict:
    metadata = _extract_metadata(video_url=video_url)

    _extract_images(video_url=video_url, metadata=metadata)

    return metadata


def _extract_images(video_url: str, metadata: dict) -> list[str]:
    """
    video_url: input/videos/pigeon.mp4
    """
    time_spotted = metadata["time_spotted"]
    output_folder = Path(f"input/images/{time_spotted}")
    output_folder.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i",
        video_url,
        "-vf",
        "fps=1",
        str(output_folder / "img%04d.png"),
    ]
    # Call ffmpeg and exports into folder of images.
    subprocess.run(cmd)


def _extract_metadata(video_url: str) -> dict:
    """
    video_url: input/videos/pigeon.mp4
    """

    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_url]

    # Call ffprobe and export metadata to output path.
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    metadata = json.loads(result.stdout)

    processed_metadata = _process_metadata(metadata=metadata)
    return processed_metadata


def _process_metadata(metadata: dict) -> dict[Any]:
    format = metadata["format"]

    time_spotted = format["tags"]["creation_time"]

    location = format["tags"]["location"]
    latitude, longitude = _parse_location(location=location)

    metadata = {
        "time_spotted": time_spotted,
        "latitude": latitude,
        "longitude": longitude,
    }

    output_path = Path(f"input/images/{time_spotted}/metadata.json")
    # Create a folder for the output if it doesn't already exist.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as file:
        json.dump(metadata, file)

    return metadata


def _parse_location(location: str) -> tuple[str, str]:
    """
    location = "+51.5162-000.1402/"
    """
    coord_str = location.strip("/")

    # Skip the first +- and find the second sign.
    for i in range(1, len(coord_str)):
        if coord_str[i] in "+-":
            latitude = coord_str[:i]
            longitude = coord_str[i:]
            return latitude, longitude

    raise ValueError("Invalid coordinate format")
