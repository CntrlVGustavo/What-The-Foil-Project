import json
import csv
import sys
import random
import numpy as np
from numpy.core.getlimits import _register_known_types
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
#from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import StratifiedKFold
#from sklearn.pipeline import Pipeline
#from sklearn.model_selection import GridSearchCV
#from sklearn import metrics
#from sklearn.feature_extraction import DictVectorizer
import fightin_words as fw
import sklearn.feature_extraction.text as sk_text

def get_from_json():

    #Aquiring the data from the json file
    data = {}
    with open('email_exchanges', 'r') as f:
        data = json.load(f)
    return data

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

def useCsvToGetData(csv_file, data):
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

    lst = []
    with open(csv_file, 'r') as file:
        #making a readable object
        reader = csv.reader(file)
        next(reader) #skipping the header

        for line in reader:
            lst.append(data[line[-1]]['Emails'][0]['body'])

    return lst

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

def top_feature_extraction(c_vect, clf, n):
    feature_names = c_vect.get_feature_names()
    co_with_fns = sorted(zip(clf.coef_[0], feature_names))
    top_features = zip(co_with_fns[:n], co_with_fns[:-(n + 1):-1])

    top_rejected = []
    top_completed = []
    it = 1
    for (rej_co, rej_name), (com_co, com_name) in top_features:
        top_rejected.append([it, rej_co, rej_name])
        top_completed.append([it, com_co, com_name])
        it += 1
        #print('Rejected: %s ~ %s  |   Completed: %s ~ %s' % (rej_co,rej_name,com_co,com_name))
    
    print_features('REJECTED FEATURES', top_rejected, 50)
    print_features('COMPLETED FEATURES', top_completed, 50)

    return top_rejected, top_completed

def print_features(title,lst, n):
    print('\n%s' % (title))
    print ("{:<8} {:<20} {:<10}".format('Top#','Coefficient','Feature'))
    for v in lst:
        if n == 0: break
        top, coef, feat = v
        print ("{:<8} {:<20} {:<10}".format( top, coef, feat))
        n += -1

    return

def trainBinarySvm(exs_class0, exs_class1):
    examples,labels = makeDandL_lsts(exs_class1, exs_class0)

    examples = np.array(examples)
    labels = np.array(labels)

    skf = StratifiedKFold(n_splits=2)
    skf.get_n_splits(examples, labels)

    for train_index, test_index in skf.split(examples, labels):
        ex_train, ex_test = examples[train_index], examples[test_index]
        l_train, l_test = labels[train_index], labels[test_index]

    #Making count vectors
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(ex_train)
    
    #Making tf-idf vectors
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    #Making the classifier
    svm_clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None).fit(X_train_tfidf, l_train)
    
    #Finding top features
    top_rej, top_com = top_feature_extraction(count_vect,svm_clf, 20)
   
    #Doing predictions
    X_test_counts = count_vect.transform(ex_test)
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)
    svm_predicted = svm_clf.predict(X_test_tfidf)

    svm_mean = np.mean(svm_predicted == l_test)
    return svm_mean, top_rej, top_com

def iterTestBinaryClf(clf, iter, data):
    total = 0
    rej_dic = {}
    com_dic = {}

    for i in range(iter):
        completed_examples = useCsvToGetData('completed_foia_requests.csv', data)
        rejected_examples = useCsvToGetData('rejected_foia_requests.csv', data)
        curr_mean, top_rej, top_com = clf(rejected_examples,completed_examples)
        print(i)
        print(curr_mean) 
        print('\n')

        #co_with_fns = sorted(zip(clf.coef_[0], feature_names))
        #top_features = zip(co_with_fns[:n], co_with_fns[:-(n + 1):-1])
        for [i, coef, name] in top_rej:
            temp = rej_dic.setdefault(name,0)
            rej_dic[name] = temp + coef

        for [i, coef, name] in top_com:
            temp = com_dic.setdefault(name,0)
            com_dic[name] = temp + coef

        total += curr_mean

    return total, rej_dic, com_dic

def iterFightingWords(csv_file, data, cv_bool, iter_n):
    examples = useCsvToGetData(csv_file, data)
    ex_length = len(examples)

    z_score_dic = {}
    for n in range(iter_n):
        random.shuffle(examples)
        ex_10percent = examples[:(ex_length//10)]
        ex_90percent = examples[(ex_length//10):]

        if cv_bool: cv = sk_text.CountVectorizer(max_features=15000)
        else: cv = None

        z_score_lst = fw.bayes_compare_language(ex_10percent,ex_90percent,1,.01,cv)
        for (name, coef) in z_score_lst:
            temp = z_score_dic.setdefault(name,0)
            z_score_dic[name] = temp + coef
        print(n)
        print("\n")


    return z_score_dic

def avgCoef(ex_dic, title, iter, n_of_f, reverse_bool):
    for key in ex_dic.keys(): ex_dic[key] = ex_dic[key] / iter

    ex_co_with_fns = sorted(zip(ex_dic.values(), ex_dic.keys()))

    top_ex = []
    it = 1
    for (ex_co, ex_name) in ex_co_with_fns:
            top_ex.append([it, ex_co, ex_name])
            it += 1

    if reverse_bool: top_ex.reverse()
    print_features(title, top_ex, n_of_f)
    return

def main():
    d = get_from_json()

    fw_iter = 100
    reverse_bool = True
    fighting_words_com = iterFightingWords('completed_foia_requests.csv', d, True, fw_iter)
    avgCoef(fighting_words_com, "FIGHTING WORDS COMPLETED", fw_iter, 10, reverse_bool)

    fighting_words_rej = iterFightingWords('rejected_foia_requests.csv', d, True, fw_iter)
    avgCoef(fighting_words_rej,"FIGHTING WORDS REJECTED", fw_iter, 10, reverse_bool)

    binary_clf = trainBinarySvm
    iter = 100
    total_mean, rej_dic, com_dic = iterTestBinaryClf(binary_clf, iter, d)

    print('Av Precision:')
    print(total_mean / iter)

    #finding the average coeff
    for key in rej_dic.keys(): rej_dic[key] = rej_dic[key] / iter
    for key in com_dic.keys(): com_dic[key] = com_dic[key] / iter

    rej_co_with_fns = sorted(zip(rej_dic.values(), rej_dic.keys()))
    com_co_with_fns = sorted(zip(com_dic.values(), com_dic.keys()))

    top_rejected = []
    it = 1
    for (rej_co, rej_name) in rej_co_with_fns:
            top_rejected.append([it, rej_co, rej_name])
            it += 1

    top_completed = []
    it = len(com_co_with_fns)
    for (com_co, com_name) in com_co_with_fns:
            top_completed.append([it, com_co, com_name])   
            it -= 1  
    top_completed.reverse()

    print_features('REJECTED FEATURES', top_rejected, 50)
    print_features('COMPLETED FEATURES',top_completed, 50)
    return

if __name__ == "__main__":
    main()