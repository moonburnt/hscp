import pytest
import hscp
import string
from random import randint, choices
from os import environ
from sys import exit
from dotenv import load_dotenv

load_dotenv(".env")

url = environ["HSCP_TEST_URL"]
app = environ["HSCP_TEST_APP"]

login = None
pw = None
client = None

def _generate_string(length:int = 6) -> str:
    return "".join(choices(string.ascii_uppercase + string.digits, k=length))

def test_init():
    global client
    client = hscp.HyScoresClient(
        url = url, 
        app = app,
    )

def test_token_requirement():
    with pytest.raises(hscp.TokenUnavailable):
        client.get_scores()

def test_register():
    global login
    global pw

    login = _generate_string()
    pw = _generate_string()
    client.register(login, pw)

def test_login():
    client.login(login, pw)

def test_scores():
    assert type(client.get_scores()) is list

def test_score():
    assert type(client.get_score("sadam")) is dict

def test_score_fail():
    with pytest.raises(hscp.InvalidName):
        client.get_score("your mom")

def test_score_uploader():
    assert client.post_score("sadam", randint(1, 100)) is True

def test_logout():
    client.logout()
    assert client.token is None
