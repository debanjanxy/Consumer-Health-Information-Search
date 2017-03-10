#!/usr/bin/python

#--------------------------------------------------------------------------------------
#-----------------------------------INSTRUCTOR-----------------------------------------
#                               PROF. KAMAL SARKAR
#                   DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
#                              JADAVPUR UNIVERSITY
#--------------------------------------------------------------------------------------
#-------------------------------------AUTHORS------------------------------------------
#NAME : MAMTA KUMARI                                            NAME : DEBANJAN DAS
#ROLL : 001310501009                                            ROLL : 001310501011

#NAME : INDRA BANERJEE                                          NAME : PRASENJIT BISWAS
#ROLL : 001310501001                                            ROLL : 001310501015
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
#PACKAGES & CONSTANTS
#--------------------------------------------------------------------------------------
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
import nltk
from nltk.corpus import stopwords
import xlrd
import os.path
import re
import wikipedia
from xlwt import Workbook
import json
import math
import unicodedata
from scipy import stats
import numpy as np
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from nltk.corpus import sentiwordnet as swn
INT_MAX = 32767
#--------------------------------------------------------------------------------------


#**************************************************************************************
#USER DEFINED FUNCTIONS
#**************************************************************************************


#--------------------------------------------------------------------------------------
#FINDS IF A WHOLE WORD IS PRESENT IN A SENTENCE OR NOT
#--------------------------------------------------------------------------------------
def findWord(w,s):
    s_l = s.split()
    for w1 in s_l:
        if w1==w:
            return True
    return False
#--------------------------------------------------------------------------------------
#computeTF is used to compute term frequency(TF)
#--------------------------------------------------------------------------------------
def computeTF(word,sentence):
    sentence = re.sub('[!@#$.,()\\%?0123456789":;-]','',sentence)
    word_list = sentence.split()
    count = word_list.count(word)
    n = len(word_list)
    val = count/float(n)
    return val
#--------------------------------------------------------------------------------------
#COMPUTES IDF OF A WORD IN A SET OF SENTENCES
#--------------------------------------------------------------------------------------
def computeIDF(num_rows,word,total_queries):
    count = 0
    for i in range(num_rows):
        word.encode('ascii','ignore')
        val = findWord(word,total_queries[i])
        if val:
            count = count+1
    if (count==0): 
        return INT_MAX
    else:
        return math.log(num_rows/float(count)) 
#--------------------------------------------------------------------------------------        
#Computes the modulus of a vector
#--------------------------------------------------------------------------------------
def modulus(vect):
    c = 0
    for x in vect:
        c += float(math.pow(vect[x],2))
    return math.sqrt(c)
 
#--------------------------------------------------------------------------------------        
#Computes the cos0 between two vectors
#--------------------------------------------------------------------------------------
def cosTheta(mqv,uqv,val):
    m1 = modulus(mqv)
    m2 = modulus(uqv)
    try:
        return val/float((m1*m2))
    except:
        return 0
#--------------------------------------------------------------------------------------
#Computes dot product between two vectors represented as dictionaries
#--------------------------------------------------------------------------------------
def dotProduct(mqv,uqv):
    val = 0;
    for w in mqv:
        val = val+float(mqv[w]*uqv[w])
    return val
#--------------------------------------------------------------------------------------
#CLEANS A STRING
#--------------------------------------------------------------------------------------
def cleanString(string):
    string = string.lower()
    string = re.sub('[-!@#$.,()\'%?0123456789"/{}:;]','',string)
    lst = string.split()
    lst = [word for word in lst if word not in stopwords.words('english')]
    final_word_list = []
    for word in lst:
        a = word.encode('ascii','ignore').decode('ascii')
        final_word_list.append(a)
    string = ' '.join(final_word_list)
    return string
#--------------------------------------------------------------------------------------
#WORDS OF mqn THAT ARE SUBSTRING OF w ARE STORED IN nn
#--------------------------------------------------------------------------------------
def subString(mqn,w):
    nn = list()
    for x in mqn:
        if x in w:
            nn.append(x)
    return nn
#--------------------------------------------------------------------------------------
#WORDS OF mqw THAT ARE PRESENT IN q ARE STORED IN pvc
#--------------------------------------------------------------------------------------    
def isPresent(mqw,q):
    pvc = []
    for w in mqw:
        p = findWord(w,q)
        if p:
            pvc.append(w)
    return pvc    
