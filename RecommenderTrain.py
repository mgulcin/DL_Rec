'''
Created on April 04, 2016

Recommender using Word2Vec 

@author: mgulcin
'''

import os
import logging
import csv
import random
from gensim.models import Word2Vec
import time

trainDataFolder =  "data" 
modelFolder = os.path.join('model', "model-users")

def hash32(value):
    random.seed(123)
    return hash(value) & 0xffffffff


# Copied from KaggleWord2Vec tutorial written by Angela Chapman
# TODO make model name and other variables parametric!!
def train_word2vec_model(modelFolder, sentences, featureCount = None, contextCount=None, epochCount=None):
    # ****** Set parameters and train the word2vec model
    #
    # Import the built-in logging module and configure it so that Word2Vec
    # creates nice output messages
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
        level=logging.INFO)

    # Set values for various parameters
    if featureCount == None:
        num_features = 100    # Word vector dimensionality
    else:
        num_features = featureCount
        
    max_vocab_size=None
    min_word_count = 1    # Minimum word count
    num_workers = 1       # Number of threads to run in parallel
    
    # `window`(=context) is the maximum distance between the current and predicted word within a sentence.
    if contextCount == None:
        context = len(max(sentences,key=len))          # Context window size -- set to max length list of input
    else:
        context = contextCount
    #downsampling = 1e-3  # Downsample setting for frequent words
    downsampling = 0      # Off
    if epochCount == None:
        iterCount = 10        # Number of iterations (epochs) over the corpus.
    else:
        iterCount = epochCount
        
    # skip gram vs cbow
    algorithmType = 1;               # The training algorithm. By default (sg=1), skip-gram is used. Otherwise, cbow is employed.
    

    # Initialize and train the model (this will take some time)
    print ("Training Word2Vec model...")
    print("context window size: ", context)
    model = Word2Vec(sentences=sentences, workers=num_workers, \
                size=num_features, min_count = min_word_count, max_vocab_size=max_vocab_size, \
                window = context, sample = downsampling, seed=1, \
                hashfxn=hash32, iter = iterCount, sg=algorithmType)

    
    # If you don't plan to train the model any further, calling
    # init_sims will make the model much more memory-efficient.
    model.init_sims(replace=True)

    # It can be helpful to create a meaningful model name and
    # save the model for later use. You can load it later using Word2Vec.load()
    model_name = "checkin" + str(num_features) \
                + "Feature_1Minword_"+str(context)+"Context_"\
                + str(iterCount)+"Epoch_0Downsample_1Worker"
    modelPath = os.path.join(os.path.dirname(__file__), modelFolder, model_name)

    model.save(modelPath)
    
    return model

def readCsvData(trainDataFolder,fileName):
    # read document     
    inFile =  open(os.path.join(os.path.dirname(__file__), trainDataFolder, fileName), "r")
    reader = csv.reader(inFile)
    
    # populate list (each line in the csv is a list), whole input is a list of list
    data_list = list(reader)
    
    # filter empty strings #TODO why csv reader read them? 
    newList = [];
    for listLevel1 in data_list:
        listLevel1 = filter(lambda a: a != " ", listLevel1)
        listLevel1 = filter(lambda a: a != "", listLevel1)
        listLevel1 = filter(lambda a: a != ' ', listLevel1)
        listLevel1 = filter(lambda a: a != None, listLevel1) 
        if len(listLevel1) > 0:
            newList.append(listLevel1)
       
    return newList
    
def trainModel(trainDataFolder, fileNameList):
    # read train data
    data =[]
    for fileName in fileNameList:
        newData = readCsvData(trainDataFolder, fileName)
        data.extend(newData)
            
    # train model
    train_word2vec_model(modelFolder, data, 100, 20, 25) # default? 100 20 25
#     for featureCount in range(10, 101, 10):
#         model = train_word2vec_model(modelFolder, data, featureCount=featureCount, contextCount=20, epochCount=25) 
#      
#     for epoch in range(5, 21, 5):
#         model = train_word2vec_model(modelFolder,data, featureCount=100, contextCount=20, epochCount=epoch) 
#       
#     for contextCount in range(5, 16, 5):
#         model = train_word2vec_model(modelFolder,data, featureCount=100, contextCount=contextCount, epochCount=25) 
       
#     # also train for max
#     model =  train_word2vec_model(modelFolder, data)

if __name__ == '__main__':
    # train model using checkins
    fileNameList = [] 
    fileNameList.append("checkins.csv")
    model = trainModel(trainDataFolder, fileNameList)
   
    
    
