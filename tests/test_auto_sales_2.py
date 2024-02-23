import pytest
import os
import json

from openai import OpenAI
import gpt_extract

test_file = "20240105-0112037.txt"
#https://www.comperemedia.com/one_search/campaign/20240105-0112037/

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
    return setup_base(test_file, 'Auto-Sales', 1)

@pytest.fixture(scope="session")
def setup_4():
    return setup_base(test_file, 'Auto-Sales', 2)

##################################################################
def test_industry(setup_general_1):
    assert setup_general_1['Offer Industry'].split('-')[0] == 'Auto', f"Actual: {setup_general_1['Offer Industry'].split('-')[0]}|"

def test_category(setup_general_1):
    assert setup_general_1['Offer Industry'].split('-')[1] == 'Sales', f"Actual: {setup_general_1['Offer Industry'].split('-')[1]}|"

def test_primary_company(setup_general_1):
    assert "chevy" or "general motors" in setup_general_1['Primary Company'].lower(), f"Actual: {setup_general_1['Primary Company']}|"

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
    assert "QR Code to Scan" in setup_general_2['Response Mechanism'], f"Actual: {setup_general_2['Response Mechanism']}|"

def test_mailing_type(setup_general_2):
    assert setup_general_2['Mailing Type'] == 'Acquisition', f"Actual: {setup_general_2['Mailing Type']}|"



#########################################################
def test_offer_origin(setup_3):
    assert setup_3['Offer Origin'] == 'Manufacturer', f"Actual: {setup_3['Offer Origin']}|"

def test_vehicle_brand(setup_3):
    assert setup_3['Vehicle Brand'] == 'Chevrolet', f"Actual: {setup_3['Vehicle Brand']}|"

def test_vehicle_representation(setup_3):
    assert setup_3['Vehicle Representation'] == 'Division Line-Up', f"Actual: {setup_3['Vehicle Representation']}|"

def test_vehicle_types(setup_3):

    vehicle_types = ''
    for vehicle in setup_3['Vehicles']:
        if "Vehicle Type" in vehicle:
            vehicle_types += vehicle['Vehicle Type'] + ' '

    assert "suv" and "crossover" in vehicle_types.lower(), f"Actual: {vehicle_types}|"


#def test_warranty(setup_3):
#    assert "10" and "year" and "100" and "mile" in setup_3['Warranty'].lower(), f"Actual: {setup_3['Warranty']}|"

def test_vehicle_launch(setup_3):
    assert setup_3['Vehicle Launch'] == 'No', f"Actual: {setup_3['Vehicle Launch']}|"

#########################################################
def test_offer_description(setup_4):
    assert "vehicle" and "bonus" and "cash" in setup_4['Offer Description'].lower(), f"Actual: {setup_4['Offer Description']}|"

def test_event_name(setup_4):
    assert "red" and "tag" in setup_4['Event Name'].lower(), f"Actual: {setup_4['Event Name']}|"

def test_vehicle_financing_type(setup_4):
    assert "loan" in setup_4['Vehicle Financing Type'].lower(), f"Actual: {setup_4['Vehicle Financing Type']}|"

def test_offer_loan_term(setup_4):
    assert setup_4['Offer Loan Term'] == 36, f"Actual: {setup_4['Offer Loan Term']}|"

def test_offer_apr(setup_4):
    assert setup_4['Offer APR'] == 1.9, f"Actual: {setup_4['Offer APR']}|"

def test_offer_expiration(setup_4):
    assert setup_4['Offer Expiration'] == '2024-01-02', f"Actual: {setup_4['Offer Expiration']}|"
