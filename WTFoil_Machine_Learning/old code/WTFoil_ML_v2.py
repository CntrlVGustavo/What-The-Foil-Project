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
def train_data_split(csv_size, csv_file, test_num):
    
    random_i_list = []
    while len(random_i_list) < test_num:
        random_i = random.randrange(csv_size)
        if random_i not in random_i_list: random_i_list.append(random_i)
    
    return

def make_data(csv_file, data_size, csv_size, spe_test):
    #making a list to hold the data from the csv file
    data_lst = []

    with open(csv_file, 'r') as file:
        #making a readable object
        reader = csv.reader(file)
        next(reader) #skipping the header
        reader = list(reader) #so I'm able to index reader to get specific rows

        random_i_list = []
        while len(random_i_list) < data_size:
            random_i = random.randrange(csv_size)
            if random_i not in random_i_list: random_i_list.append(random_i)
        
        if spe_test: random_i_list = spe_test

        for i in random_i_list:
            line = reader[i]
            data_lst.append(data[line[-1]]['Emails'][0]['body'])
    
    return data_lst, random_i_list

def makeDandL_lsts(comp_lst, rej_lst):
    #creating a list of labels 
    label_lst = [1] * len(comp_lst)
    label_lst.extend([0] * len(rej_lst))

    #joining the completed and rejected email lists into one
    data_lst = comp_lst
    data_lst.extend(rej_lst)

    #shuffling data_lst and label_lst in the same way
    temp = list(zip(data_lst, label_lst))
    random.shuffle(temp)
    data_lst, label_lst = zip(*temp)
    
    return data_lst, label_lst

#this is the list which will contain all the first email bodies of foia requests that were completed 
train_completed, train_his_c = make_data('train_completed_foia_requests.csv', 454, 714, False)

#this is the list which will contain all the first email bodies of foia requests that were rejected
train_rejected, train_his_r = make_data('train_rejected_foia_requests.csv', 454, 454, False)

#this is the list which will contain all the first email bodies of foia requests that were completed 
test_completed, test_his_c = make_data('test_completed_foia_requests.csv', 200, 713, False)

#this is the list which will contain all the first email bodies of foia requests that were rejected
test_rejected, test_his_r = make_data('test_rejected_foia_requests.csv', 200, 446, False)

#creating a list of examples and lables for training
training_e, training_l = makeDandL_lsts(train_completed, train_rejected)

#creating a list of examples and lables for testing
test_e, test_l = makeDandL_lsts(test_completed, test_rejected)

#printing testing data history
print("COMPLETED TRAINING HISTORY")
print(train_his_c)
print("REJECTED TRAINING HISTORY")
print(train_his_r)
### Doing Machine Learning

#Naive Bayes Classifier
nb_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),])

nb_clf.fit(training_e, training_l)
nb_predicted = nb_clf.predict(test_e)

print("PERFORMANCE OF NAIVE BAYES")
print(metrics.classification_report(test_l, nb_predicted, target_names=["Rejected", "Completed"]))
print("~"*55)

#Support Vector Machine Classifier
svm_clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None))])

svm_clf.fit(training_e, training_l)
svm_predicted = svm_clf.predict(test_e)

print("PERFORMANCE OF SUPPORT VECTOR MACHINE")
print(metrics.classification_report(test_l, svm_predicted, target_names=["Rejected", "Completed"]))

#Doing Parameter search for the SVM
parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tfidf__use_idf': (True, False), 'clf__alpha': (1e-2, 1e-3)}
gs_clf = GridSearchCV(svm_clf, parameters, cv=5, n_jobs=-1)

#Using the SVM with parameter search
gs_clf = gs_clf.fit(training_e, training_l)
gs_predicted = gs_clf.predict(test_e)

print("PERFORMANCE OF GRID SEARCH SUPPORT VECTOR MACHINE")
print(metrics.classification_report(test_l, gs_predicted, target_names=["Rejected", "Completed"]))
print("Printing the Best Parameters")
for param_name in sorted(parameters.keys()):
    print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))


#preliminary testing
def nv():
    #this is the list which will contain all the first email bodies of foia requests that were completed 
    train_completed, train_his_c = make_data('train_completed_foia_requests.csv', 454, 714, False)

    #this is the list which will contain all the first email bodies of foia requests that were rejected
    train_rejected, train_his_r = make_data('train_rejected_foia_requests.csv', 454, 454, False)

    #this is the list which will contain all the first email bodies of foia requests that were completed 
    test_completed, test_his_c = make_data('test_completed_foia_requests.csv', 200, 713, False)

    #this is the list which will contain all the first email bodies of foia requests that were rejected
    test_rejected, test_his_r = make_data('test_rejected_foia_requests.csv', 200, 446, False)

    #creating a list of examples and lables for training
    training_e, training_l = makeDandL_lsts(train_completed, train_rejected)

    #creating a list of examples and lables for testing
    test_e, test_l = makeDandL_lsts(test_completed, test_rejected)

    #printing testing data history
    """
    print("COMPLETED TRAINING HISTORY")
    print(train_his_c)
    print("REJECTED TRAINING HISTORY")
    print(train_his_r)
    """
    ### Doing Machine Learning

    #Naive Bayes Classifier
    nb_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', MultinomialNB()),])

    nb_clf.fit(training_e, training_l)
    nb_predicted = nb_clf.predict(test_e)

    return np.mean(nb_predicted == test_l)

total = 0
iter = 10
for i in range(iter):
    curr = nv()
    print(curr)
    print('\n')
    total += curr

print(total / iter)

"""
def nv_t(data):

    completed_examples = useCsvToGetData('completed_foia_requests.csv', data)
    rejected_examples = useCsvToGetData('rejected_foia_requests.csv', data)

    examples,labels = makeDandL_lsts(completed_examples, rejected_examples)

    examples = np.array(examples)
    labels = np.array(labels)

    skf = StratifiedKFold(n_splits=2)
    skf.get_n_splits(examples, labels)

    for train_index, test_index in skf.split(examples, labels):
        ex_train, ex_test = examples[train_index], examples[test_index]
        l_train, l_test = labels[train_index], labels[test_index]

    ### Doing Machine Learning
    #Naive Bayes Classifier
    nb_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', MultinomialNB()),])

    nb_clf.fit(ex_train, l_train)
    nb_predicted = nb_clf.predict(ex_test)


    return np.mean(nb_predicted == l_test)
"""