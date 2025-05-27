import anthropic
import os
import pandas as pd
import psycopg2
import base64
import ast
import json
import parser
import supabase_setup


LOCAL_DB_NAME = "hackathon_wildlife_tracker_db"

VIDEO_FILE_PATH = "input/videos"

SIGHTING_FILE_PATH = os.getcwd() + "/input/images/"

OUTPUT_FILE_PATH = os.getcwd() + "/output/my_output.json"

conn = psycopg2.connect(
    dbname=LOCAL_DB_NAME,
    user="postgres",
    password="hello",
    host="localhost",
    port="5432",
)

with conn:
    with conn.cursor() as curs:
        curs.execute(
            """
                DROP TABLE IF EXISTS wildlife;
                CREATE TABLE IF NOT EXISTS wildlife (
                id SERIAL PRIMARY KEY,
                genus VARCHAR(255) NOT NULL,
                species VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                location VARCHAR(255),
                time_spotted TIMESTAMP
                );"""
        )
conn.commit()


def analyse_sightings(directory=SIGHTING_FILE_PATH):
    response_data = []

    for sighting in os.listdir(directory):
        sighting = os.path.join(directory, sighting)
        for filename in os.listdir(sighting):
            filename = os.path.join(sighting, filename)
            metadata = None
            if filename.endswith("metadata.json"):
                with open(filename, "r") as file:
                    metadata = json.load(file)
            else:
                with open(filename, "rb") as f:
                    print(f"\nProcessing {filename} \n")
                    BASE64_IMAGE_DATA = base64.standard_b64encode(f.read()).decode(
                        "utf-8"
                    )
                    image_type = "image/" + filename.split(".")[-1]
                    if image_type == "image/jpg":
                        image_type = "image/jpeg"

            if metadata is None:
                continue
                # raise ValueError("No metadata found for sighting")

            result = call_claude(
                image_data=BASE64_IMAGE_DATA, image_type=image_type, metadata=metadata
            )

            sighting_dict = ast.literal_eval(result.text)

            for key, value in metadata.items():
                sighting_dict[key] = value

            breakpoint()

            response_data.append(sighting_dict)

    return response_data


def call_claude(image_data, image_type, metadata):
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=1,
        system="You are a world-class ecologist and wildlife tracker. You are tasked with identifying the species of animals in a given image.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "What animal is in this image? Please give the response as a dictionary in the following format: {'species': <species>, 'genus': <genus>, 'name': <name>}. Do not include any descriptions or explanations. Do not include any line breaks or new lines. Do not include any other text. Just give the dictionary. "
                        + f"Use the following metadata from the image to guide your answer: latitude:{metadata['latitude']} , longitude:{metadata['longitude']}, creation_time: {metadata['creation_time']}.",
                    },
                ],
            }
        ],
    )
    print(message.content)
    return message.content[0]


parser.process_videos(video_directory=VIDEO_FILE_PATH)
response_data = analyse_sightings()

common_name = []
genus = []
species = []
for sighting in response_data:
    common_name.append(sighting["name"])
    genus.append(sighting["genus"])
    species.append(sighting["species"])

df = pd.DataFrame({"name": common_name, "species": species, "genus": genus})
df.to_csv("output.csv", index=False)
df.to_json("output.json", orient="records")
data_dict = df.to_dict(orient="records")


response = supabase_setup.supabase.table("wildlife").insert(response_data).execute()
print(response)
conn.close()
