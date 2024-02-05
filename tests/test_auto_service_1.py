import pytest
import os
import json

from openai import OpenAI
import gpt_extract

def setup_base(filename, industry, num):
    client = OpenAI(
        api_key=gpt_extract.CHATGPT_KEY
    )

    with open(os.path.join(gpt_extract.OCR_DONE_DIRECTORY_PATH, filename), "r") as f:
        page_text = f.read()
    #get prompt
    prompts, seed = gpt_extract.get_schema(industry, page_text)
    response = gpt_extract.call_chatgpt(client, prompts[num]['prompt'], seed)
    return json.loads(response)


@pytest.fixture(scope="session")
def setup_general_1():
    return setup_base('20230325-011572.txt', 'General', 1)

@pytest.fixture(scope="session")
def setup_general_2():
    return setup_base('20230325-011572.txt', 'General', 2)

@pytest.fixture(scope="session")
def setup_general_3():
    return setup_base('20230325-011572.txt', 'Auto-Service', 1)

##################################################################
def test_industry(setup_general_1):
    #assert setup_general_1['Offer Industry'] == 'Auto-Service'
    assert setup_general_1['Offer Industry'].split('-')[0] == 'Auto'

def test_category(setup_general_1):
    assert setup_general_1['Offer Industry'].split('-')[1] == 'Service'

def test_primary_company(setup_general_1):
    assert "Valvoline" in setup_general_1['Primary Company']

def test_mailing_type(setup_general_1):
    assert setup_general_1['Mailing Type'] == 'Acquisition'

def test_post_indicia(setup_general_1):
    assert setup_general_1['Post Indicia'] == 'Permit'

#def test_post_type(setup_general_1):
#    assert setup_general_1['Post Type'] == 'Standard'

def test_presorted(setup_general_1):
    assert setup_general_1['Presorted'] == 'Y'

#########################################################
def test_call_to_action(setup_general_2):
    assert "Customer Visit" in setup_general_2['Response Mechanism (Call to Action)']

def test_primary_incentive_type(setup_general_2):
    #check whether the main incentive was returned in the list of incentives
    #assert "Discount" in setup_general_2['Incentives'][0]['Incentive Type'] or "Discount" in setup_general_2['Incentives'][1]['Incentive Type']
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Type'] == "Discount":
                assert incentive['Incentive Type'] == "Discount"
def test_primary_incentive_value(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Value" in incentive:
            if incentive['Incentive Value'] == "15":
                assert incentive['Incentive Value'] == "15"

def test_primary_incentive_text(setup_general_2):
    #loop through incentives
    for incentive in setup_general_2['Incentives']:
        if "Incentive Text" in incentive:
            if "15 Off" in incentive['Incentive Text']:
                assert "15 Off" in incentive['Incentive Text']

#########################################################
def test_offer_origin(setup_general_3):
    assert setup_general_3['Offer Origin'] == 'Service Center'

def test_product(setup_general_3):
    assert "oil change" in setup_general_3['Product'].lower()

def test_offer_summary(setup_general_3):
    assert "oil change" in setup_general_3['Offer Summary'].lower() or "maintenance" in setup_general_3['Offer Summary'].lower()

def test_offer_close_date(setup_general_3):
    assert setup_general_3['Offer Close Date'] == '4/18/2023'
