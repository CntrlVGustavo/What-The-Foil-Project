from numpy.core.numeric import True_
import muckrock_data_processing as dp
import csv
import wget
import os
import shutil

### HELPER FUNCTIONS
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
### HELPER FUNCTIONS


### MAIN FUNCTIONS
def downloading_exchanges(URL, filename):
    #requesting the http contents of a given URL 
    page = dp.request_content(URL)

    ### email exchanges
    #list of emails sent by the government agency
    black_bd_list = dp.make_dateBody_list(page, 'collapsable communication textbox')

    #list of emails sent by the journalist
    blue_bd_list = dp.make_dateBody_list(page, 'blue collapsable communication textbox')

    #list of emails sent by the journalist that are collapsed by default in the website
    blue_collapsed_bd_list = dp.make_dateBody_list(page, 'blue collapsable communication textbox collapsed')

    #list of emails sent by the government agency that are collapsed by default in the website
    black_collapsed_bd_list = dp.make_dateBody_list(page, 'collapsable communication textbox collapsed')

    #compiling and sorting email lists
    master_comm_list = dp.compile_sort_lists(blue_bd_list, blue_collapsed_bd_list, black_bd_list, black_collapsed_bd_list)
    
    #creating a text file with the email exchanges
    with open(filename, 'w') as f:
        for i in range(len(master_comm_list)):
            f.write('\n')
            f.write('[{['+str(i)+']}]') #to make it easier to index a particular email the txt file
            f.write('\n')
            f.write(master_comm_list[i][1])
        shutil.move(filename, 'email_exchanges') #moving the text file with the email exchanges into the appropiate folder

    ### file exchanges
    #list of files the journalist received
    files_received_list = dp.make_files_list(page, 'collapsable communication textbox')
    files_received_list.extend(dp.make_files_list(page, 'collapsable communication textbox collapsed'))
    
    #list of files the journalist gave
    files_given_list = dp.make_files_list(page, 'blue collapsable communication textbox')
    files_given_list.extend(dp.make_files_list(page, 'blue collapsable communication textbox collapsed'))

    #downloading the files recieved by the journalists
    make_file_dir(filename, True, files_received_list)

    #downloading the files given by the journalists
    make_file_dir(filename, False, files_given_list)

    return
### MAIN FUNCTIONS

#making a directory to store all the text files containing the email exchanges
make_dir('email_exchanges')

#making a directory to store all the files attached on the emails
make_dir('email_files')

#making a directory to store all the files attached on the emails sent by the govrnment agency
make_dir('recieved', 'email_files')

#making a directory to store all the files attached on the emails sent by the journalist
make_dir('given', 'email_files')

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
        filename = line[1]

        downloading_exchanges(URL, filename)