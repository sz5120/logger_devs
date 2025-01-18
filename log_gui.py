#!/usr/bin/env python3
from nicegui import events, ui
import os
import csv
import ao3_logger as ao3
from io import StringIO
import sys
#need environment 310, and cd /d D:\Git_sz5120\Logger_dev

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



pwd = os.path.abspath(os.path.dirname(__file__))
#pwd = os.path.abspath(os.path.dirname('__file__')) #for testing in console
CSV_FILE = "data_csv.csv"
'''
# Ensure the CSV file exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "title", "words"])  # Add default headings
'''
# Function to read data from the CSV file

def read_csv():
    global pwd
    folder_name="Data"
    file_name="data_csv.csv"
    
    dir_path=pwd+"\\"+folder_name
    file_path=dir_path+"\\"+file_name
    
    print(file_path)
    if not os.path.exists(file_path):
        print("File does not exist at ",file_path," creating blank file")
        
        #create a blank file
            #categories of info we want
        meta_dict=ao3.create_blank_dict() #create a blank dict
        ao3.csv_writer_ao3(meta_dict)
        
    
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file,delimiter=",")
        print("found file, opening")    
        return [row for row in reader if any(row.values())]
'''
# Function to write data to the CSV file
def write_csv(data):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["author", "title", "words"])
        writer.writeheader()
        writer.writerows(data)
'''
# Read initial data

data = read_csv()

#initilaise some things
total_words=None
total_words_label=None
add_row_button=None
search_res=None

# Sample function to autopopulate fields based on search

#for the search/input fields, we have
# ao3_logger.scrape_from_ao3(fic_id) and ao3_logger.csv_writer_ao3(meta_dict)
# if we already have the source scraped, we can also do: get_meta_info(fic_id,soup)


# Build the NiceGUI interface
def update_table():
    log_table.rows.clear()
    for row in data: #only reading data here
        #print(row)
        if row["title"]: #only if there's a title field
            #print(row['date_fin'])
            log_table.add_row(row)
    
    

def refresh_table():
    print("refreshing table")
    update_textbox()
    global data, total_words
    data=read_csv()
    update_table()
    if len(data)>1: #only do this if there's something in it
        recalculate_stats()
    

def clear_table():
    log_table.rows.clear()


def perform_search():
    # this will call fic_logger search_from_ID
    global search_res
    print("resetting button")
    update_textbox()
    reset_add_button()
    print("clearing input fields")
    update_textbox()
    clear_input_fields()
    search_res = ao3.scrape_from_ao3(fic_id_input.value)
    #search_res = ao3.scrape_from_ao3(fic_id)
    #print(search_res)
    update_textbox()
    #date_field.value=search_res["date_fin"]
    author_input.value = search_res["author"]
    title_input.value = search_res["title"]
    wordcount_input.value = search_res["words"]
    fandom_input.value = search_res["fandom"]
    rating_input.value = search_res["rating"]
    url_input.value=search_res["url"]

def set_date_field():
    global search_res
    search_res['date_fin']=date_field.value
    print(search_res['date_fin'])
    
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
    global data 
    if search_res:
        #data.append(search_res)
        set_date_field()
        ao3.csv_writer_ao3(search_res)
        #...also need to add in the if there's manual stuff.....
        #table.add_row(search_res)
        #author_input.value = title_input.value = wordcount_input.value = ""
        #wordcount_input.value=fandom_input.value= rating_input.value =url_input.value=""
        
        refresh_table()
        add_row_button.text="Added"
        print(search_res)
        update_textbox()
    else:
        print("nothing to add")
        update_textbox()
#append this new search to the csv only if we hit add here

def reset_add_button():
    add_row_button.text = "Add Row"    
    
def clear_input_fields():
    author_input.value = title_input.value = wordcount_input.value = ""
    wordcount_input.value=fandom_input.value= rating_input.value =url_input.value=""

columns=[
    {"name": "date_fin", "label": "Date", "field": "date_fin"},
    #{"name": "status", "label": "Status", "field": "status"},
    {"name": "title", "label": "Title", "field": "title","style":"max-width: 15%; white-space: nowrap; overflow-wrap: normal; text-overflow: ellipsis;"},
    {"name": "author", "label": "Author", "field": "author","style":"max-width:15%"},
    {"name": "words", "label": "Words", "field": "words","style":"max-width:15%"},
    {"name": "published", "label": "Published", "field": "published","style":"max-width:15%"},
    {"name": "chapters", "label": "Chapters", "field": "chapters","style":"max-width:15%"},
    {"name": "fandom", "label": "Fandom", "field": "fandom","style":"max-width:15%,text-overflow: ellipsis"},
    {"name": "url", "label": "URL", "field": "url","style":"max-width:15%"},
]

# actually building the stuff now

with ui.column():
    ui.label('Will add date started and finished. MANUAL ADD DOES NOT WORK YET. Date can be added to the csv file but will not show in table. I do not know why')
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
        
        
                   
        

    
    with ui.row():
        author_input = ui.input(label="Author").props('clearable').on('input', reset_add_button)
        title_input = ui.input(label="Title (Req.)").props('clearable').on('input', reset_add_button)
        wordcount_input = ui.input(label="Word Count").props('clearable').on('input', reset_add_button)
        fandom_input = ui.input(label="Fandom").props('clearable').on('input', reset_add_button)
        rating_input =ui.input(label="Rating").props('clearable').on('input', reset_add_button)
        url_input=ui.input(label="URL").props('clearable').on('input', reset_add_button)

        add_row_button=ui.button("Add Row", on_click=add_new_row)
        #ui.button('Clear', on_click=data_fields_container.clear)

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

def recalculate_stats():    
    global total_words
    if len(data)>1:
        total_words=sum([int(ent["words"].replace(',','')) for ent in data])
    total_words_label.text = f"Total words: {total_words}" 
    print("recalculating stats")
    update_textbox()
    
with ui.row():
    ui.button("Refresh Table", on_click=refresh_table)
    ui.button("Clear Table (not working)",on_click=clear_table)
    ui.button("Recalculate Stats", on_click=recalculate_stats)


with ui.row():
    total_words_label = ui.label(f"Total words: {total_words}")
    #ui.label("total words: "+ str(total_words))
    



def export_csv():
    with open('export_data.csv',"w") as data_f:
        print("writing to file")
        update_textbox()
        data_w=csv.DictWriter(data_f,data[0].keys())
        data_w.writeheader()
        for row in data:
            data_w.writerow(row)    
    ui.download('export_data.csv')

ui.button('Export to CSV', on_click=export_csv)



# Redirect stdout
#redirect_stdout()

# Layout for the UI
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
        ui.button("Update", on_click=update_textbox)
        ui.button("Redirect stdout to here", on_click=redirect_stdout)
        ui.button("Restore stdout to normal function", on_click=restore_stdout)
    
        # Button to clear the stdout and the textbox
        ui.button("Clear Output", on_click=lambda: (stdout_capture.truncate(0), stdout_capture.seek(0), update_textbox()))


ui.run()
#ui.run(on_air=True)