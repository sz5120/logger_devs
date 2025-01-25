# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 11:59:47 2025

@author: Tian
"""
import requests
from bs4 import BeautifulSoup
import argparse
import time
import os
import csv
import sys
from unidecode import unidecode
import json
import warnings
import pandas as pd
from helpers import strings
from helpers import login
warnings.simplefilter('ignore')


# so we're not constantly scraping this for now

pwd = os.path.abspath(os.path.dirname(__file__)) #for running as file
#pwd = os.path.abspath(os.path.dirname('__file__')) #for testing in console

#ill eventually get this as an input

json_file="src.json"
json_path=pwd+"\\"+json_file

src_dict={}
if not os.path.exists(json_path):
    src_dict={}
else:
    with open(json_path) as json_file:
        src_dict=json.load(json_file)


# create log in
headers = {'user-agent': 'fic_logger +sz5120@github.com'}
#user_session=requests.Session() 


def error_dump_file(error_content):
    with open("error_log.txt","w") as f:
        f.write(error_content)

def login_here(username,password,curr_session):
    print("logging in")
    req=curr_session.get(strings.AO3_LOGIN_URL,headers=headers)
    soup=BeautifulSoup(req.text,'html.parser')
    token=login.get_token(soup)
    payload=login.get_payload(username, password, token)
    
    #pass in the log in info
    login_response = curr_session.post(strings.AO3_LOGIN_URL, data=payload, headers=headers)
    print(login_response.status_code)
    #check if log-in failed  
    
    if login.is_failed_login(BeautifulSoup(login_response.text,'html.parser')):
        print("Failed login")
        #logged_in_lable.text="Failed"
        #return "Failed"
    else:
        print("Logged in")
        #return "Logged in"
        #logged_in_lable.text="Logged in"

#returns a dataframe
def scrape_from_ao3(fic_id,curr_session):
    print('Scraping:', fic_id)
    global src_dict
    if str(fic_id) in src_dict:
        src=src_dict[str(fic_id)]
        print("already scraped, moving on")
    else:
        src=get_soup_ao3(fic_id,curr_session)
        
        if not src: return None
        
    
    soup = BeautifulSoup(src, 'html.parser')
    
    if (access_denied(soup)):
        print('Access Denied')
        return None
    
    print("Getting Info")
    #meta_dict=get_meta_info(fic_id,soup)
    meta_df=pd.DataFrame([get_meta_info(fic_id,soup)])
    
    print("meta info retrieved")
    
    #except now we actually want to add this to a dataframe
    #return meta_dict
    return meta_df



def get_soup_ao3(fic_id,curr_session):
    global src_dict
    url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true'
    print("from url:",url)
    
    #below two lines are place holders until i figure out what ethical scraping means
    #header_info=''
    #headers=header_info   
    #print(headers)
    req = curr_session.get(url, headers=headers)
    print("status code:",req.status_code)
    src=req.text
    
    
    if req.status_code>=400:
        print("Error scraping fic_id:", fic_id, " and now exiting,", req.status_code)
        error_dump_file(src,'html.parser')
        return None
    if (access_denied(BeautifulSoup(src, 'html.parser'))):
        print('Access Denied')
        return None
    
    src_dict[fic_id]=src
    save_src_json(src_dict) #man this thing is gonna hate mre 
    return src


# error handling taken from ao3 scraper

def access_denied(soup):
    if (soup.find(class_="flash error")):
        return True
    if (not soup.find(class_="work meta group")):
        if soup.find("h3",class_="heading").text=="Sorry!":
            print("This content is restricted to logged in users only, please log in")
        return True
    
    return False

#taken from ao3 scraper
def get_tag_info(category, meta):
	'''
	given a category and a 'work meta group, returns a list of tags (eg, 'rating' -> 'explicit')
	'''
	try:
		tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
	except AttributeError as e: #change this error handling
		return []
	return [unidecode(result.text) for result in tag_list] 

def create_blank_df():
    #categories of info we want
    type_names=['type'] #for now this will also have manual word options of fanfic, book, etc
    work_id_names=['fic_id']
    headmeta_names=['author','title']
    stat_ao3_names=['words','published','status','chapters']
    stat_book_names=['pages','runtime'] 
    tag_names=['rating','category','fandom','relationship','character','warning','freeform']
    url_names=['url']
    date_names=['start_date','end_date'] #by default this will be current date unless overwritten
    status_names=['reading_status'] #this will manually have options of "in progress", "want to read","reread","finished"
    #dictionary with categories as keys
    df=pd.DataFrame(columns=type_names+work_id_names+headmeta_names+stat_ao3_names+stat_book_names+\
                    tag_names+url_names+date_names+status_names)
        
    
    df['chapters']=df['chapters'].astype(dtype='string')
    df['start_date']=df['start_date'].astype(dtype='datetime64[ns]')
    df['end_date']=df['end_date'].astype(dtype='datetime64[ns]')
    return df


    
def get_meta_info(fic_id,soup):
    #will return a dictionary with author title word count tags date published(?)
    # and from tags we want: fandom pairing characters
    #tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
    #categories = ['language', 'published', 'status', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits'] 
    ''
    #categories of info we want
    work_id_names=['fic_id']
    headmeta_names=['author','title']
    stat_names=['words','published','status','chapters']
    tag_names=['rating','category','fandom','relationship','character','warning','freeform']
    url_names=['url']
    #date_names=['date'] #by default this will be current date unless overwritten
    '''' this has now been moved to "create_blank_dict"
    
    #dictionary with categories as keys
    
'''
    meta_dict=dict.fromkeys(work_id_names+headmeta_names+stat_names+tag_names+url_names)
    #meta_dict=create_blank_dict()
    #get the work meta and the heading/preface meta from the soup
    meta = soup.find("dl", class_="work meta group")
    headmeta=soup.find("div",class_="preface group")

    #get the author and title
    meta_dict['fic_id']=fic_id
    meta_dict['author'] = [tag.contents[0] for tag in headmeta.find("h3", class_="byline heading").contents if tag.name=='a'] #may be multiple authors
    title_soup=''.join([t for t in headmeta.find("h2",class_="title heading").contents if t.name!='img'])
    meta_dict['title']= title_soup.strip()
 
    # get the info for listed stats
    for stat in stat_names:
        if stat=='status':
            if meta.find("dt",class_=stat):
                meta_dict[stat]='Completed' if unidecode(meta.find("dt",class_=stat).text)=='Completed' else ('Updated: '+unidecode(meta.find("dd",class_=stat).text))
            else:
                meta_dict[stat]='oneshot'
        else:
            meta_dict[stat] = str(unidecode(meta.find("dd",class_=stat).text))

    
    
    #get the info for listed tags
    for cat in tag_names:
        meta_dict[cat]=get_tag_info(cat,meta)
        
    #include URL at end
    meta_dict['url']='http://archiveofourown.org/works/'+str(fic_id)
    
    meta_dict['type']='ao3'
    return meta_dict

## Write metadata to csv
# In a folder called Data with a file called data_csv.csv
def csv_writer_ao3(df):
    global pwd
    if df.empty:
        print("Nothing to write")
        return False
    folder_name="Data"
    file_name="df_csv.csv"
    dir_path=pwd+"\\"+folder_name
    file_path=dir_path+"\\"+file_name     
    
    dir_exists=os.path.exists(dir_path)
    #check if directory exists
    if not dir_exists:
        os.makedirs(dir_path)
    
    
    #file_exists=os.path.exists(file_path)
    write_header=False if os.path.exists(file_path) else True
    print("write header:",write_header)
    #meta_dict['date']=date
    #if it exists, don't write, otherwise, write
    
    df.to_csv(file_path, mode='a', index=True, header=write_header)
    print("wrote to file")
    '''
    with open(file_path,"a") as data_f:
        print("writing to file")
        data_w=csv.DictWriter(data_f,meta_dict.keys())
        if not file_exists: data_w.writeheader()
        data_w.writerow(meta_dict)
    '''
def save_src_json(src_dict):
    with open(json_path,'w') as f:
        json.dump(src_dict,f)

#df=create_blank_df()
#print("loading file")
'''



#testing the call
# fic_id=32262178 should be access denied
#fic_id=61766950 #should be allowed
fic_id=33751156 #utsdih
fic_id=12005586 #rwm
fic_id=61766950 #to the world
fic_id=61781653 #another one
fic_id=10098500 #another one
# ahot https://archiveofourown.org/works/30248028
scrape_from_ao3(fic_id)

# have saved metas: rwm_soup, rwm_meta,ahot_soup,ahot_meta,utsdih_soup,utsdih_meta
'''

'''
def scrape_and_write(fic_id):
    global df
# for testing purposes, we'll save the 
    output=scrape_from_ao3(fic_id)
    df=pd.concat([df,output],ignore_index=True)
    df=df.astype({'chapters':'string','start_date':'datetime64[ns]','end_date':'datetime64[ns]'})
    if len(df)==1:
        csv_writer_ao3(df)
    else:
        csv_writer_ao3(df.tail(1))

fic_id=61766950
scrape_and_write(fic_id)

fic_id=12005586
scrape_and_write(fic_id)

fic_id=33751156
scrape_and_write(fic_id)

fic_id=6954559
scrape_and_write(fic_id)
'''