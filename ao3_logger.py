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
warnings.simplefilter('ignore')


# so we're not constantly scraping this for now

pwd = os.path.abspath(os.path.dirname(__file__)) #for running as file
#pwd = os.path.abspath(os.path.dirname('__file__')) #for testing in console
json_file="src.json"
json_path=pwd+"\\"+json_file

src_dict={}
if not os.path.exists(json_path):
    src_dict={}
else:
    with open(json_path) as json_file:
        src_dict=json.load(json_file)

# error handling taken from ao3 scraper

def access_denied(soup):
    if (soup.find(class_="flash error")):
        return True
    if (not soup.find(class_="work meta group")):
        if soup.find("h3",class_="heading").text=="Sorry!":
            print("This content is restricted to logged in users only")
        return True
    
    return False

#taken from ao3 scraper
def get_tag_info(category, meta):
	'''
	given a category and a 'work meta group, returns a list of tags (eg, 'rating' -> 'explicit')
	'''
	try:
		tag_list = meta.find("dd", class_=str(category) + ' tags').find_all(class_="tag")
	except AttributeError as e:
		return []
	return [unidecode(result.text) for result in tag_list] 

def create_blank_dict():
    #categories of info we want
    work_id_names=['fic_id']
    headmeta_names=['author','title']
    stat_names=['words','published','status','chapters']
    tag_names=['rating','category','fandom','relationship','character','warning','freeform']
    url_names=['url']
    date_names=['date_fin'] #by default this will be current date unless overwritten
    #dictionary with categories as keys
    meta_dict=dict.fromkeys(work_id_names+headmeta_names+stat_names+tag_names+url_names+date_names)
    
    return meta_dict
    
def get_meta_info(fic_id,soup,date=None):
    #will return a dictionary with author title word count tags date published(?)
    # and from tags we want: fandom pairing characters
    #tags = ['rating', 'category', 'fandom', 'relationship', 'character', 'freeform']
    #categories = ['language', 'published', 'status', 'words', 'chapters', 'comments', 'kudos', 'bookmarks', 'hits'] 
    ''
    #categories of info we want
    #work_id_names=['fic_id']
    #headmeta_names=['author','title']
    stat_names=['words','published','status','chapters']
    tag_names=['rating','category','fandom','relationship','character','warning','freeform']
    #url_names=['url']
    #date_names=['date'] #by default this will be current date unless overwritten
    '''' this has now been moved to "create_blank_dict"
    
    #dictionary with categories as keys
    meta_dict=dict.fromkeys(work_id_names,headmeta_names+stat_names+tag_names+url_names)
'''
    meta_dict=create_blank_dict()
    #get the work meta and the heading/preface meta from the soup
    meta = soup.find("dl", class_="work meta group")
    headmeta=soup.find("div",class_="preface group")

    #get the author and title
    meta_dict['fic_id']=fic_id
    meta_dict['author'] = [tag.contents[0] for tag in headmeta.find("h3", class_="byline heading").contents if tag.name=='a'] #may be multiple authors
    meta_dict['title']= unidecode(headmeta.find("h2", class_="title heading").string).strip()
    

    # get the info for listed stats
    for stat in stat_names:
        if stat=='status':
            if meta.find("dt",class_=stat):
                meta_dict[stat]='Completed' if unidecode(meta.find("dt",class_=stat).text)=='Completed' else ('Updated: '+unidecode(meta.find("dd",class_=stat).text))
            else:
                meta_dict[stat]='oneshot'
        else:
            meta_dict[stat] = unidecode(meta.find("dd",class_=stat).text)

    
    
    #get the info for listed tags
    for cat in tag_names:
        meta_dict[cat]=get_tag_info(cat,meta)
        
    #include URL at end
    meta_dict['url']='http://archiveofourown.org/works/'+str(fic_id)
    
    meta_dict['date_fin']=date
    return meta_dict


def get_soup_ao3(fic_id):
    global src_dict
    url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true'
    print("from url:",url)
    
    #below two lines are place holders until i figure out what ethical scraping means
    header_info=''
    headers=header_info   
    
    req = requests.get(url, headers=headers)
    src=req.text
    src_dict[fic_id]=src
    save_src_json(src_dict) #man this thing is gonna hate mre 
    if req.status_code>=400:
        print("Error scraping fic_id:", fic_id, " and now exiting,", req.status_code)
        return None
    
    return src

def scrape_from_ao3(fic_id):
    print('Scraping:', fic_id)
    global src_dict
    if str(fic_id) in src_dict:
        src=src_dict[str(fic_id)]
        print("already scraped, moving on")
    else:
        src=get_soup_ao3(fic_id)
        
        if not src: return None
        
    
    soup = BeautifulSoup(src, 'html.parser')
    
    if (access_denied(soup)):
        print('Access Denied')
        return None
    
    print("Getting Info")
    meta_dict=get_meta_info(fic_id,soup)
    print("meta info retrieved")

    return meta_dict


## Write metadata to csv
# In a folder called Data with a file called data_csv.csv
def csv_writer_ao3(meta_dict):
    global pwd
    if not meta_dict:
        return
    
    folder_name="Data"
    file_name="data_csv.csv"
    dir_path=pwd+"\\"+folder_name
    file_path=dir_path+"\\"+file_name     
    
    dir_exists=os.path.exists(dir_path)
    #check if directory exists
    if not dir_exists:
        os.makedirs(dir_path)
    
    file_exists=os.path.exists(file_path)
    
    #meta_dict['date']=date
    
    
    
    with open(file_path,"a") as data_f:
        print("writing to file")
        data_w=csv.DictWriter(data_f,meta_dict.keys())
        if not file_exists: data_w.writeheader()
        data_w.writerow(meta_dict)

def save_src_json(src_dict):
    with open(json_path,'w') as f:
        json.dump(src_dict,f)


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

# for testing purposes, we'll save the 