# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 12:14:34 2025

@author: Tian
"""
# attempt log in
import requests
from bs4 import BeautifulSoup
import re

headers = {'user-agent': 'fic_logger +sz5120@github.com'}
AO3_LOGIN_URL = 'https://archiveofourown.org/users/login'
AO3_FAILED_LOGIN = 'The password or user name you entered doesn\'t match our records.'

#soup=requests.get(AO3_LOGIN_URL,headers=headers)

def get_token(soup: BeautifulSoup) -> str:
    """Get authentication token for logging in to ao3."""

    token = (soup.find('form', class_='new_user').find('input', attrs={'name': 'authenticity_token'}).get('value'))
    return token

def get_payload(username: str, password: str, token: str) -> dict[str, str]:
    """Get payload for ao3 login."""

    payload = {
        'user[login]': username,
        'user[password]': password,
        'user[remember_me]': '1',
        'authenticity_token': token
    }
    return payload


def string_exists(soup: BeautifulSoup, string: str) -> bool:
    pattern = string
    expression = re.compile(pattern)
    match = soup.find_all(text=expression)
    return len(match) > 0

def is_failed_login(soup: BeautifulSoup) -> bool:
    return string_exists(soup, AO3_FAILED_LOGIN)
'''

sess=requests.Session()
req=sess.get(AO3_LOGIN_URL)
soup=BeautifulSoup(req.text,'html.parser')
token=get_token(soup)
payload=get_payload(username, password, token)
response = sess.post(AO3_LOGIN_URL, data=payload, headers=headers)
new_soup=BeautifulSoup(response.text,'html.parser')

if is_failed_login(new_soup):
    print("Failed login")
    '''