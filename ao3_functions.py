# import functions


# this part will eventually be called outside
import requests
from helpers import strings

headers=strings.AO3_HEADER
user_session=requests.Session()

from bs4 import BeautifulSoup
from helpers import login
from helpers import error_handling as errored

# region ### Logging In ###

# some dummy log-in values
# these are actually retrieved from the main GUI
import params
username=params.username
password=params.password
#password="wrong_pw"

def login_here(username,password,curr_session):
    print("Attemtping Log In")
    try:
        req=curr_session.get(strings.AO3_LOGIN_URL,headers=headers)
        soup=BeautifulSoup(req.text,'html.parser')
        token=login.get_token(soup)
        payload=login.get_payload(username, password, token)

        #pass in log in info
        login_response = curr_session.post(strings.AO3_LOGIN_URL, data=payload, headers=headers)
        print(login_response.status_code)

        if login.is_failed_login(BeautifulSoup(login_response.text,'html.parser')) or login.is_session_expired(BeautifulSoup(login_response.text,'html.parser')):
            raise errored.FailedLoginError
        
    
    except errored.FailedLoginError as e:
        print(e)
    except AttributeError as e:
        print(e)
    else:
        print("Logged In")

# endregion ### End Log In ###


# region ### Debugging Area ###

def check_errors():
    try:
        print("trying and then raising an error")
        raise errored.FailedLoginError
    except errored.FailedLoginError as e:
        print(e)
    except AttributeError as e:
        print(e)
    else:
        print("Logged In")

#check_errors()
#login_here(username,password,user_session)

# endregion