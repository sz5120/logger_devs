#!/usr/bin/env python3
from nicegui import app, run, events, ui
import os
import csv
import ao3_logger as ao3
from io import StringIO
import sys
import pandas as pd
#need environment 310, and cd /d D:\Git_sz5120\Logger_Dev0
import requests
#import webview

##########################

''' Some experimental stuff
'''
stdout_capture = StringIO()
std_out_status_label=None

# Function to redirect stdout to the StringIO object
def redirect_stdout():
    sys.stdout = stdout_capture
    std_out_status_label.text="Current status: Printing to here"

# Function to restore the original stdout
def restore_stdout():
    sys.stdout = sys.__stdout__
    std_out_status_label.text="Current status: Printing to console"

# Function to update the textbox with the current stdout contents
def update_textbox():
    stdout_text.value = stdout_capture.getvalue()

# Example function that prints to stdout
def example_function():
    print("This is a test message!")
    print("Another line of output!")
    update_textbox()



###############################



## FILE PICKER EXPERIMENT TIME



async def choose_file():
    #folder = await app.native.main_window.create_file_dialog(dialog_type=webview.FOLDER_DIALOG,allow_multiple=False)
    file = await app.native.main_window.create_file_dialog(allow_multiple=False)
    #for file in files:
        #ui.notify(file)
    #    print(file)
    #ui.notify(folder)
    print(file)
    file_dir_label.value=file[0]
    
        
async def set_path():
#window.create_file_dialog(dialog_type=OPEN_DIALOG, directory='', allow_multiple=False, save_filename='', file_types=())`
    global file_path
    file_path=file_dir_label
    #pwd=file_dir_label.value
    ui.notify(file_path)



app.native.settings['ALLOW_DOWNLOADS'] = True

# this will create a default in a temporary folder

#pwd = os.path.abspath(os.path.dirname(__file__))
#pwd = os.path.abspath(os.path.dirname('__file__')) #for testing in console
#OUTPUT_FILE = "export_csv.csv"


#might need this for executable instead
pwd=os.path.dirname(os.path.realpath(sys.argv[0]   ))

folder_name="Data"
file_name="df_csv.csv"

dir_path=pwd+"\\"+folder_name
#file_path=dir_path+"\\"+file_name

'''
# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "title", "words"])  # Add default headings
'''
# Function to read data from the CSV file

#changed it ot read from a dataframe instead
def read_csv_fl(dir_path,file_name):
    file_path=dir_path+"\\"+file_name   
    print(pwd,file_path)
    if not os.path.exists(file_path):
        print("File does not exist at ",file_path," creating blank file")
        #create a blank file
            #categories of info we want
        meta_df=ao3.create_blank_df() #create a blank dict
        ao3.csv_writer_ao3(meta_df,dir_path,file_name)
        
    data_df=pd.read_csv(file_path)
    #data_df=data_df.astype({'chapters':'string','start_date':'datetime64[ns]','end_date':'datetime64[ns]'})
    data_df=data_df.astype({'chapters':'string'})
    return data_df
    '''
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file,delimiter=",")
        print("found file, opening")    
        return [row for row in reader if any(row.values())]
'''
'''
# Function to write data to the CSV file
def write_csv(data):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["author", "title", "words"])
        writer.writeheader()
        writer.writerows(data)
'''
# Read initial data

data_df = read_csv_fl(dir_path,file_name)
data=data_df.to_dict('records')

#initilaise some things
total_words=None
total_words_label=None
add_row_button=None
search_res=None
headers = {'user-agent': 'fic_logger +sz5120@github.com'}
user_session=requests.Session() 
# Sample function to autopopulate fields based on search

#for the search/input fields, we have
# ao3_logger.scrape_from_ao3(fic_id) and ao3_logger.csv_writer_ao3(meta_dict)
# if we already have the source scraped, we can also do: get_meta_info(fic_id,soup)


### COLUMN DEFINITIONS (consider doing this outside?)   
columns=[
    {"name": "date_fin", "label": "Date", "field": "date_fin"},
    #{"name": "status", "label": "Status", "field": "status"},
    {"name": "title", "label": "Title", "field": "title","style":"max-width: 15%; white-space: nowrap; overflow-wrap: normal; text-overflow: ellipsis;"},
    {"name": "author", "label": "Author", "field": "author","style":"max-width:15%"},
    {"name": "words", "label": "Words", "field": "words","style":"max-width:15%"},
    {"name": "published", "label": "Published", "field": "published","style":"max-width:15%"},
    {"name": "chapters", "label": "Chapters", "field": "chapters","style":"max-width:15%"},
    {"name": "fandom", "label": "Fandom", "field": "fandom","style":"max-width:15%,text-overflow: ellipsis"},
    {"name": "relationship", "label": "Pairing", "field": "relationship","style":"max-width:15%,text-overflow: ellipsis"},
    {"name": "url", "label": "URL", "field": "url","style":"max-width:15%"},
]

