import pytest
import os
import json

from openai import OpenAI
import gpt_extract

test_file = "37784235.txt"

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
    assert "fountain tire" in setup_general_1['Primary Company'].lower(), f"Actual: {setup_general_1['Primary Company']}|"

##################################################################
def test_post_indicia(setup_general_3):
    assert setup_general_3['Post Indicia'] == 'Permit', f"Actual: {setup_general_3['Post Indicia']}|"

#def test_post_type(setup_general_1):
#    assert setup_general_1['Post Type'] == 'Standard'

def test_presorted(setup_general_3):
    assert setup_general_3['Presorted'] == 'N', f"Actual: {setup_general_3['Presorted']}|"

#########################################################
def test_call_to_action(setup_general_2):
    assert "Customer Visit" in setup_general_2['Response Mechanism'] or "QR Code to Scan" in setup_general_2['Response Mechanism'], f"Actual: {setup_general_2['Response Mechanism']}|"

def test_mailing_type(setup_general_2):
    assert setup_general_2['Mailing Type'] == 'Acquisition', f"Actual: {setup_general_2['Mailing Type']}|"

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
            if incentive['Incentive Value'] == "225":
                assert incentive['Incentive Value'] == "225", f"Actual: {incentive['Incentive Value']}|"

def test_primary_incentive_text(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Text" in incentive:
            if "225" in incentive['Incentive Text']:
                assert "225" in incentive['Incentive Text'] and "tires" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

##
def test_second_incentive_type(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    #assert "Discount" in setup_general_2['Incentives'][0]['Incentive Type'] or "Discount" in setup_general_2['Incentives'][1]['Incentive Type']
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Type'] == "Discount":
                assert incentive['Incentive Type'] == "Discount", f"Actual: {incentive['Incentive Type']}|"
def test_second_incentive_value(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "50":
                assert incentive['Incentive Value'] == "50", f"Actual: {incentive['Incentive Value']}|"

def test_second_incentive_text(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Text" in incentive:
            if "50" in incentive['Incentive Text']:
                assert "50" in incentive['Incentive Text'] and "service" in incentive['Incentive Text'], f"Actual: {incentive['Incentive Text']}|"

#########################################################
def test_offer_origin(setup_3):
    assert setup_3['Offer Origin'] == 'Service Center', f"Actual: {setup_3['Offer Origin']}|"

def test_product(setup_3):
    assert "service" in setup_3['Product'].lower(), f"Actual: {setup_3['Product']}|"

def test_offer_summary(setup_3):
    assert "save" or "discount" in setup_3['Offer Summary'].lower() and "tires" or "service" in setup_3['Offer Summary'].lower(), f"Actual: {setup_3['Offer Summary']}|"

def test_offer_close_date(setup_3):
    assert 'December 16' in setup_3['Offer Close Date'], f"Actual: {setup_3['Offer Close Date']}|"
