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
import pandas as pd
from io import StringIO
from supabase import create_client, Client
from pathlib import Path
import scrubadub, scrubadub_spacy #, scrubadub_address

from openai import OpenAI
#from chatgpt_wrapper import ChatGPT
from dotenv import load_dotenv

class PIIReplacer(scrubadub.post_processors.PostProcessor):
    name = 'pii_replacer'
    def process_filth(self, filth_list):
        for filth in filth_list:
            # replacement_string is what the Filth will be replaced by
            #filth.replacement_string = 'PII'
            if filth.text.startswith(("1-800", "800-", "1-866", "866-", "1-888", "888-", "1-877", "877-", "1-855", "855-", "1-844", "844-", "1-833", "833-")):
                filth.replacement_string = '800 Telephone Number'
        return filth_list


load_dotenv()

AWS_KEY = os.getenv("AWS_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")
GPT_MODEL_35_TURBO = "gpt-3.5-turbo-0125"
GPT_MODEL_40_PREVIEW = "gpt-4-1106-preview"
OCR_DIRECTORY_PATH = 'ocr'
OCR_DONE_DIRECTORY_PATH = 'ocr_done'
JSON_RESULT_DIRECTORY_PATH = 'json_result'
SCHEMA_DIRECTORY_PATH = 'schema'
PROMPT_DIRECTORY_PATH = 'prompt'
total_cost = 0


def do_unzips():
    print("Checking for zip files to unzip")

    source_directory_path = 'images'
    initial_working_directory = os.getcwd()

    working_directory = os.path.join(initial_working_directory, source_directory_path)
    os.chdir(working_directory)

    for file in os.listdir(working_directory):  # get the list of files
        if zipfile.is_zipfile(file):  # if it is a zipfile, extract it
            print("Unzipping " + file + "..")
            with zipfile.ZipFile(file) as item:  # treat the file as a zip
                item.extractall()  # extract it in the working directory
            os.remove(file)

    os.chdir(initial_working_directory)


def get_prompts(industry, textBody):
    schemaFilename = ""
    seedAutoSales = 202402
    seedAutoService = 202403
    seedGeneral = 202401

    cnt=1
    promptDict={}

    for file in sorted(os.listdir(SCHEMA_DIRECTORY_PATH)):
        if file.startswith(industry.lower()):
            print(file)
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, file), "r") as f:
                schema = json.load(f)
            promptFile=file.split(".")[0] + ".txt"
            with open(os.path.join(PROMPT_DIRECTORY_PATH, promptFile), "r") as f:
                prompt = f.read()
            #print(prompt)
            #p = {'prompt': pro.format(schema=schema, textBody=textBody)}
            #print(p)
            promptDict[cnt] = {'prompt': prompt.format(schema=schema, textBody=textBody)}
            cnt+=1

    #print(promptDict)
    return promptDict, seedGeneral



def call_chatgpt(client, prompt, seed):

    gptModel = GPT_MODEL_35_TURBO
    #gptModel = GPT_MODEL_40_PREVIEW

    chat_completion = client.chat.completions.create(
        model=gptModel,
        response_format={"type": "json_object"},
        seed=seed,
        temperature=0.1,
        messages=[
            #{"role": "system", "content": "Provide output in valid JSON"},
            {"role": "system", "content": "You will be provided with a document delimited by triple quotes and a JSON schema. The JSON schema includes a number of fields, their desription, and their type.  Your task is to populate the fields in the schema, according to their defined descriptions, using only the provided document. Provide output in valid JSON.  If a field in the schema is null, omit it from the JSON output. Think step by step."},
            {"role": "user", "content": prompt}
        ]
    )
    # prompt, response = scrape_via_prompt(chat, page_text, schema)
    response = chat_completion.choices[0].message.content
    print("fingerprint:" + chat_completion.system_fingerprint + " seed:" + str(seed))
    prompt_tokens = chat_completion.usage.prompt_tokens
    completion_tokens = (
            chat_completion.usage.total_tokens - chat_completion.usage.prompt_tokens
    )
    #using 3.5-turbo
    if gptModel == GPT_MODEL_35_TURBO:
        prompt_cost = prompt_tokens * .0005 / 1000
        completion_cost = completion_tokens * .0015 / 1000
    #using 4-turbo
    else:
        prompt_cost = prompt_tokens * .03 / 1000
        completion_cost = completion_tokens * .06 / 1000

    print("Prompt tokens: " + str(prompt_tokens))
    print("Completion tokens: " + str(completion_tokens))
    print("Total cost:" + str(prompt_cost + completion_cost))
    global total_cost
    total_cost = total_cost + prompt_cost + completion_cost

    # print(response)
    return response

def replace_ssn(text):
    # Define a regex pattern for SSNs
    ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    # Replace SSNs with "xxx"
    modified_text = re.sub(ssn_pattern, 'xxx-xx-xxxx', text)
    print(modified_text)

    return modified_text


