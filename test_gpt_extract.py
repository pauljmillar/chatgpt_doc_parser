import pytest
import os
import json

from openai import OpenAI
import gpt_extract

@pytest.fixture
def setup():

    client = OpenAI(
        api_key=gpt_extract.CHATGPT_KEY
    )
    #get auto sales data
    auto_filename = '20230325-011572.txt'
    with open(os.path.join(gpt_extract.OCR_DIRECTORY_PATH, auto_filename), "r") as f:
        page_text = f.read()
    #get prompt
    prompts, seed = gpt_extract.get_schema('General', page_text)
    gen1Response = gpt_extract.call_chatgpt(client, prompts[1]['prompt'], seed)
    return json.loads(gen1Response)


def test_offer_industry(setup):
    assert setup['Offer Industry'] == 'Auto-Service'

def test_primary_company(setup):
    assert "Valvoline" in setup['Primary Company']

def test_mailing_type(setup):
    assert setup['Mailing Type'] == 'Acquisition'

def test_post_indicia(setup):
    assert setup['Post Indicia'] == 'Metered'

def test_post_type(setup):
    assert setup['Post Type'] == 'Standard'

def test_presorted(setup):
    assert setup['Presorted'] == 'Y'