#--------------------------------------------------------------------------------------
#CALCULATES THE NUMBER OF POSITIVE, NEGATIVE & NEUTRAL WORDS IN A SENTENCE
#--------------------------------------------------------------------------------------
def pos_neg_value(fobj,s,i):
    words = s.split()
    pw = 0
    nw = 0
    ntw = 0
    for w in words:
        a = list(swn.senti_synsets(w))
        try:
            pos = a[0].pos_score()
            neg = a[0].neg_score()
        except:
            pos = 0.0
            neg = 0.0
        if pos>neg:
            pw = pw+1
        elif neg>pos:
            nw = nw+1
        else:
            ntw = ntw+1
    
    print "Positive words = %d\nNegtive words = %d\nNeutral words = %d\n"%(pw,nw,ntw) 
    print "----------------------------------"
    fobj.write(str(pw)+' ')
    fobj.write(str(nw)+' ')
    fobj.write(str(ntw)+' ')   

#--------------------------------------------------------------------------------------
#FILTER OUT IMPORTANT WORDS FROM A LIST OF RAW WORDS
#--------------------------------------------------------------------------------------
def cleanWords(total_queries):
    words = list()
    for i in range(len(total_queries)):
        words = words + total_queries[i].split()
    words = [word.lower() for word in words]
    temp_str = ' '.join(words)
    #temp_str = re.sub('[-!@#$.,()\'%?0{}123456789/":;]','',temp_str)
    temp_str = cleanString(temp_str)
    final_words = temp_str.split() 
    seen = set()
    result = list()
    for item in final_words:
        if item not in seen:
            seen.add(item)
            result.append(item)

    filtered_result = [word for word in final_words if word not in stopwords.words('english')]
    filtered_result = list(set(filtered_result))

    final_word_list = []
    for word in filtered_result:
        a = word.encode('ascii','ignore').decode('ascii')
        final_word_list.append(a)
    return final_word_list
#--------------------------------------------------------------------------------------


#**************************************************************************************
#**************************************************************************************


#MAIN PROGRAM


#--------------------------------------------------------------------------------------
#INPUT & INITIALIZATION
#--------------------------------------------------------------------------------------
inp0 = raw_input('Enter the query:')
#inp = ''
filename = inp0 + '.xlsx'
if inp0=='ecig':
    inp = 'ecigarettes'
elif inp0=='skincancer':
    inp = 'does sun exposure cause skin cancer'
elif inp0=='hrt':
    inp = 'women should take hrt post menopause'
elif inp0=='vitaminC':
    inp = 'vitamin C common cold'
elif inp0=='mmr_vaccine':
    inp = 'mmr vaccine lead to autism'
wb = xlrd.open_workbook(filename)
sh = wb.sheet_by_index(0)
total_queries = sh.col_values(0)
labels = sh.col_values(1)
main_query = re.sub('[_]',' ',inp)
main_query = cleanString(main_query)
main_query_words = main_query.split()
stemmer = PorterStemmer()
#--------------------------------------------------------------------------------------
#FETCH CLEAN WORDS FROM THE INPUT EXCEL DATASHEET
#--------------------------------------------------------------------------------------
words = list()
for i in range(len(total_queries)):
    words = words + total_queries[i].split()
words = [word.lower() for word in words]
temp_str = ' '.join(words)
temp_str = re.sub('[-!@#$.,()\'%?0{}123456789/":;]','',temp_str)
final_words = temp_str.split() 
seen = set()
result = list()
for item in final_words:
    if item not in seen:
        seen.add(item)
        result.append(item)

filtered_result = [word for word in final_words if word not in stopwords.words('english')]
filtered_result = list(set(filtered_result))

final_word_list = []
for word in filtered_result:
    a = word.encode('ascii','ignore').decode('ascii')
    final_word_list.append(a)
