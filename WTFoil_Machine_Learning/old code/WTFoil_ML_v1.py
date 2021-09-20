import json
import csv
import sys
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn import metrics

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

#Aquiring the data from the json file
data = {}
with open('email_exchanges', 'r') as f:
    data = json.load(f)

"""
data is a dictionary
It's keys are the slugs of the links that contain email exchanges.

The values to those keys are themselves dictionaries.
The keys to those dictionaries are the following: 'Status', 'Agency', 'User', 'Slug', 'Emails'.

The value to the key 'Emails' is a list of dictionaries, each of which contains information about a particular email.
The list is ordered in chronological order (for instance the dict in index 0 is the first email sent, the dict in index 1 is the second, and so on).

The keys for the dictionaries that contain data of a particular email are the following: 'sender', 'date', 'body'.
The values to those keys are strings.

Example: this code prints the body of the first email of the email exchange recorded in the link which has the slug '100-18762-harry-hay-60143'
print(data['100-18762-harry-hay-60143']['Emails'][0]['body'])
"""

#this is the list which will contain all the first email bodies of foia requests that were completed 
train_completed = []

#this is the list which will contain all the first email bodies of foia requests that were rejected
train_rejected = []

#this is the list which will contain all the first email bodies of foia requests that were completed 
test_completed = []

#this is the list which will contain all the first email bodies of foia requests that were rejected
test_rejected = []

### Generating the training and testing data
#making a list containing 200 of the first email bodies of foia requests that were rejected from the training data
with open('train_rejected_foia_requests.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)
    next(reader) #skipping the header
    reader = list(reader) #so I'm able to index reader to get specific rows

    random_i_list = []
    while len(random_i_list) < 200:
        random_i = random.randrange(446)
        if random_i not in random_i_list: random_i_list.append(random_i)
        
    for i in random_i_list:
        line = reader[i]
        train_rejected.append(data[line[-1]]['Emails'][0]['body'])

#making a list containing 200 of the first email bodies of foia requests that were completed from the training data
with open('train_completed_foia_requests.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)
    next(reader) #skipping the header
    reader = list(reader) #so I'm able to index reader to get specific rows

    random_i_list = []
    while len(random_i_list) < 200:
        random_i = random.randrange(713)
        if random_i not in random_i_list: random_i_list.append(random_i)
        
    for i in random_i_list:
        line = reader[i]
        train_completed.append(data[line[-1]]['Emails'][0]['body'])


### Generating the testing data
#making a list containing 50 of the first email bodies of foia requests that were rejected from the testing data
with open('test_rejected_foia_requests.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)
    next(reader) #skipping the header
    reader = list(reader) #so I'm able to index reader to get specific rows

    random_i_list = []
    while len(random_i_list) < 50:
        random_i = random.randrange(454)
        if random_i not in random_i_list: random_i_list.append(random_i)
        
    for i in random_i_list:
        line = reader[i]
        test_rejected.append(data[line[-1]]['Emails'][0]['body'])

#making a list containing 50 of the first email bodies of foia requests that were completed from the testing data
with open('test_completed_foia_requests.csv', 'r') as file:
    #making a readable object
    reader = csv.reader(file)
    next(reader) #skipping the header
    reader = list(reader) #so I'm able to index reader to get specific rows

    random_i_list = []
    while len(random_i_list) < 50:
        random_i = random.randrange(714)
        if random_i not in random_i_list: random_i_list.append(random_i)
        
    for i in random_i_list:
        line = reader[i]
        test_completed.append(data[line[-1]]['Emails'][0]['body'])

#creating a list of labels for the examples in the training data 
training_l = [1] * len(train_completed)
training_l.extend([0] * len(train_rejected))   

#mixing the completed and rejected email lists into one to create the training data list
training_d = train_completed
training_d.extend(train_rejected)

#shuffling training_d and training_l in the same way
temp = list(zip(training_d, training_l))
random.shuffle(temp)
training_d, training_l = zip(*temp)

#creating a list of labels for the examples in the testing data
test_l = [1] * len(test_completed)
test_l.extend([0] * len(test_rejected))   

#mixing the completed and rejected email lists into one to create the testing data list
test_d = test_completed
test_d.extend(test_rejected)

#shuffling test_d and test_l in the same way
temp = list(zip(test_d, test_l))
random.shuffle(temp)
test_d, test_l = zip(*temp)

### Doing Machine Learning

#Naive Bayes Classifier
nb_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),])

nb_clf.fit(training_d, training_l)
nb_predicted = nb_clf.predict(test_d)

print("PERFORMANCE OF NAIVE BAYES")
print(metrics.classification_report(test_l, nb_predicted, target_names=["Rejected", "Completed"]))
print("~"*55)

#Support Vector Machine Classifier
svm_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None))])

svm_clf.fit(training_d, training_l)
svm_predicted = svm_clf.predict(test_d)

print("PERFORMANCE OF SUPPORT VECTOR MACHINE")
print(metrics.classification_report(test_l, svm_predicted, target_names=["Rejected", "Completed"]))

#Doing Parameter search for the SVM
parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tfidf__use_idf': (True, False), 'clf__alpha': (1e-2, 1e-3)}
gs_clf = GridSearchCV(svm_clf, parameters, cv=5, n_jobs=-1)

#Using the SVM with parameter search
gs_clf = gs_clf.fit(training_d, training_l)
gs_predicted = gs_clf.predict(test_d)

print("PERFORMANCE OF GRID SEARCH SUPPORT VECTOR MACHINE")
print(metrics.classification_report(test_l, gs_predicted, target_names=["Rejected", "Completed"]))
print("Printing the Best Parameters")
for param_name in sorted(parameters.keys()):
    print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))