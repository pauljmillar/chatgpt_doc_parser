import pytest
import os
import json

from openai import OpenAI
import gpt_extract

test_file = "20231024-0111446.txt"

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
    return setup_base(test_file, 'Auto-Warranty', 1)

##################################################################
def test_industry(setup_general_1):
    #assert setup_general_1['Offer Industry'] == 'Auto-Service'
    assert setup_general_1['Offer Industry'].split('-')[0] == 'Auto', f"Actual: {setup_general_1['Offer Industry'].split('-')[0]}|"

def test_category(setup_general_1):
    assert setup_general_1['Offer Industry'].split('-')[1] == 'Warranty', f"Actual: {setup_general_1['Offer Industry'].split('-')[1]}|"

def test_primary_company(setup_general_1):
    assert "evercare direct" in setup_general_1['Primary Company'].lower(), f"Actual: {setup_general_1['Primary Company']}|"

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
    assert "800 Telephone Number" in setup_general_2['Response Mechanism'], f"Actual: {setup_general_2['Response Mechanism']}|"

def test_mailing_type(setup_general_2):
    assert setup_general_2['Mailing Type'] == 'Acquisition', f"Actual: {setup_general_2['Mailing Type']}|"


#########################################################
def test_offer_origin(setup_3):
    assert setup_3['Offer Origin'] == 'Service Center', f"Actual: {setup_3['Offer Origin']}|"

def test_service(setup_3):
    assert "extended" and "warranty" in setup_3['Service'].lower(), f"Actual: {setup_3['Service']}|"

def test_offer_summary(setup_3):
    assert "extend" or "extension" in setup_3['Offer Summary'].lower() and "warranty" or "coverage" in setup_3['Offer Summary'].lower(), f"Actual: {setup_3['Offer Summary']}|"

def test_offer_close_date(setup_3):
    assert setup_3['Offer Close Date'] == '2023-10-16', f"Actual: {setup_3['Offer Close Date']}|"

def test_warranty(setup_3):
    assert "6" or "6 years" in setup_3['Warranty'].lower() and "100" in setup_3['Warranty'].lower(), f"Actual: {setup_3['Warranty']}|"