def scrub_text(text):
    #scrubber = scrubadub.Scrubber()
    scrubber = scrubadub.Scrubber(post_processor_list=[
        PIIReplacer(),
        scrubadub.post_processors.PrefixSuffixReplacer(prefix='{', suffix='}'),
    ])
    #scrubber.add_detector(scrubadub.detectors.TextBlobNameDetector)
    #scrubber.add_detector(scrubadub_address.detectors.AddressDetector)
    out = scrubber.clean(text)
    print(text)
    print("*******************")
    print(out)
    return out

def analyze_texts():

    client = OpenAI(
        api_key=CHATGPT_KEY
    )

    # Loop through each file in the directory
    for filename in os.listdir(OCR_DIRECTORY_PATH):
        # Check if the current item is a file
        if os.path.isfile(os.path.join(OCR_DIRECTORY_PATH, filename)) and not filename.endswith('.gitignore'):
            print("Calling ChagGPT to determine Industry")

            #read in ocr'd text
            with open(os.path.join(OCR_DIRECTORY_PATH, filename), "r") as f:
                page_text = f.read()

            #get general prompts
            prompts, seed = get_prompts('General', page_text)
            #call gpt1
            print("Calling ChagGPT to get general 1 info")
            response=call_chatgpt(client, prompts[1]['prompt'], seed)
            #write response to output file
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "w") as f:
                f.write(response)
            #map response to industry field
            wjdata = json.loads(response)
            #print(wjdata)
            print("Industry:"+wjdata['Offer Industry'])


            #call gpt with general prompt 2 and 3, appending results to file
            print("Calling ChagGPT to get general 2")
            response=call_chatgpt(client, prompts[2]['prompt'], seed)
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                f.write(",\n" + response)

            print("Calling ChagGPT to get general 3")
            response=call_chatgpt(client, prompts[3]['prompt'], seed)
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                f.write(",\n" + response)

            #get industry prompt(s)
            prompts, seed = get_prompts(wjdata['Offer Industry'], page_text)

            #call gpt for each industry prompt in loop
            for p in prompts:
                #print(prompts[p]['prompt'])

                print("Calling ChatGPT to extract industry fields ")
                response=call_chatgpt(client, prompts[p]['prompt'], seed)

                with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                    f.write(",\n" + response)

            # if success, move file to done
            os.replace(os.path.join(OCR_DIRECTORY_PATH, filename), os.path.join(OCR_DONE_DIRECTORY_PATH, filename))


def do_ocr():

    # Specify the directory path
    source_directory_path = 'images'
    done_directory_path = 'images_done'
    OCR_DIRECTORY_PATH = 'ocr'

    #print("Starting to OCR files...")
    client = boto3.client('textract', region_name='us-west-2', aws_access_key_id='AKIASNRH2MGA4ZH72OFX',
                          aws_secret_access_key=AWS_KEY)

    # Loop through each file in the directory
    for filename in sorted(os.listdir(source_directory_path)):
        # Check if the current item is a file
        if os.path.isfile(os.path.join(source_directory_path, filename)) and not filename.endswith('.gitignore'):

            # determine output filename; if it ends in _22 or _2, save filename without these characters
            # and concatenate all; For example output from bigfile_1.png and bigfile_2.png would both get saved in bigfile
            if re.search("_[0-9]{1,2}\.(jpg|JPG|gif|GIF|doc|DOC|pdf|PDF|png|PNG|jpeg|JPEG)$", filename):
                output_filename = filename.rsplit('_', 1)[0] + ".txt"
            else:
                output_filename = filename

            file1 = open(os.path.join(OCR_DIRECTORY_PATH, output_filename), "a")  # append mode

            # image to read text from
            with open(os.path.join(source_directory_path, filename), 'rb') as file:
                img_bytes = file.read()
                #bytes_test = bytearray(img_test)

            print("Calling OCR for " + filename)
            img_text = client.detect_document_text(
                Document={"Bytes": img_bytes}
            )
            # Print detected text
            for item in img_text["Blocks"]:
                if item["BlockType"] == "LINE":
                    #print(item["Text"])
                    file1.write(item["Text"] + "\n")

            # add a blank line between pages and close file
            file1.write("\n")
            file1.close()


            #if success, move file to done
            os.replace(os.path.join(source_directory_path, filename), os.path.join(done_directory_path, filename))


def main():
    text = "Hello Zhang Wei, I am John. Your AnyCompany Financial Services, LLC credit card account 5424 4242 4242 4242 OR 5424424242424242 has a minimum payment of $24.53 that is due by July 31st. " \
          "Based on your autopay settings, we will withdraw your payment on the due date from your bank account number 11112222 with the routing number 33334444. " \
          "Your SSN is 111-22-2221. Your latest statement was mailed to 2200 West Cypress Creek Road, 1st Floor, Fort Lauderdale, Florida, 33309." \
          "After your payment is received, you will receive a confirmation text message at 206-555-0100." \
          "have questions about your bill, AnyCompany Customer Service is available by phone at 1-800-555-0199 or email at support@anycompany.com."

    #ocr on images in the ocr directory
    do_unzips()
    do_ocr()
    analyze_texts()
    print("Total Cost: " + str(total_cost))
    #print("###############################")
    #scrub_text(text)
    #print("###############################")
    #replace_ssn(text)
    #print("###############################")


if __name__ == "__main__":
    main()






