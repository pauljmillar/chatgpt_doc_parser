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





from openai import OpenAI
#from chatgpt_wrapper import ChatGPT
from dotenv import load_dotenv

load_dotenv()

AWS_KEY = os.getenv("AWS_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
GENERAL_SCHEMA = "general.schema.json"
GENERAL_SCHEMA_1 = "general_1.schema.json"
GENERAL_SCHEMA_2 = "general_2.schema.json"
GENERAL_SCHEMA_3 = "general_3.schema.json"
AUTO_SERVICE_SCHEMA = "auto_service.schema.json"
AUTO_SALES_SCHEMA = "auto_sales.schema.json"
TELECOM_INTERNET_SCHEMA = "telecom_internet.schema.json"
GPT_MODEL_35_TURBO = "gpt-3.5-turbo-0125"
GPT_MODEL_40_PREVIEW = "gpt-4-1106-preview"
OCR_DIRECTORY_PATH = 'ocr'
OCR_DONE_DIRECTORY_PATH = 'ocr_done'
JSON_RESULT_DIRECTORY_PATH = 'json_result'
SCHEMA_DIRECTORY_PATH = 'schema'
PROMPT_DIRECTORY_PATH = 'prompt'


def do_unzips():
    #print("Starting unzipping")

    source_directory_path = 'images'
    initial_working_directory = os.getcwd()

    working_directory = os.path.join(initial_working_directory, source_directory_path)
    #print(working_directory)
    os.chdir(working_directory)

    for file in os.listdir(working_directory):  # get the list of files
        #print(file)
        if zipfile.is_zipfile(file):  # if it is a zipfile, extract it
            print("Unzipping " + file + "..")
            with zipfile.ZipFile(file) as item:  # treat the file as a zip
                item.extractall()  # extract it in the working directory
            os.remove(file)

    os.chdir(initial_working_directory)
    #print("Done unzipping")


def get_schema(industry, textBody):
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
'''
    match industry:
        case "General":
            schemaFilename = "auto_sales.schema.json"
            seed = seedGeneral

            #read in json schema for general fields: to determine what industry the mail is for
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, GENERAL_SCHEMA_1), "r") as f:
                schema1 = json.load(f)
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, GENERAL_SCHEMA_2), "r") as f:
                schema2 = json.load(f)
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, GENERAL_SCHEMA_3), "r") as f:
                schema3 = json.load(f)
            promptDict = {
                #1: {'prompt': f'```{textBody}```\n\nThe text above is promotional material. Determine which industry it is for, using the Offer Industry list in description in the following JSON schema. Then, determine the Primary Company - this is the company or business who has sent the offer.  \n\nFinally, populate the Offer Industry, Primary Company, and the other fields defined in the schema and provide your response in JSON that adheres to the schema.:\n\n```{schema1}```'},
                1: {'prompt': f'```{textBody}```\n\nThe text above is promotional material. Determine which industry it is for, using the description provided in the following JSON schema. Then, read the following JSON schema to learn the description, type, and enum for Offer Industry, Primary Company, Secondary Company, Business Type.  \n\nFinally, populate the Offer Industry, Primary Company, and the other fields defined in the schema and provide your response in JSON format that adheres to the schema.:\n\n```{schema1}```'},
                #2: {'prompt': f'```{textBody}```\n\nThe text above includes promotional incentives: products, services, or benefits offered to customers for completing the task required by the company. First, observe all of the incentives in the text.  Then, refine them according to descriptions in the following JSON schema. Then, determine whether the other fields in the JSON schema are present in the text, according to the definitions in the field description in the JSON schema.  \n\nFinally, populate the Incentive Text, Incentive Type, and the other fields defined in the schema and provide your response in JSON that adheres to the schema.:\n\n```{schema2}```'}
                2: {'prompt': f'```{textBody}```\n\nThat text above is marketing material.  Determine the Mailing Type, Response Mechanism, and Incentives presented in the material. Then, read in the following JSON file. It defines the Mailing Type, Response Mechanism, and Incentive attributes.  Finally, populate the attributes from the JSON file using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema2}```'},
                3: {'prompt': f'```{textBody}```\n\nThe text above is promotional material. From the text, determine the direct mail attributes, which are listed in the following JSON schema.  Then, read the following JSON schema to learn the description, type, and enum for Post Indicia, Post Type, Presorted, Pre-screen Opt Out Disclosure.  \n\nFinally, populate the attributes from the JSON file using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema3}```'}
            }


        case "Auto-Sales":
            schemaFilename1 = "auto_sales_1.schema.json"
            schemaFilename2 = "auto_sales_2.schema.json"
            seed=seedAutoSales

            industrySeed = seedAutoSales
            #read in json schema for auto warranty fields:
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename1), "r") as f:
                schema1 = json.load(f)
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename2), "r") as f:
                schema2 = json.load(f)
            promptDict = {
                1: {'prompt': f'```{textBody}```\n\nThat text was mailed to a potential automobile customer.  Within the text, observe information about the vehicles provided, including the Offer Origin, which describes the type of company that originated the offer. It can be either a Dealer, a Manufacturer, or a Service Center. Then, read in the following JSON file, including the field names, their types, definitions, and enums.  Finally, identify those defined fields, including Offer Origin, using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema1}```'},
                #2: {'prompt': f'```{textBody}```\n\nThat text was mailed to a potential automobile customer.  Within the text, determine what is the main Offer Description: a summary of the most prominent offer presented, limited to 10 words or less.  Next, determine whether there is an Event Name, or a title or reason for the set of promotions. Then, read in the following JSON file - it defines 7 attributes: Event Name, Offer Description, Vehicle Financing Type, Offer Loan Term, Offer APR, Offer Expiration, Purchase Discount.  Finally, populate the attributes from the JSON file using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema2}```'}
                2: {'prompt': f'```{textBody}```\n\nThat text was mailed to a potential automobile customer.  Observe information about the offers presented. Then, read in the following JSON file - it defines 7 attributes: Event Name, Offer Description, Vehicle Financing Type, Offer Loan Term, Offer APR, Offer Expiration, Purchase Discount.  Finally, populate the attributes from the JSON file using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema2}```'}
            }

        case "Auto-Service":
            schemaFilename = "auto_service.schema.json"
            seed = seedAutoService
            #read in json schema for auto service fields
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename), "r") as f:
                schema = json.load(f)
            promptDict = {
                1: {'prompt': f'```{textBody}```\n\nWithin the given text, identify the Offer Description and the other attributes described in following JSON schema, and provide them in a JSON representation that strictly follows this schema:\n\n```{schema}```'}
            }

        case "Auto-Warranty":
            schemaFilename = "auto_warranty.schema.json"
            seed = seedAutoService
            #read in json schema for auto warranty fields:
            with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename), "r") as f:
                schema = json.load(f)
            promptDict = {
                1: {'prompt': f'```{textBody}```\n\nWithin the given text, identify the main Service being offered - it may be an Extended Auto Warranty. Summarize the Offer presented in the text. Then read in the following JSON file, including the field names, their types, definitions, and enums.  Finally, identify those defined fields using the given text, and return them in a JSON representation that strictly follows this JSON schema:\n\n```{schema}```'}
            }

        case "Telecom-Internet":
            schemaFilename = "telecom_internet.schema.json"

        case _:
            print("The industry does not match.")

    #print("Choosing schema: " + schemaFilename)
    return promptDict, seed
'''




'''
    #auto
    if any(re.findall(r'car |auto|truck |suv |motorcycle ', promo_text, re.IGNORECASE)) and any(re.findall(r'service| oil| tire|repair', promo_text, re.IGNORECASE)):
        schemaFilename = "auto_service.schema.json"
    elif any(re.findall(r'lease|financing|sales', promo_text, re.IGNORECASE)) and any(re.findall(r'ford|chevy|chrysler|cadillac|dodge|gmc|hyundai|tesla|gm|jeep|lincoln|honda|nissan|audi|porsche|bmw|mercedes', promo_text, re.IGNORECASE)):
        schemaFilename = "auto_sales.schema.json"
    #telecom
    elif any(re.findall(r'internet', promo_text, re.IGNORECASE)) and any(re.findall(r'speed|installation|service', promo_text, re.IGNORECASE)):
        schemaFilename = "telecom_internet.schema.json"
    #else: Call chatgpt to figure out what category


'''

def get_attribute(data, attr):
    if attr in data:
        return data[attr]

def get_accuracy(new_row_id):
    return 50

def compare_vals(test, master):
    if test is None:
        if master is None:
            return True
        else:
            return False
    else:
        if master is None:
            return False

    if test.lower() == master.lower():
        return True
    else:
        return False

def check_accuracy():
    '''
    Look for all rows without an accuracy value. For each, looks for a master record.
    If found, compares fields in the master record to fields in the test record, calculates accuracy, updates general row.
    '''

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    response = supabase.table('general_attributes').select('(*)').eq('record_type', 'test').is_('accuracy', 'null').execute()

    response_json = json.loads(response.json())
    test_entries = response_json['data']

    for i in range(len(test_entries)):
        #print('Rec ' + str(test_entries[i]['id']) + ': '+ test_entries[i]['primary_company'] + ' mailpack: ' + test_entries[i]['mailpack_id'])
        totalAttributes = 0
        matchedAttributes = 0

        masterResponse = supabase.table('general_attributes').select('(*)').eq('record_type', 'master').eq('mailpack_id',test_entries[i]['mailpack_id']).execute()
        master_json = json.loads(masterResponse.json())
        master_entry = master_json['data']

        #compare master_entry with test_entry
        if  compare_vals(test_entries[i]['mailpack_id'], master_entry[0]['mailpack_id']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['mailpack_id'], master_entry[0]['mailpack_id'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['primary_company'], master_entry[0]['primary_company']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['primary_company'], master_entry[0]['primary_company'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['business_type'], master_entry[0]['business_type']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['business_type'], master_entry[0]['business_type'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['mailing_type'], master_entry[0]['mailing_type']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['mailing_type'], master_entry[0]['mailing_type'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['post_indicia'], master_entry[0]['post_indicia']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['post_indicia'], master_entry[0]['post_indicia'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['post_type'], master_entry[0]['post_type']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['post_type'], master_entry[0]['post_type'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['presorted'], master_entry[0]['presorted']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['presorted'], master_entry[0]['presorted'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['pre_screen_opt_out_disclosure'], master_entry[0]['pre_screen_opt_out_disclosure']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['pre_screen_opt_out_disclosure'], master_entry[0]['pre_screen_opt_out_disclosure'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['response_mechanism'], master_entry[0]['response_mechanism']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['response_mechanism'], master_entry[0]['response_mechanism'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['incentive_1'], master_entry[0]['incentive_1']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_1'], master_entry[0]['incentive_1'])
        totalAttributes += 1

        if  compare_vals(test_entries[i]['incentive_type_1'], master_entry[0]['incentive_type_1']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_type_1'], master_entry[0]['incentive_type_1'])
        totalAttributes += 1

        if compare_vals(test_entries[i]['incentive_2'], master_entry[0]['incentive_2']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_2'], master_entry[0]['incentive_2'])
        totalAttributes += 1

        if compare_vals(test_entries[i]['incentive_type_2'], master_entry[0]['incentive_type_2']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_type_2'], master_entry[0]['incentive_type_2'])
        totalAttributes += 1

        if compare_vals(test_entries[i]['incentive_3'], master_entry[0]['incentive_3']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_3'], master_entry[0]['incentive_3'])
        totalAttributes += 1

        if compare_vals(test_entries[i]['incentive_type_3'], master_entry[0]['incentive_type_3']):
            matchedAttributes += 1
        else:
            print(test_entries[i]['incentive_type_3'], master_entry[0]['incentive_type_3'])
        totalAttributes += 1

        accuracy = matchedAttributes / totalAttributes
        print(f"Accuracy: {accuracy:.1%}")

        #update accuracy in parent record
        #data, count = supabase.table('general_attributes').update({'accuracy': accuracy}).eq('id', test_entries[i]['id']).execute()

    #print(response)

def log_to_db(generalJson, industryJson, filename, industrySchema):

    main_list = []
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

    mailpackId = Path(filename).stem

    #insert general record
    general = json.loads(generalJson)
    offerIndustry = get_attribute(general, "Offer Industry")
    primaryCompany = get_attribute(general, "Primary Company")
    secondaryCompany = get_attribute(general, "Secondary Company")
    businessType = get_attribute(general, "Business Type")
    mailingType = get_attribute(general, "Mailing Type")
    postIndicia = get_attribute(general, "Post Indicia")
    postType = get_attribute(general, "Post Type")
    presorted = get_attribute(general, "Presorted")
    preScreenOptOutDisclousre = get_attribute(general, "Pre-screen Opt Out Disclosure")
    responseMechanism = get_attribute(general, "Response Mechanism (Call to Action)")
    incentive1 = ''
    incentive2 = ''
    incentive3 = ''
    incentiveType1 = ''
    incentiveType2 = ''
    incentiveType3 = ''



    if "Incentives" in general: #general["Incentives"]:
        if len(general["Incentives"]) > 0:
            incentive1 = general["Incentives"][0]["Incentive Text"]
            incentiveType1 = general["Incentives"][0]["Incentive Type"]
        if len(general["Incentives"]) > 1 :
            incentive2 = general["Incentives"][1]["Incentive Text"]
            incentiveType2 = general["Incentives"][1]["Incentive Type"]
        if len(general["Incentives"]) > 2:
            incentive3 = general["Incentives"][2]["Incentive Text"]
            incentiveType3 = general["Incentives"][2]["Incentive Type"]

    value = {'mailpack_id': mailpackId,
             'offer_industry': offerIndustry,
             'primary_company': primaryCompany,
             'secondary_company': secondaryCompany,
             'business_type': businessType,
             'mailing_type': mailingType,
             'post_indicia': postIndicia,
             'post_type': postType,
             'presorted': presorted,
             'pre_screen_opt_out_disclosure': preScreenOptOutDisclousre,
             'response_mechanism': responseMechanism,
             'incentive_1': incentive1,
             'incentive_type_1': incentiveType1,
             'incentive_2': incentive2,
             'incentive_type_2': incentiveType2,
             'incentive_3': incentive3,
             'incentive_type_3': incentiveType3,
             'record_type': 'test'
             }

    main_list.append(value)

    data = supabase.table('general_attributes').insert(main_list).execute()
    print('^^^^^^^^^^^^^^^^')
    print(data)
    data_json = json.loads(data.json())
    new_row_id = data_json['data'][0]['id']


    #insert industry-specific record
    if (industrySchema == AUTO_SALES_SCHEMA):
        industry = json.loads(industryJson)

        offerOrigin = get_attribute(industry, "Offer Origin")
        vehicleRepresentation = get_attribute(industry, "Vehicle Representation")
        vehicleLaunch = get_attribute(industry, "Vehicle Launch")

        value = {
             'offer_origin': offerOrigin,
             'vehicle_representation': vehicleRepresentation,
             'vehicle_launch': vehicleLaunch,
             'record_type': 'test'
        }

        data2 = supabase.table('auto_attributes').insert(value).execute()

    return new_row_id


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

    # print(response)
    return response

def replace_ssn(text):
    # Define a regex pattern for SSNs
    ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    # Replace SSNs with "xxx"
    modified_text = re.sub(ssn_pattern, 'xxx-xx-xxxx', text)

    return modified_text

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
            prompts, seed = get_schema('General', page_text)
            #call gpt1
            print("Calling ChagGPT to get general 1 info")
            gen1Response=call_chatgpt(client, prompts[1]['prompt'], seed)
            #write response to output file
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "w") as f:
                f.write(gen1Response + "\n")
            #map response to industry field
            wjdata = json.loads(gen1Response)
            print(wjdata)
            print("Industry:"+wjdata['Offer Industry'])


            #call gpt2
            gen2Response=call_chatgpt(client, prompts[2]['prompt'], seed)
            print("Calling ChagGPT to get general 2")
            #write response to output file
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                f.write(gen2Response + "\n")

            #call gpt3
            gen2Response=call_chatgpt(client, prompts[3]['prompt'], seed)
            print("Calling ChagGPT to get general 3")
            #write response to output file
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                f.write(gen2Response + "\n")

            #get industry prompt(s)
            prompts, seed = get_schema(wjdata['Offer Industry'], page_text)
            #call industry gpt in loop



            for p in prompts:
                print(prompts[p]['prompt'])

                #with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename), "r") as f:
                #    schema = json.load(f)
                #print("schema:"+prompts[p]['schema'])

                print("Calling ChatGPT 3rd time to extract fields ")
                response=call_chatgpt(client, prompts[p]['prompt'], seed)

                with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "a") as f:
                    f.write(response)

            # Record entry in db
            #new_row_id = log_to_db(gen1Response, response, filename, schemaFilename)

            # if success, move file to done
            os.replace(os.path.join(OCR_DIRECTORY_PATH, filename), os.path.join(OCR_DONE_DIRECTORY_PATH, filename))
            #print("Chatgpt calls complete.")

            #accuracy = get_accuracy(new_row_id)
            #print(accuracy)
'''
            # determine which schema looking at text keywords
            schemaFilename = get_schema(page_text)

            with open(os.path.join(SCHEMA_DIRECTORY_PATH, schemaFilename), "r") as f:
                schema = json.load(f)



            prompt = f"```{page_text}```\n\nWithin the given text, identify the Offer Description and the other attributes described in following JSON schema, and provide them in a JSON representation that strictly follows this schema:\n\n```{schema}```"


            print("Saving results to", os.path.join(JSON_RESULT_DIRECTORY_PATH, filename))
            with open(os.path.join(JSON_RESULT_DIRECTORY_PATH, filename), "w") as f:
                #f.write(json.dumps(results, indent=2))
                f.write(response)

            # if success, move file to done
            os.replace(os.path.join(OCR_DIRECTORY_PATH, filename), os.path.join(OCR_DONE_DIRECTORY_PATH, filename))
'''



def do_ocr():

    # Specify the directory path
    source_directory_path = 'images'
    done_directory_path = 'images_done'
    OCR_DIRECTORY_PATH = 'ocr'

    #get key from file
    #f = open("aws_key.txt", "r")
    #aws_key=

    #print("Starting to OCR files...")
    client = boto3.client('textract', region_name='us-west-2', aws_access_key_id='AKIASNRH2MGA4ZH72OFX',
                          aws_secret_access_key=AWS_KEY)

    # Loop through each file in the directory
    for filename in sorted(os.listdir(source_directory_path)):
        # Check if the current item is a file
        if os.path.isfile(os.path.join(source_directory_path, filename)) and not filename.endswith('.gitignore'):
            # Do something with the file, for example, print its name
            #print(filename)

            # determine output filename; if it ends in _22 or _2, save filename without these characters
            # and concatenate all; For example output from bigfile_1.png and bigfile_2.png would both get saved in bigfile
            if re.search("_[0-9]{1,2}\.(jpg|JPG|gif|GIF|doc|DOC|pdf|PDF|png|PNG|jpeg|JPEG)$", filename):
                output_filename = filename.rsplit('_', 1)[0] + ".txt"
            else:
                output_filename = filename
            #print(">>>writing text to:" + output_filename)

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
    #print("OCR complete")


def get_prompts(industry):
    #global prompt_dict


    auto_sales_dict = {
        1: { 'prompt':'1gen for auto sales'},
        2: { 'prompt':'2gen for auto sales'}
    }

    general_dict = {
        1: { 'prompt':'1gen for general'},
        2: { 'prompt':'2gen for general'}
    }

    auto_service_dict = {
        1: {'prompt':'1gen for auto service'},
        2: {'prompt':'2gen for auto service'},
        3: {'prompt': '3gen for auto service'}
    }

    match industry:
        case "Auto-Sales":
            return auto_sales_dict
        case "Auto-Service":
            return auto_service_dict
        case "General":
            return general_dict



def try_dict():

    prompt_dict = get_prompts("General")

    for p in prompt_dict:
        print(prompt_dict[p]['prompt'])

    prompt_dict = get_prompts("Auto-Service")

    for p in prompt_dict:
        print(prompt_dict[p]['prompt'])


def main():
    #ocr on images in the ocr directory
    do_unzips()
    do_ocr()
    analyze_texts()
    #check_accuracy()
    #init()
    #try_dict()

if __name__ == "__main__":
    main()