#print final_word_list
#--------------------------------------------------------------------------------------
#LEVEL 1 FEATURE 1 CALCULATION
#--------------------------------------------------------------------------------------
wb1 = Workbook()
sh1 = wb1.add_sheet('Sheet1')
sh1.col(0).width = 17000
for i in range(len(total_queries)):
    q1 = total_queries[i]
    q = cleanString(q1)
    q_words1 = q.split()
    common_words1 = set(main_query_words).intersection(q_words1)
    common_words1 = list(set(common_words1))
    similarity1 = (2*len(common_words1))/float(len(q_words1)+len(main_query_words))
    sh1.write(i,0,q1)
    sh1.write(i,1,similarity1)
    wb1.save('f11.xls')
wb1.save('f11.xls')
#--------------------------------------------------------------------------------------
#LEVEL 1 FEATURE 2 CALCULATION
#--------------------------------------------------------------------------------------
wb2 = Workbook()
sh2 = wb2.add_sheet('Sheet1')
sh2.col(0).width = 17000
for w in main_query_words:
    w = stemmer.stem(w)
for i in range(len(total_queries)):
    q2 = total_queries[i]
    q = cleanString(q2)
    q_words2 = q.split()
    for w1 in q_words2:
        w1 = stemmer.stem(w1)
    common2 = set(main_query_words).intersection(q_words2)
    common2 = list(set(common2))
    similarity2 = (2*len(common2))/float((len(main_query_words)+len(q_words2)))    
    sh2.write(i,0,q)
    sh2.write(i,1,similarity2)
    wb2.save('f22.xls')
wb2.save('f22.xls')
#--------------------------------------------------------------------------------------
#LEVEL 1 FEATURE 3 CALCULATION
#--------------------------------------------------------------------------------------
word_idf_table = {}
total_num_user_queries = len(total_queries)
for i in range(len(final_word_list)):
    str1 = final_word_list[i]
    word_idf_table[str1] = computeIDF(total_num_user_queries,str1,total_queries)
word_idf_table = dict((k,float(v)) for k,v in word_idf_table.iteritems())

mean_idf = 0
for w in word_idf_table:
    mean_idf += word_idf_table[w]
mean_idf /= len(final_word_list)
for w in word_idf_table:
    if word_idf_table[w]==32767:
        word_idf_table[w] = mean_idf
wb3 = Workbook()
sh3 = wb3.add_sheet('Sheet1')
sh3.col(0).width = 17000

for i in range(len(total_queries)):
    s3 = total_queries[i]
    s = cleanString(s3)
    s_w = s.split()
    common3 = set(main_query_words).intersection(s_w)
    var = [w for w in s_w if w not in common3]
    var = var + main_query_words
    q_dicn = {}
    s_dicn = {}
    for w in var:
        if w in main_query_words:
            tf = computeTF(w,main_query)
            try:
                idf = word_idf_table[w]
                q_dicn[w] = tf*idf
            except:
                q_dicn[w] = 0
        else:
            q_dicn[w] = 0
        if w in s_w:
            tf = computeTF(w,s)
            idf = word_idf_table[w]
            s_dicn[w] = tf*idf
        else:
            s_dicn[w] = 0
    p = dotProduct(q_dicn,s_dicn)
    cos = cosTheta(q_dicn,s_dicn,p)
    sh3.write(i,0,s3)
    sh3.write(i,1,cos)
    wb3.save('f33.xls')
wb3.save('f33.xls')
#--------------------------------------------------------------------------------------
#LEVEL 1 FEATURE 4 CALCULATION
#--------------------------------------------------------------------------------------
main_query_nouns = []
dict_file = ''
if inp0=='ecig':
    main_query_nouns = ['ecigarettes','cigarettes','electronic']
    dict_file = 'Dictionary_ecig_t.xls'
elif inp0=='skincancer':
    main_query_nouns = ['skin','cancer','sun']
    dict_file = 'Dictionary_skincancer_t.xls'
elif inp0=='mmr_vaccine':
    main_query_nouns = ['mmr','vaccine','autism']
    dict_file = 'Dictionary_mmr_t.xls'
elif inp0=='vitaminC':
    main_query_nouns = ['vitaminc','cold']
    dict_file = 'Dictionary_vitamin_t.xls'
elif inp0=='hrt':
    main_query_nouns = ['women','hrt','menopause']
    dict_file = 'Dictionary_hrt_t.xls'
