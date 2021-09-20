import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

### HELPER FUNCTIONS
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
### HELPER FUNCTIONS


### MAIN FUNCTIONS
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

#given the http contents of a page and an email class, returns a list of file links that were attached to the emails of email_class
def make_files_list(page_contents, email_class):
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

#given the http contents of a page and an email class, returns a list of tuples of the form (date the email was sent, email's body of text)
def make_dateBody_list(page_contents, email_class):
    #list of some type of email inside the previously aquired class 
    e_list = page_contents.find_all('section', class_= email_class)


    e_body_list = get_email_body_list(e_list)
    e_date_list = get_email_date_list(e_list)

    dateBody_list = []
    for (d,b) in zip(e_date_list, e_body_list): dateBody_list.append((d,b))

    return dateBody_list

#compiles four lists of email date/body tuples into a single email date/body tuple list that is ordered by date
def compile_sort_lists(list1,list2,list3, list4):
    #compiling lists
    list1.extend(list2)
    list1.extend(list3)
    list1.extend(list4)

    #sorting emails by date
    list1.sort(key = lambda l: datetime.strptime(l[0], '%m/%d/%Y'))

    return list1
### MAIN FUNCTIONS