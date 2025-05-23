import anthropic
import os
import pandas as pd
import psycopg2
import base64
import ast


LOCAL_DB_NAME = "hackathon_wildlife_tracker_db"

INPUT_FILE_PATH = os.getcwd() + "/input/images/"


OUTPUT_FILE_PATH = os.getcwd() + "/output/my_output.json"


def analyse_directory(directory=INPUT_FILE_PATH):
    response_data = []
    for sighting in os.listdir(directory):
        sighting = os.path.join(directory, sighting)
        for filename in os.listdir(sighting):
            filename = os.path.join(sighting, filename)
            with open(filename, "rb") as f:
                BASE64_IMAGE_DATA = base64.standard_b64encode(f.read()).decode("utf-8")
                image_type = "image/" + filename.split(".")[-1]
                if image_type == "image/jpg":
                    image_type = "image/jpeg"

            result = call_claude(image_data=BASE64_IMAGE_DATA, image_type=image_type)

            response_data.append(ast.literal_eval(result.text))

    return response_data


def call_claude(image_data, image_type):
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
                        "text": "What animal is in this image? Please give the response as a dictionary in the following format: {'species': <species>, 'genus': <genus>, 'common_name': <name>}. Do not include any descriptions or explanations. Do not include any line breaks or new lines. Do not include any other text. Just give the dictionary.",
                    },
                ],
            }
        ],
    )
    print(message.content)
    return message.content[0]


response_data = analyse_directory()

common_name = []
genus = []
species = []
for sighting in response_data:
    common_name.append(sighting["common_name"])
    genus.append(sighting["genus"])
    species.append(sighting["species"])

df = pd.DataFrame({"name": common_name, "species": species, "genus": genus})
df.to_csv("output.csv", index=False)


conn = psycopg2.connect(
    dbname=LOCAL_DB_NAME,
    user="postgres",
    password="hello",
    host="localhost",
    port="5432",
)

with conn:
    with conn.cursor() as curs:
        for row in df.itertuples():
            curs.execute(
                "INSERT INTO wildlife (name, species, genus) VALUES (%s, %s, %s)",
                (row.name, row.species, row.genus),
            )
conn.commit()
conn.close()
