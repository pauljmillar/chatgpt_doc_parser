#!/usr/bin/env python
"""
Generic ChatGPT extraction script. Converts any input data to
any output JSON, as specified by a given JSON schema document.

This is dependent on the ChatGPT wrapper library:

https://github.com/mmabrouk/chatgpt-wrapper

Make sure to also run playwright install before running
this extractor script!
"""
from datetime import datetime
import json
import os
import re
import sys
import time
import boto3
import zipfile


from openai import OpenAI
#from chatgpt_wrapper import ChatGPT
from dotenv import load_dotenv

load_dotenv()

AWS_KEY = os.getenv("AWS_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")
GENERAL_SCHEMA = "general.schema.json"
AUTO_SERVICE_SCHEMA = "auto_service.schema.json"
AUTO_SALES_SCHEMA = "auto_sales.schema.json"
TELECOM_INTERNET_SCHEMA = "telecom_internet.schema.json"


def do_unzips():
    print("Starting unzipping")

    source_directory_path = 'images'
    initial_working_directory = os.getcwd()

    working_directory = os.path.join(initial_working_directory, source_directory_path)
    print(working_directory)
    os.chdir(working_directory)

    for file in os.listdir(working_directory):  # get the list of files
        #print(file)
        if zipfile.is_zipfile(file):  # if it is a zipfile, extract it
            print(file + " is zipfile...unzipping")
            with zipfile.ZipFile(file) as item:  # treat the file as a zip
                item.extractall()  # extract it in the working directory
            os.remove(file)

    os.chdir(initial_working_directory)
    print("Done unzipping")


def get_schema(industry):
    schema_filename = ""

    match industry:
        case "Auto-Sales":
            schema_filename = "auto_sales.schema.json"

        case "Auto-Service":
            schema_filename = "auto_service.schema.json"

        case "Telecom-Internet":
            schema_filename = "telecom_internet.schema.json"

        case _:
            print("The industry does not match.")

    print("Choosing schema: " + schema_filename)
    return schema_filename
'''
    #auto
    if any(re.findall(r'car |auto|truck |suv |motorcycle ', promo_text, re.IGNORECASE)) and any(re.findall(r'service| oil| tire|repair', promo_text, re.IGNORECASE)):
        schema_filename = "auto_service.schema.json"
    elif any(re.findall(r'lease|financing|sales', promo_text, re.IGNORECASE)) and any(re.findall(r'ford|chevy|chrysler|cadillac|dodge|gmc|hyundai|tesla|gm|jeep|lincoln|honda|nissan|audi|porsche|bmw|mercedes', promo_text, re.IGNORECASE)):
        schema_filename = "auto_sales.schema.json"
    #telecom
    elif any(re.findall(r'internet', promo_text, re.IGNORECASE)) and any(re.findall(r'speed|installation|service', promo_text, re.IGNORECASE)):
        schema_filename = "telecom_internet.schema.json"
    #else: Call chatgpt to figure out what category


'''

def call_chatgpt(client, prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Provide output in valid JSON"},
            {"role": "user", "content": prompt}
        ]
    )
    # prompt, response = scrape_via_prompt(chat, page_text, schema)
    response = chat_completion.choices[0].message.content
    # print(response)
    return response