wb = xlrd.open_workbook(dict_file)
sh = wb.sheet_by_index(0)
key_word = sh.col_values(0)
meaning_val = sh.col_values(1)    
nouns = {x.name().split('.',1)[0] for x in wn.all_synsets('n')}
l = 0
wb4 = Workbook()
sh4 = wb4.add_sheet('Sheet1')
sh4.col(0).width = 17000
meaning = "string"
for i in range(len(total_queries)):
    q4 = total_queries[i]
    q = cleanString(q4)
    q_words4 = q.split()
    q_nouns = q_words4
    common_nouns = set(main_query_nouns).intersection(q_nouns)
    common_nouns = list(common_nouns)
    if(len(common_nouns)!=len(main_query_nouns)):
        for w in q_nouns:
            nn = subString(main_query_nouns,w)
            common_nouns += nn
            common_nouns = list(set(common_nouns))
        
    if(len(common_nouns)!=len(main_query_nouns)):
        for w in q_nouns:
            try:
                k = key_word.index(w)
                meaning = meaning_val[k]
            except wikipedia.exceptions.DisambiguationError:
                meaning = 'many_meanings'
            except wikipedia.exceptions.PageError:
                meaning = 'many_meanings'
            except:
                meaning = 'many_meanings'
                pass
            meaning = cleanString(meaning)
            meaning_nouns = meaning.split()
            meaning_nouns = [w for w in meaning_nouns if w in nouns]
            for x in meaning_nouns:
                nn = subString(main_query_nouns,x)
                common_nouns += nn
                common_nouns = list(set(common_nouns))
            common = set(main_query_nouns).intersection(meaning_nouns)
            common_nouns += common
            common_nouns = list(set(common_nouns))
    f=len(common_nouns)/float(len(main_query_nouns))
    sh4.write(l,0,q4)
    sh4.write(l,1,f)
    l = l+1
    wb4.save('f44.xls')
wb4.save('f44.xls')

#--------------------------------------------------------------------------------------
#LEVEL 1 FEATURE 5 CALCULATION
#--------------------------------------------------------------------------------------
wb5 = Workbook()
sh5 = wb5.add_sheet('Sheet1')
sh5.col(0).width = 17000
l = 0
for i in range(len(total_queries)):
    q5 = total_queries[i]
    q = cleanString(q5)
    q_words5 = q.split()
    common5 = set(main_query_words).intersection(q_words5)
    common5 = list(set(common5))
    uncommon = [w for w in q_words5 if w not in common5]
    for x in uncommon:
        try:
            ind = key_word.index(x)
            meaning = meaning_val[ind]
        except wikipedia.exceptions.DisambiguationError:
            meaning = 'many_meanings'
        except wikipedia.exceptions.PageError:
            meaning = 'many_meanings'
        except:
            meaning = 'many_meanings'
        if ((meaning == 'many_meanings')or(meaning=='')):
            pass
        else:
            meaning = cleanString(meaning)
            present = isPresent(main_query_words,meaning)
            common5 += present
    common5 = list(set(common5))     
    similarity5 = (2*len(common5))/float((len(main_query_words)+len(q_words5)))  
    sh5.write(l,0,q5)
    sh5.write(l,1,similarity5)
    l = l+1
    wb5.save('f55.xls')
wb5.save('f55.xls')            
#--------------------------------------------------------------------------------------
#MERGE FEATURES OF LEVEL 1 INTO ONE FILE 
#--------------------------------------------------------------------------------------
w1 = xlrd.open_workbook('f11.xls')
s1 = w1.sheet_by_index(0)
f1 = s1.col_values(1)
q = s1.col_values(0)
w2 = xlrd.open_workbook('f22.xls')
s2 = w2.sheet_by_index(0)
f2 = s2.col_values(1)
w3 = xlrd.open_workbook('f33.xls')
s3 = w3.sheet_by_index(0)
f3 = s3.col_values(1)
w4 = xlrd.open_workbook('f44.xls')
s4 = w4.sheet_by_index(0)
f4 = s4.col_values(1)
w5 = xlrd.open_workbook('f55.xls')
s5 = w5.sheet_by_index(0)
f5 = s5.col_values(1)
x = 0
w0 = Workbook()
s0 = w0.add_sheet('Sheet1')
s0.col(0).width = 17000
for s in q:
    s0.write(x,0,q[x])
    s0.write(x,1,f1[x])
    s0.write(x,2,f2[x])
    s0.write(x,3,f3[x])
    s0.write(x,4,f4[x])
    s0.write(x,5,f5[x])
    s0.write(x,6,labels[x])
    x = x+1
    w0.save('Features_l1.xls')
