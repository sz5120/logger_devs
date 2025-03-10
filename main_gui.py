#region #### HEADER ######
# Header shit goes here
#endregion ### END HEADER


# region #### IMPORT PACKAGES ###

# import things
from nicegui import app, run, events, ui, ElementFilter
import os
import ao3_functions as ao3



import csv
#import ao3_logger as ao3
from io import StringIO
import sys
import pandas as pd
#need environment 310, and cd /d D:\Git_sz5120\Logger_Dev0
import requests
#import webview

from helpers import strings

#endregion ### END IMPORT ###

# region ### startup stuff ###

# get path
pwd=os.path.dirname(os.path.realpath(sys.argv[0]))

# create session
headers=strings.AO3_HEADER
user_session=requests.Session()

#endregion




@ui.page('/main')
def main_page():
    with ui.header(elevated=False).style('height:75px').classes('bg-gray-500 items-center float-right'):
        ui.label('Log In: ')
        with ui.row().classes('w-5/6 float-right items-center gap-1'):
            un_input=ui.input(label="Username").props('outlined dense color="white" size=12')
            pw_input=ui.input(label="Password").props('outlined dense color="white" size=12')
            ui.button("Log In",on_click=lambda: ao3.login_here(un_input.value,pw_input.value,user_session))

    with ui.footer(elevated=True):
        ui.button('close from page', on_click=app.shutdown)    



    # region ### APPLY FORMATTING ###

    ElementFilter(kind=ui.button).props('flat no-caps padding="5px" color="grey-10" style="size:15px; color: black; background:#700"')
    #ElementFilter(kind=ui.input).props('outlined dense color="red-500" style="size:15px"')

    # endregion ### END FORMATTING###


main_page()
ui.button("close",on_click=app.shutdown)

ui.run(native=True)