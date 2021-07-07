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
rows = []
with open('foia_requests.csv', 'r') as f:
    # create the csv reader
    reader = csv.reader(f)
    
    header = next(reader)
    header.append('Slug')

    #recording all of the rows of the csv file + their respective slugs
    for line in reader:
        line.append(line[3].split('/')[-2])
        rows.append(line)

with open('foia_requests.csv', 'w') as f:
    # create the csv writer
    writer = csv.writer(f)

    # editing the header
    writer.writerow(header)

    #editing the csv rows
    iter = 0
    for r in rows:
        print(iter)
        iter += 1

        writer.writerow(r)