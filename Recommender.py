'''
Created on Mar 23, 2015

Recommender using Word2Vec 

@author: mgulcin
'''
import os
from os import listdir
from os.path import isfile, join
import csv
import random
from gensim.models import Word2Vec
from KNearestItemsRecommender import KNearestItemRecommender
from NNeighborsRecommender import NNeighborsRecommender
from KItemsUnionRecommender import KItemsUnionRecommender

dataFolder =  "data" 
checkinsFileName = "checkins.csv"

modelFolder= 'model/'
outDataFolder =  os.path.join('output/', "temp") 


'''
Note: 
# "N_Neighbors" "k_NearestItems"  & #"k_ItemsUnion"  use userids as parameters, 
however (for now) models does not contain that info!! Nasil calisiyor o zaman??
'''
# recommendation type
rec_type = "N_Neighbors" #"k_NearestItems" #"k_ItemsUnion"  #"N_Neighbors_Inverted" #"k_ItemsUnion_Inverted"   #"k_NearestWithoutUser"
        

def hash32(value):
    random.seed(123)
    return hash(value) & 0xffffffff

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


def readVenues(trainDataFolder):
    inFile =  open(os.path.join(os.path.dirname(__file__), trainDataFolder, "locationsList.csv"), "r")
    reader = csv.reader(inFile)
    
    # populate list - only a single list (not list of list)
    loc_list = list(reader)[0]
    
    return loc_list

def readUsers(trainDataFolder):
    inFile =  open(os.path.join(os.path.dirname(__file__), trainDataFolder, "usersList.csv"), "r")
    reader = csv.reader(inFile)
    
    # populate list - only a single list (not list of list)
    user_list = list(reader)[0]
    
    return user_list

def readHometowns(trainDataFolder):
    inFile =  open(os.path.join(os.path.dirname(__file__), trainDataFolder, "hometownsMultiLine.csv"), "r")
    reader = csv.reader(inFile)
    
    # populate list - only a single list (not list of list)
    hList = list(reader)
    hometown_list = [el[1] for el in hList]
    
    return hometown_list

def create_checkins_map(checkins): 
    checkins_map = {d[0]: d[1:] for d in checkins}
    return checkins_map
    
'''
    # predict/recommend new locations that a user will visit
    k = 10; # output_size
    N = 30; # neighbor_count
    rec_type =  # recommendation type
        "k_NearestItems"
        "N_Neighbors"
        "k_ItemsUnion"
        "k_NearestWithoutUser"
        "k_ItemsUnion_Inverted"
        N_Neighbors_Inverted"
    users_list # list of target users
    loc_list   # list of locations that can be recommended (seen in the training set)
'''
def recommend(outtrainDataFolder, outFileName, model, users_list, loc_list, hometown_list, rec_type, k=10, N=30, modelInverted=None):
   
    # get items list
    if rec_type == "k_NearestItems":
        rc = KNearestItemRecommender()
        rc.recommend(outtrainDataFolder, outFileName, model, users_list, loc_list, hometown_list, k)
     
    elif rec_type == "N_Neighbors":
        # create map from checkins,  since it is eaiser to use
        checkins = readCsvData(dataFolder, checkinsFileName)
        # create user-->checkins map
        checkins_map = create_checkins_map(checkins)
        
        rc = NNeighborsRecommender()
        rc.recommend(outtrainDataFolder, outFileName, model, checkins_map, users_list, loc_list, hometown_list, k, N)
        
    elif rec_type == "k_ItemsUnion":
        rc = KItemsUnionRecommender()
        rc.recommend(outtrainDataFolder, outFileName, model, users_list, loc_list, hometown_list, k, N)   
    else:
        print("Error in rec_type")
        
def getRectTypeShortForm(rec_type):
    shortForm = "NoShortForm"
    
    if rec_type == "k_NearestItems":
        shortForm = "KNI"
        
    elif rec_type == "N_Neighbors":
        shortForm = "NN"
        
    elif rec_type == "k_ItemsUnion":
        shortForm = "KIU"
    else:
        print("Error in rec_type @ short form") 
        
    return shortForm

def getOutFileName(rec_type, modelInverted_name, model_name):
    outFileName = None
    if rec_type == "k_NearestItems" or rec_type == "N_Neighbors" or  rec_type == "k_ItemsUnion" or rec_type == "k_NearestWithoutUser":
        outFileName = model_name
    elif rec_type == "k_ItemsUnion_Inverted" or rec_type == "N_Neighbors_Inverted":
        outFileName = modelInverted_name
    #else: print("Error in rec_type @ outFileName) 
    
    return outFileName
        

    
def run(onlyModelFiles):
    #for featureCount in range(100, 101, 10):
    for model_name in onlyModelFiles: 
        # Do  not re-run the recommendation for the same recType & model
        outFileName = getOutFileName(rec_type, "no_inverted_model", model_name)
        outFileFullName = os.path.join(os.path.dirname(__file__), outDataFolder, outFileName)
       
        isProcessed = os.path.exists(outFileFullName)
        if isProcessed==True:
            continue;
            
        # start recommendation
        # use an existing model
        # load model
        print("model_name: ", model_name)
        modelPath = os.path.join(os.path.dirname(__file__), modelFolder, model_name)
        model = Word2Vec.load(modelPath)
              
           
        # predict/recommend new locations that a user will visit
        # get users and loc lists (to be used while giving recommendation)
        users_list = readUsers(dataFolder) # target list
        loc_list = readVenues(dataFolder)  # candidate pool
        hometown_list = readHometowns(dataFolder)  # hometown list
            
        print("users_list size: ", len(users_list))
        print("loc_list size: ", len(loc_list))
        print("hometown_list size: ", len(hometown_list))
         
        # set other parameters
        k = 10 # output_size
        N = 30 # neighbor_count
        outFileName = getOutFileName(rec_type, "no_inverted_model", model_name)
        recommend(outDataFolder, outFileName, model, users_list, loc_list, hometown_list, rec_type, k, N, model)
                   
    
    return

if __name__ == '__main__':
    # recommend
    onlyModelFiles = [ f for f in listdir(modelFolder) if isfile(join(modelFolder,f)) ]
    run(onlyModelFiles);
     
    
    