'''
#### start up call #can probably use this to ask user to do some selectiions first if needed
def startup():
    global data_df,data
    data_df = read_csv_fl(dir_path,file_name)
    data=data_df.to_dict('records')
    refresh_table()
    print("starting up")
'''

###### DISPLAYING DATA IN THE TABLE (will be changed to aggrid)
def update_table():
    if log_table.rows: log_table.rows.clear() 
    for row in data: #only reading data here
        #print(row)
        if row["title"]: #only if there's a title field
            #print(row['author'])
            log_table.add_row(row)
    log_table.update()
    '''
def update_table():
    log_table.rows.clear()
    log_table.from_pandas(data_df)
    log_table.update()
'''
def refresh_table():
    print("refreshing table")
    update_textbox()
    global data, total_words
    data_df=read_csv_fl(dir_path,file_name)
    data=data_df.to_dict('records')
    update_table()
    if len(data)>0: #only do this if there's something in it
        recalculate_stats()
    

def clear_table():
    log_table.rows.clear()
    log_table.update()


#### SEARCH ON AO3 AND OTHER
#changed this to async, hopefully this iddn't break anything

async def perform_search():
    # this will call fic_logger search_from_ID
    global search_res
    print("resetting button")
    update_textbox()
    reset_add_button()
    print("clearing input fields")
    update_textbox()
    clear_input_fields()
    
    search_res = await(ao3.scrape_from_ao3(fic_id_input.value,user_session)) #need to call it as an await
    print(search_res,search_res.info)
    #print(search_res['author'])
    #search_res = ao3.scrape_from_ao3(fic_id)
    #print(search_res)
    update_textbox()
    
    #search_output=search_res.to_dict('records')[0]
    
    author_input.value =[x for x in search_res.iloc[0]['author']]
    title_input.value = search_res.iloc[0]['title']
    wordcount_input.value = search_res.iloc[0]['words']
    fandom_input.value = [x for x in search_res.iloc[0]['fandom']]
    relationship_input.value = [x for x in search_res.iloc[0]["relationship"]]
    rating_input.value = search_res.iloc[0]["rating"]
    url_input.value=search_res.iloc[0]["url"]

def set_date_field():
    global search_res
    #search_res['end_date']=date_field.value
    #print(search_res['date_fin'])
    
    
#### ADD NEW ROW (also will be changed)    
def add_new_row():
    # new_row = {
    #     "author": author_input.value,
    #     "title": title_input.value,
    #     "words": wordcount_input.value,
    #     "fandom": title_input.value,
    #     "rating": wordcount_input.value,
    #     "title": title_input.value,
    #     "words": wordcount_input.value,
    # }
    global search_res
    global data_df 
    #if search_res.any():
    print("adding row")
    #data.append(search_res)
    set_date_field()
    data_df=pd.concat([data_df,search_res],ignore_index=True)
    data_df=data_df.astype({'chapters':'string','start_date':'datetime64[ns]','end_date':'datetime64[ns]'})
    if len(data_df)==1:
        ao3.csv_writer_ao3(data_df,dir_path,file_name)
    else:
        ao3.csv_writer_ao3(data_df.tail(1),dir_path,file_name)
    #...also need to add in the if there's manual stuff.....
    #table.add_row(search_res)
    #author_input.value = title_input.value = wordcount_input.value = ""
    #wordcount_input.value=fandom_input.value= rating_input.value =url_input.value=""
    
    refresh_table()
    add_row_button.text="Added"
    print(search_res)
    update_textbox()
    '''
    else:
        print("nothing to add")
        update_textbox()
#append this new search to the csv only if we hit add here
'''
def reset_add_button():
    add_row_button.text = "Add Row"    
    
def clear_input_fields():
    author_input.value = title_input.value = wordcount_input.value = ""
    wordcount_input.value=fandom_input.value= rating_input.value =url_input.value=""



#### STATS WILL INCLUDE THINGS LIKE PAIRINGS ETC


def recalculate_stats():    
    global total_words
    if len(data)>0:
        total_words=sum([int(ent["words"].replace(',','')) for ent in data])
    total_words_label.text = f"Total words: {total_words}" 
    print("recalculating stats")
    update_textbox()
   
    


# actually building the stuff now

def refresh_session():
    global user_session
    user_session=requests.Session() 
    
    
    
#### LOGIN INFO    
    
def get_login_info():
    username=un_input.value
    password=pw_input.value
    print("help",username,password)
    update_textbox()


    
def dummy_search():
    print("pressed a button")
    
    
#### EXPORTING FILSE


def export_csv():
    with open('export_data.csv',"w") as data_f:
        print("writing to file")
        update_textbox()
        data_w=csv.DictWriter(data_f,data[0].keys())
        data_w.writeheader()
        for row in data:
            data_w.writerow(row)    
    ui.download('export_data.csv')
    exit()
    