def analyze_texts():

    print("Starting to make chatgpt calls ...")

    #get key from file, create client
    #f = open("openai_key.txt", "r")
    client = OpenAI(
        api_key=CHATGPT_KEY
    )

    # Specify the directory path
    ocr_directory_path = 'ocr'
    ocr_done_directory_path = 'ocr_done'
    json_result_directory_path = 'json_result'
    schema_directory_path = 'schema'


    # Loop through each file in the directory
    for filename in os.listdir(ocr_directory_path):
        # Check if the current item is a file
        if os.path.isfile(os.path.join(ocr_directory_path, filename)):
            # Do something with the file, for example, print its name
            print(filename)

            #read in ocr'd text
            with open(os.path.join(ocr_directory_path, filename), "r") as f:
                page_text = f.read()

            #read in json schema for general fields: to determine what industry the mail is for
            with open(os.path.join(schema_directory_path, GENERAL_SCHEMA), "r") as f:
                general_schema = json.load(f)

            #call chatgpt to figure out what type of text this is, and what schema to use
            prompt = f"```{page_text}```\n\nThe text above is promotional material. Determine which industry it is for, using the industries in the following JSON schema. Populate the other properties defined in the schema and provide your response in JSON that adheres to the schema.:\n\n```{general_schema}```"
            response=call_chatgpt(client, prompt)
            print(response)

            #lookup the schema file name
            wjdata = json.loads(response)
            print(wjdata['Offer Industry'])
            schema_filename = get_schema(wjdata['Offer Industry'])

            with open(os.path.join(schema_directory_path, schema_filename), "r") as f:
                schema = json.load(f)

            #call chatgppt a 2nd time to get the industry specific fields
            prompt = f"```{page_text}```\n\nWithin the given text, identify the Offer Description and the other attributes described in following JSON schema, and provide them in a JSON representation that strictly follows this schema:\n\n```{schema}```"
            response=call_chatgpt(client, prompt)
            print(response)

            print("Saving results to", os.path.join(json_result_directory_path, filename))
            with open(os.path.join(json_result_directory_path, filename), "w") as f:
                #f.write(json.dumps(results, indent=2))
                f.write(response)

            # if success, move file to done
            os.rename(os.path.join(ocr_directory_path, filename), os.path.join(ocr_done_directory_path, filename))
    print("Chatgpt calls complete.")

'''
            # determine which schema looking at text keywords
            schema_filename = get_schema(page_text)

            with open(os.path.join(schema_directory_path, schema_filename), "r") as f:
                schema = json.load(f)



            prompt = f"```{page_text}```\n\nWithin the given text, identify the Offer Description and the other attributes described in following JSON schema, and provide them in a JSON representation that strictly follows this schema:\n\n```{schema}```"


            print("Saving results to", os.path.join(json_result_directory_path, filename))
            with open(os.path.join(json_result_directory_path, filename), "w") as f:
                #f.write(json.dumps(results, indent=2))
                f.write(response)

            # if success, move file to done
            os.rename(os.path.join(ocr_directory_path, filename), os.path.join(ocr_done_directory_path, filename))
'''



def do_ocr():

    # Specify the directory path
    source_directory_path = 'images'
    done_directory_path = 'images_done'
    ocr_directory_path = 'ocr'

    #get key from file
    #f = open("aws_key.txt", "r")
    #aws_key=

    print("Starting to OCR files...")
    client = boto3.client('textract', region_name='us-west-2', aws_access_key_id='AKIASNRH2MGA4ZH72OFX',
                          aws_secret_access_key=AWS_KEY)

    # Loop through each file in the directory
    for filename in os.listdir(source_directory_path):
        # Check if the current item is a file
        if os.path.isfile(os.path.join(source_directory_path, filename)):
            # Do something with the file, for example, print its name
            print(filename)
            print(os.path.join(source_directory_path, filename))

            # determine output filename; if it ends in _22 or _2, save filename without these characters
            # and concatenate all; For example output from bigfile_1.png and bigfile_2.png would both get saved in bigfile
            if re.search("_[0-9]{1,2}\.(jpg|JPG|gif|GIF|doc|DOC|pdf|PDF|png|PNG)$", filename):
                output_filename = filename.rsplit('_', 1)[0] + ".txt"
            else:
                output_filename = filename
            print(output_filename)

            file1 = open(os.path.join(ocr_directory_path, output_filename), "a")  # append mode

            # image to read text from
            with open(os.path.join(source_directory_path, filename), 'rb') as file:
                img_bytes = file.read()
                #bytes_test = bytearray(img_test)
            img_text = client.detect_document_text(
                Document={"Bytes": img_bytes}
            )
            # Print detected text
            for item in img_text["Blocks"]:
                if item["BlockType"] == "LINE":
                    print(item["Text"])
                    file1.write(item["Text"] + "\n")

            # add a blank line between pages and close file
            file1.write("\n")
            file1.close()


            #if success, move file to done
            os.rename(os.path.join(source_directory_path, filename), os.path.join(done_directory_path, filename))
    print("OCR complete")



if __name__ == "__main__":

    #ocr on images in the ocr directory
    do_unzips()
    do_ocr()
    analyze_texts()