w0.save('Features_l1.xls')
#--------------------------------------------------------------------------------------
#LEVEL 1 CLASSIFIER
#--------------------------------------------------------------------------------------
if inp0=='ecig':
    inp1 = 'ecig_l1_trainF.xls'
elif inp0=='skincancer':
    inp1 = 'skincancer_l1_trainF.xls'
elif inp0=='hrt':
    inp1 = 'hrt_l1_trainF.xls'
elif inp0=='vitaminC':
    inp1 = 'vitaminc_l1_trainF.xls'
elif inp0=='mmr_vaccine':
    inp1 = 'mmr_vaccine_l1_trainF.xls'
wb = xlrd.open_workbook(inp1)
sh = wb.sheet_by_index(0)
target_l1 = sh.col_values(6)
row_num = len(sh.col_values(0))
n_features_l1 = [sh.col_values(1),sh.col_values(2),sh.col_values(3),sh.col_values(4),sh.col_values(5)]
n_features_l1 = np.array([n_features_l1])
n_features_l1 = n_features_l1.astype(np.float)

sh1,nx,ny= n_features_l1.shape
d2_n_features_l1 = n_features_l1.reshape(sh1,nx*ny)
print d2_n_features_l1
d2_n_features_l1 = d2_n_features_l1.reshape((row_num,5))
print d2_n_features_l1

data_file = 'Features_l1.xls'
wb = xlrd.open_workbook(data_file)
sh = wb.sheet_by_index(0)
row_num = len(sh.col_values(0))
n_features_l1t = [sh.col_values(1),sh.col_values(2),sh.col_values(3),sh.col_values(4),sh.col_values(5)]
n_features_l1t = np.array([n_features_l1t])
n_features_l1t = n_features_l1t.astype(np.float)

sh1,nx,ny= n_features_l1t.shape
d2_n_features_l1t = n_features_l1t.reshape(sh1,nx*ny)
print d2_n_features_l1t
d2_n_features_l1t = d2_n_features_l1t.reshape((row_num,5))
print d2_n_features_l1t


classifier1 = svm.SVC(C=10000000, cache_size=200, class_weight=None, coef0=0.0,decision_function_shape=None, degree=3, gamma=0.006, kernel='poly',max_iter=-1, probability=False, random_state=None, shrinking=True,tol=0.001, verbose=False)
classifier1.fit(d2_n_features_l1, target_l1)
predictions_l1 = classifier1.predict(d2_n_features_l1t)
p=0
wb2 = Workbook()
sh2 = wb2.add_sheet('Sheet1')
sh2.col(0).width = 17000
for i in range(row_num):
    if predictions_l1[i] == 'relevant':
        p = 1
    else:
        p = 0
    sh2.write(i,1,p)
    sh2.write(i,2,predictions_l1[i])
    wb2.save('e1.xls')
wb2.save('e1.xls')
#--------------------------------------------------------------------------------------
#LEVEL2 FEATURE CALCULATION
#--------------------------------------------------------------------------------------
xyz = ''
inp2 = ''
if inp0=='ecig':
    inp2 = 'ecig_l2_trainF.txt'
    xyz = 'ecig_train_data.xlsx'
elif inp0=='skincancer':
    inp2 = 'skincancer_l2_trainF.txt'
    xyz = 'skincancer_train_data.xlsx'
elif inp0=='hrt':
    inp2 = 'hrt_l2_trainF.txt'
    xyz = 'hrt_train_data.xlsx'
elif inp0=='vitaminC':
    inp2 = 'vitaminc_l2_trainF.txt'
    xyz = 'vitaminc_train_data.xlsx'
elif inp0=='mmr_vaccine':
    inp2 = 'mmr_vaccine_l2_trainF.txt'
    xyz = 'mmr_vaccine_train_data.xlsx'    
