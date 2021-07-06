from os import stat_result
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import csv
import wget
import os
import json

"""
FUNCTIONS USED TO GET INFORMATION FROM THE URLS
"""
#requests http contents of a given URL and returns the class of all email exchanges
def request_content(URL):
    #waits for 2 seconds and then requests for the URL page contents 
    sleep(2)

    #getting the page contents
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    #section that has all of the communications
    communications_section = soup.find(id = 'comms')

    #class inside the previosuly aquired section that contains all the communications
    com_list = communications_section.find(class_='communications-list')

    return com_list

#given a list of emails, returns a list with only the body of text of the emails
def get_email_body_list(e_list):
    email_body_list = []
    for e in e_list:
        #testing to see if the email doesn't contain text
        body = e.find(class_='textbox__section communication-body')
        if (body): email_body_list.append(body.text)
    
    return email_body_list

#given a list of emails, returns a list with only the dates of the emails
def get_email_date_list(e_list):
    date_list = []
    for e in e_list:
        date = e.find(class_= 'date').text
        
        #correcting the formating of the dates
        date = date.replace(" ", "")
        date = date.replace("\n", "")
        
        date_list.append(date)
    
    return date_list

#given a list of emails, returns a list with only the name of who sent the email
def get_email_sender_list(e_list):
    email_body_list = []
    for e in e_list:
        #testing to see if the email doesn't contain text
        sender = e.find(class_='from')
        sender = sender.text
        
        #correcting the formating
        sender = sender.replace("From: ", "")

        email_body_list.append(sender)
    
    return email_body_list

#given the http contents of a page and an email class, returns a list of file links that were attached to the emails of email_class
def get_files_list(page_contents, email_class):
    #list of some type of email inside the previously aquired class 
    e_list = page_contents.find_all('section', class_= email_class)
    
    email_files_list = []
    #looping through all the emails
    for e in e_list: 
        files_class = e.find(class_='files') #finding the classe of attached files if there are any
        
        #if there are files attached, then loop through each of them
        if files_class:
            files = files_class.find_all('div', class_='file') #getting an iterable object of all the files in the files_class
            for f in files:
                #finding the class that contains the download link for the file
                file_actions = f.find(class_='file-actions')
                #finding the download link for the file
                file_link = file_actions.find_all('a', class_='action')[-1]['href']
                #appending the file link to the files list
                email_files_list.append(file_link)
    
    return email_files_list

"""
FUNCTIONS USED TO MAKE A LIST OF TUPLES CONTAINING THE INFORMATION AQUIRED BY THE FUNCTIONS ABOVE
"""
#given the http contents of a page and an email class, returns a list of tuples of the form (date the email was sent, email's body of text, name of who sent the email)
def make_dateBodySender_list(page_contents, email_class):
    #list of some type of email inside the previously aquired class 
    e_list = page_contents.find_all('section', class_= email_class)


    e_body_list = get_email_body_list(e_list)
    e_date_list = get_email_date_list(e_list)
    e_sender_list = get_email_sender_list(e_list)

    dateBody_list = []
    for (d,b,s) in zip(e_date_list, e_body_list, e_sender_list): dateBody_list.append((d,b,s))

    return dateBody_list

#compiles four lists of email date/body/sender tuples into a single email date/body/sender tuple list that is ordered by date
def compile_sort_lists(list1,list2,list3, list4):
    #compiling lists
    list1.extend(list2)
    list1.extend(list3)
    list1.extend(list4)

    #sorting emails by date
    list1.sort(key = lambda l: datetime.strptime(l[0], '%m/%d/%Y'))

    return list1

"""
FUNCTIONS USED TO MAKE DIRECTORIES FOR THE FILES ATTACHED TO THE EMAILS
"""
#given a directory name and potentially a path, makes a dir in the directory the main.py file is in + a potential extra path. It also returns the path for the dir made
def make_dir(name, path=None):
    parent_dir = os.path.dirname(os.path.abspath(__file__)) #path of the directory main.py is in
    
    if path: path = os.path.join(parent_dir, path)
    else: path = parent_dir

    path = os.path.join(path, name)
    os.mkdir(path)
    
    return path

