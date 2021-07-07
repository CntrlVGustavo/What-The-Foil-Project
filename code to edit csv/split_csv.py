import csv
import sys

### this is some quick and dirty code to deal with huge csv files
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
### without this code, we can't itrate the reader object because of how big it is

header = []
#all types of rows
comp_rows = [] #Completed
rej_rows = [] #Rejected
with_rows = [] #Withdrawn
awaitAck_rows = [] #Awaiting Acknowledgement
inLit_rows = [] #In Litigation
fixReq_rows = [] #Fix Required
proc_rows = [] #Processing
payReq_rows = [] #Payment Required
awaitRes_rows = [] #Awaiting Response
awaitApp_rows = [] #Awaiting Appeal
partComp_rows = [] #Partially Completed
noResDoc_rows = [] #No Responsive Documents

with open('foia_requests.csv', 'r') as f:
    #create the csv reader
    reader = csv.reader(f)
    
    #recording the header
    header = next(reader)
    
    #recording all of the rows of the csv file
    for line in reader:
        #recording rows that are marked "Completed"
        if line[2] == 'Completed': comp_rows.append(line)
        #recording rows that are marked "Rejected"
        elif line[2] == 'Rejected': rej_rows.append(line)
        #recording rows that are marked "Withdrawn"
        elif line[2] == 'Withdrawn': with_rows.append(line)
        #recording rows that are marked "Awaiting Acknowledgement"
        elif line[2] == 'Awaiting Acknowledgement': awaitAck_rows.append(line)
        #recording rows that are marked "In Litigation"
        elif line[2] == 'In Litigation': inLit_rows.append(line)
        #recording rows that are marked "Fix Required"
        elif line[2] == 'Fix Required': fixReq_rows.append(line)
        #recording rows that are marked "Processing"
        elif line[2] == 'Processing': proc_rows.append(line)
        #recording rows that are marked "Payment Required"
        elif line[2] == 'Payment Required': payReq_rows.append(line)
        #recording rows that are marked "Awaiting Response"
        elif line[2] == 'Awaiting Response': awaitRes_rows.append(line)
        #recording rows that are marked "Awaiting Appeal"
        elif line[2] == 'Awaiting Appeal': awaitApp_rows.append(line)
        #recording rows that are marked "Partially Completed"
        elif line[2] == 'Partially Completed': partComp_rows.append(line)
        #recording rows that are marked "No Responsive Documents"
        elif line[2] == 'No Responsive Documents': noResDoc_rows.append(line)


#function to create a csv file with only the "x_rows" rows
def csv_file_type(name, x_rows):
    #Creating a csv file with only the "Rejected" rows
    print(name)
    with open(name+'_foia_requests.csv', 'w') as f:
        # create the csv writer
        writer = csv.writer(f)

        # editing the header
        writer.writerow(header)

        #editing the csv rows
        for r in x_rows: writer.writerow(r)

var_list = [comp_rows, rej_rows, with_rows, awaitAck_rows, inLit_rows, fixReq_rows, proc_rows, payReq_rows, awaitRes_rows, awaitApp_rows, partComp_rows, noResDoc_rows]
name_list =['completed', 'rejected', 'withdrawn', 'awaiting_acknowledgement', 'in_litigation', 'fix_required', 'processing', 'payment_required', 
'awaiting_response', 'awaiting_appeal', 'partially_completed', 'no_responsive_documents']

#Creating a csv files with only the "x" rows
for i in range(len(name_list)):
    csv_file_type(name_list[i], var_list[i])