#===================================
wxyz = xlrd.open_workbook(xyz)
sxyz = wxyz.sheet_by_index(0)
sents = sxyz.col_values(0)
finale_words = cleanWords(sents)
L1 = set(finale_words)
wtest = xlrd.open_workbook(filename)
stest = wtest.sheet_by_index(0)
sents_test = stest.col_values(0)
words_test = cleanWords(sents_test)
L2 = set(words_test)
diff = list(L1-L2)
L = diff + words_test
#====================================
wbl1 = xlrd.open_workbook('e1.xls')
shl1 = wbl1.sheet_by_index(0)
relevancy = shl1.col_values(1)
wb = Workbook()
sh = wb.add_sheet('Sheet1')
sh.col(0).widh = 17000
fobj = open('test','w')
for s in total_queries:
    index = total_queries.index(s)
    dictionary = word_idf_table.copy()
    s1 = cleanString(s)
    word = s1.split()
    word = [w.lower() for w in word]
    for w in L:
        if w in word:
            val = computeTF(w,s)
            idf = dictionary[w]
            dictionary[w] = val*idf
        else:
            dictionary[w] = 0
        fobj.write(str(dictionary[w]))
        fobj.write(' ')
    pos_neg_value(fobj,s,i)
    flag = 0
    fobj.write(str(relevancy[index]))
    fobj.write('\n')
fobj.close()
crs = open("test", "r")
rows = (row.strip().split() for row in crs)
a = zip(*rows)
#--------------------------------------------------------------------------------------
#LEVEL2 CLASSIFIER
#--------------------------------------------------------------------------------------
data_file_l2 = inp2
temp0 = open(inp2,'r')
rows = (row.strip().split() for row in temp0)
ab = zip(*rows)
target_l2 = sxyz.col_values(2)
row_num1 = len(ab[0])
n_features_l2 = ab
n_features_l2 = np.array([n_features_l2])
n_features_l2 = n_features_l2.astype(np.float)

sh1,nx,ny= n_features_l2.shape
d2_n_features_l2 = n_features_l2.reshape(sh1,nx*ny)
print d2_n_features_l2
d2_n_features_l2 = d2_n_features_l2.reshape((row_num1,len(ab)))

row_num = len(a[0])
n_features_l2t = a 
n_features_l2t = np.array([n_features_l2t])
n_features_l2t = n_features_l2t.astype(np.float)

sh1,nx,ny= n_features_l2t.shape
d2_n_features_l2t = n_features_l2t.reshape(sh1,nx*ny)
d2_n_features_l2t = d2_n_features_l2t.reshape((row_num,len(a)))


classifier2 = svm.SVC(C=10000000, cache_size=200, class_weight=None, coef0=0.0,decision_function_shape=None, degree=3, gamma=0.005, kernel='rbf',max_iter=-1, probability=False, random_state=None, shrinking=True,tol=0.001, verbose=False)
classifier2.fit(d2_n_features_l2, target_l2)
predictions_l2 = classifier2.predict(d2_n_features_l2t)

wb12 = Workbook()
sh12 = wb12.add_sheet('Sheet1')
sh12.col(0).width = 17000
i=0
for i in range(row_num):
    sh12.write(i,0,predictions_l2[i])
    wb12.save('e2.xls')
wb12.save('e2.xls')
#--------------------------------------------------------------------------------------
#FINAL RESULT FILE GENERATION
#--------------------------------------------------------------------------------------
fname = inp0+'.xlsx'
wbf = xlrd.open_workbook(fname)
shf = wbf.sheet_by_index(0)
valf = shf.col_values(0)
wbfl1 = xlrd.open_workbook('e1.xls')
shfl1 = wbfl1.sheet_by_index(0)
valfl1 = shfl1.col_values(2)
wbfl2 = xlrd.open_workbook('e2.xls')
shfl2 = wbfl2.sheet_by_index(0)
valfl2 = shfl2.col_values(0)


wb = Workbook()
sh = wb.add_sheet('Sheet1')
sh.col(0).width = 17000
i = 0
for i in range(len(valf)):
    sh.write(i,0,valf[i])
    sh.write(i,1,valfl1[i])
    sh.write(i,2,valfl2[i])
    wb.save('FINAL.xls')
    i = i+1
wb.save('FINAL.xls')
#--------------------------------------------------------------------------------------
#------------------------------------------END-----------------------------------------