#creates directories for the files attached to the emails, also plaxes the files into their appropriate dir
def make_file_dir(filename, received_files_bool, file_list):
    #checks to see wether the files were received or given by the journalist
    n = 'given'
    if received_files_bool: n = 'recieved'

    #making a directory for the files recieved/given by the journalists
    path = make_dir(filename+'_'+n, 'email_files/'+n) #name of the dir is "(the name of the email exchange)_(wether it was recieved or given by the jorunalist)"

    #downloading files that were received/given
    for url in file_list:
        wget.download(url, out=path)
        print('\n')
    
    return

"""
MAIN FUNCTION USED T0 CREATE THE DICTIONARY WITH ALL THE DATA AS WELL AS DOWNLOAD THE FILES
"""
def downloading_exchanges(URL, ex):
    #requesting the http contents of a given URL 
    page = request_content(URL)

    ### email exchanges
    #list of emails sent by the government agency
    black_bd_list = make_dateBodySender_list(page, 'collapsable communication textbox')

    #list of emails sent by the journalist
    blue_bd_list = make_dateBodySender_list(page, 'blue collapsable communication textbox')

    #list of emails sent by the journalist that are collapsed by default in the website
    blue_collapsed_bd_list = make_dateBodySender_list(page, 'blue collapsable communication textbox collapsed')

    #list of emails sent by the government agency that are collapsed by default in the website
    black_collapsed_bd_list = make_dateBodySender_list(page, 'collapsable communication textbox collapsed')

    #compiling and sorting email lists
    master_comm_list = compile_sort_lists(blue_bd_list, blue_collapsed_bd_list, black_bd_list, black_collapsed_bd_list)
    
    #assmbling the dictionary that will contain information about the email exchange
    emails = []
    for t in master_comm_list:
        dic = {
            'sender': t[2],
            'date': t[0],
            'body': t[1],
        }
        emails.append(dic)
    ex['Emails'] = emails

    ### file exchanges
    #list of files the journalist received
    files_received_list = get_files_list(page, 'collapsable communication textbox')
    files_received_list.extend(get_files_list(page, 'collapsable communication textbox collapsed'))
    
    #list of files the journalist gave
    files_given_list = get_files_list(page, 'blue collapsable communication textbox')
    files_given_list.extend(get_files_list(page, 'blue collapsable communication textbox collapsed'))

    #downloading the files recieved by the journalists
    make_file_dir(ex['Slug'], True, files_received_list)

    #downloading the files given by the journalists
    make_file_dir(ex['Slug'], False, files_given_list)

    return

"""
THE CODE BELOW CALLS THE FUNCTIONS ABOVE TO OUTPUT:
    1) A DIRECTORY WITH THE FILES THAT WERE ATTACHED TO THE EMAILS
    2) A JSON FILE THAT CONTAINS THE DICTIONARY THAT HAS THE EMAIL EXCHANGES DATA
"""
#making a directory to store all the files attached on the emails
make_dir('email_files')

#making a directory to store all the files attached on the emails sent by the govrnment agency
make_dir('recieved', 'email_files')

#making a directory to store all the files attached on the emails sent by the journalist
make_dir('given', 'email_files')

#Creating the dictionary that will hold all of the data
exchanges = {}

#opening the csv file
with open('foia_requests_test.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)

    next(reader) #skipping the first row of the csv file
    
    iter = 0
    #looping through the csv file rows and downloading the email exchanges in the urls found in the thrid column of the csv file
    for line in reader:
        print(iter) #printing a count of the txt files being generated so the terminal shows how far the program has progessed
        iter += 1

        URL = line[3]
        #Creating the dictionary that will hold metadata about the email exchange
        ex = {}
        ex['Status'] = line[2] 
        ex['Agency'] = line[8]
        ex['User'] = line[0]
        ex['Slug'] = line[-1]

        downloading_exchanges(URL, ex)

        exchanges[ex['Slug']] = ex

#converting the exchanges dictionary into json and saving it all as a json file
exchanges_json = json.dump(exchanges, open('email_exchanges', 'w'))
