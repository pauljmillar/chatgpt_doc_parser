import pytest
import os
import json

from openai import OpenAI
import gpt_extract

test_file = "20220212-011483.txt"
#https://www.comperemedia.com/one_search/campaign/20220212-011483/


def setup_base(filename, industry, num):
    client = OpenAI(
        api_key=gpt_extract.CHATGPT_KEY
    )

    with open(os.path.join(gpt_extract.OCR_DONE_DIRECTORY_PATH, filename), "r") as f:
        page_text = f.read()
    #get prompt
    prompts, seed = gpt_extract.get_prompts(industry, page_text)
    response = gpt_extract.call_chatgpt(client, prompts[num]['prompt'], seed)
    return json.loads(response)


@pytest.fixture(scope="session")
def setup_general_1():
    return setup_base(test_file, 'General', 1)

@pytest.fixture(scope="session")
def setup_general_2():
    return setup_base(test_file, 'General', 2)

@pytest.fixture(scope="session")
def setup_general_3():
    return setup_base(test_file, 'General', 3)

@pytest.fixture(scope="session")
def setup_3():
    return setup_base(test_file, 'Auto-Service', 1)

##################################################################
def test_industry(setup_general_1):
    #assert setup_general_1['Offer Industry'] == 'Auto-Service'
    assert setup_general_1['Offer Industry'].split('-')[0] == 'Auto', f"Actual: {setup_general_1['Offer Industry'].split('-')[0]}|"

def test_category(setup_general_1):
    assert setup_general_1['Offer Industry'].split('-')[1] == 'Service', f"Actual: {setup_general_1['Offer Industry'].split('-')[1]}|"

def test_primary_company(setup_general_1):
    assert "midas" in setup_general_1['Primary Company'].lower(), f"Actual: {setup_general_1['Primary Company']}|"

##################################################################
def test_post_indicia(setup_general_3):
    assert setup_general_3['Post Indicia'] == 'Permit', f"Actual: {setup_general_3['Post Indicia']}|"

#def test_post_type(setup_general_1):
#    assert setup_general_1['Post Type'] == 'Standard'

def test_presorted(setup_general_3):
    assert setup_general_3['Presorted'] == 'Y', f"Actual: {setup_general_3['Presorted']}|"

#########################################################
def test_call_to_action(setup_general_2):
    #assert "Customer Visit" in setup_general_2['Response Mechanism (Call to Action)'] or "QR Code" in setup_general_2['Response Mechanism (Call to Action)'], f"Actual: {setup_general_2['Response Mechanism (Call to Action)']}|"
    assert "Customer Visit" in setup_general_2['Response Mechanism'], f"Actual: {setup_general_2['Response Mechanism']}|"

def test_mailing_type(setup_general_2):
    assert setup_general_2['Mailing Type'] == 'Acquisition', f"Actual: {setup_general_2['Mailing Type']}|"

def test_incentive_1(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "10":
                assert incentive['Incentive Value'] == "10", f"Actual: {incentive['Incentive Value']}|"
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert "10" in incentive['Incentive Text'] and "service" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

'''
def test_primary_incentive_type(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    #assert "Discount" in setup_general_2['Incentives'][0]['Incentive Type'] or "Discount" in setup_general_2['Incentives'][1]['Incentive Type']
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Type'] == "Discount":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
def test_primary_incentive_value(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "10":
                assert incentive['Incentive Value'] == "10", f"Actual: {incentive['Incentive Value']}|"

def test_primary_incentive_text(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Text" in incentive:
            if "10" in incentive['Incentive Text']:
                assert "10" in incentive['Incentive Text'] and "service" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"
'''
#######OFFER 2

def test_incentive_2(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "20":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert incentive['Incentive Value'] == "20", f"Actual: {incentive['Incentive Value']}|"
                assert "20" in incentive['Incentive Text'] and "oil" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"


def test_incentive_3(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "25":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert incentive['Incentive Value'] == "25", f"Actual: {incentive['Incentive Value']}|"
                assert "25" in incentive['Incentive Text'] and "alignment" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"


def test_incentive_4(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "30":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert incentive['Incentive Value'] == "30", f"Actual: {incentive['Incentive Value']}|"
                assert "30" in incentive['Incentive Text'] and "service" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

def test_incentive_5(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "50":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert incentive['Incentive Value'] == "50", f"Actual: {incentive['Incentive Value']}|"
                assert "50" in incentive['Incentive Text'] and "off" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

def test_incentive_5(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "70":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
                assert incentive['Incentive Value'] == "70", f"Actual: {incentive['Incentive Value']}|"
                assert "70" in incentive['Incentive Text'] and "brakes" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

def test_incentive_6(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Type'] == "Free Service":
                assert incentive['Incentive Type'] == "Free Service", f"Actual: {incentive['Incentive Type']}|"
                assert "alighment" in incentive['Incentive Text'].lower(), f"Actual: {incentive['Incentive Text']}|"





#########################################################
def test_offer_origin(setup_3):
    assert setup_3['Offer Origin'] == 'Service Center', f"Actual: {setup_3['Offer Origin']}|"

def test_product(setup_3):
    assert "service" in setup_3['Product'].lower(), f"Actual: {setup_3['Product']}|"

def test_offer_summary(setup_3):
    assert "save" or "discount" in setup_3['Offer Summary'].lower() and "auto" or "service" in setup_3['Offer Summary'].lower(), f"Actual: {setup_3['Offer Summary']}|"

def test_offer_close_date(setup_3):
    assert setup_3['Offer Close Date'] == '4/30/22', f"Actual: {setup_3['Offer Close Date']}|"