#need to add an async to this
async def close_and_export():
    await export_csv()
    app.shutdown()


#### UI CREATION


## Search, log-in, and inputs
with ui.row():
    ui.button('close', on_click=app.shutdown)
    ui.button('close and save', on_click=lambda:close_and_export())


with ui.column():
    ui.label('Will add date started and finished. \n MANUAL ADD DOES NOT WORK YET. \n \
If entries are not showing up, go to last page. Log in works, however fetching fics is spotty.\n \
Also the search results are no longer showing up in the fields but they can still be added').style('white-space: pre-wrap')
    
    with ui.row():
        with ui.column():
            #fic_id_input = ui.input(label="Search",validation=lambda value: 'Too short' if len(value) < 2 else None).props('clearable')
            fic_id_input = ui.input(label="AO3 Work ID").props('clearable')
            search_res={}
    
            ui.button("Search", on_click=perform_search).tooltip('The number part after /works/[NUMBER]')
            
    
        #taken wholesale from the nicegui demo until i figure out wtf is going on
        date_field=ui.input('Date').on('change',set_date_field)
        with date_field as date:
            with ui.menu().props('no-parent-event') as menu:
                with ui.date().bind_value(date).on('change',set_date_field):
                    with ui.row().classes('justify-end'):
                        ui.button('Close').on('click',menu.close).props('flat')
                    
            with date.add_slot('append'):
                ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
        
        with ui.column():
            un_input=ui.input(label="Username")
            pw_input=ui.input(label="Password")
            #ui.button("Submit", on_click= get_login_info)
            
        with ui.column():
            ui.button("Log in",on_click=lambda: ao3.login_here(un_input.value,pw_input.value,user_session))
            ui.button("Refresh session", on_click=lambda: refresh_session())
        
        #set path directory
        with ui.column():
            file_dir_label=ui.input(label="Working_Directory")
            ui.button('Choose Existing File', on_click=choose_file)
            ui.button('confirm',on_click=set_path)
    
    with ui.row():
        author_input = ui.input(label="Author").props('clearable').on('input', reset_add_button)
        title_input = ui.input(label="Title (Req.)").props('clearable').on('input', reset_add_button)
        wordcount_input = ui.input(label="Word Count").props('clearable').on('input', reset_add_button)
        fandom_input = ui.input(label="Fandom").props('clearable').on('input', reset_add_button)
        relationship_input = ui.input(label="Pairing").props('clearable').on('input', reset_add_button)
        rating_input =ui.input(label="Rating").props('clearable').on('input', reset_add_button)
        url_input=ui.input(label="URL").props('clearable').on('input', reset_add_button)

        add_row_button=ui.button("Add Row", on_click=lambda:add_new_row())
        #ui.button('Clear', on_click=data_fields_container.clear)

## table display

with ui.row():
#    with ui.card().style(f'width: {fixed_container_width}; height: {fixed_container_height}; overflow: auto;'):
    log_table = ui.table(
        columns=columns,
        rows=data,
        row_key="title",
        pagination=5,
        column_defaults={
            'align': 'left',
            'max-width': '15%', 
            }
    ).props('virtual-scroll')
    log_table.style("width: 1000px; height: 350px; overflow: auto; overflow-wrap: auto")

with ui.row():
    ui.button("Refresh Table", on_click=lambda:refresh_table())
    ui.button("Clear Table (maybe)",on_click=lambda:clear_table())
    ui.button("Recalculate Stats", on_click=lambda:recalculate_stats())


with ui.row():
    total_words_label = ui.label(f"Total words: {total_words}")
    #ui.label("total words: "+ str(total_words))
    

## export button

ui.button('Export to CSV', on_click=export_csv)



# Redirect stdout
#redirect_stdout()


# Debugging window
with ui.row():
    with ui.column():
        ui.label("Redirect standard output to this textbox if you want to keep an eye on error debugging messages.")
        # Textbox to display stdout
        stdout_text = ui.textarea(label="Standard Output", value="").style(
            "width: 500px; height: 200px; overflow: auto;"
        )
        std_out_status_label=ui.label("Current status: Printing to console")
    with ui.column():
        # Button to trigger example function
        ui.button("Update", on_click=lambda: update_textbox())
        ui.button("Redirect stdout to here", on_click= lambda: redirect_stdout())
        ui.button("Restore stdout to normal function", on_click=lambda: restore_stdout())
    
        # Button to clear the stdout and the textbox
        ui.button("Clear Output", on_click=lambda: (stdout_capture.truncate(0), stdout_capture.seek(0), update_textbox()))

#app.on_startup()
ui.run(native=True,reload=True)
#ui.run(native=True,reload=False)
#ui.run(on_air=True)