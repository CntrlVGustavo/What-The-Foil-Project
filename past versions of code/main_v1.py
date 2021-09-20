import muckrock_data_processing as dp
import csv
import shutil

def downloading_exchanges(URL, filename):
    #requesting the http contents of a given URL 
    page = dp.request_content(URL)

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
        for b in master_comm_list: f.write(b[1])

    return


#opening the csv file
with open('foia_requests_test.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)

    next(reader) #skipping the first row of the csv file
    
    iter = 0
    for line in reader:
        print(iter)
        iter += 1

        URL = line[3]
        filename = line[1]
        downloading_exchanges(URL, filename)
        shutil.move(filename, 'email_exchanges')