'''
Created on Mar 23, 2015

@author: mgulcin
'''
from collections import Counter
from collections import defaultdict
import gc
import operator
import os
import time
from Commons import Commons

class KItemsUnionRecommender(object):
    def create_inverted_list(self, data):
        index = defaultdict(list)
        for i, tokens in enumerate(data):
            for token in tokens:
                index[token].append(i)
        return index
    
    '''
    Difference from KNearestItems:
    In KNI: Find items that are close to the target user only
    In this (KIU): Find items that are close to the target user and his neighbors
    '''
    def find_rec_items(self, model, rec_neighbours, target_userid, unwantedList, k):
        # I'm trying to do sth like do-while 
        postiveList = [target_userid]
        postiveList.extend(rec_neighbours)
        
        # remove unwanted items
        commons = Commons()
        items = commons.removeUnwantedItems( model = model, postiveList = postiveList, 
                                         topn = k, unwantedItemsList = unwantedList)
        
        # find items to recommend
        rec_items = items
            
        # return 
        return rec_items
    
    
    def getNeighbors(self, model, target_userid, unwantedList, N):
        # I'm trying to do sth like do-while 
        rec_neighbours_tuples = model.most_similar(positive=[target_userid],topn=N)
        rec_neighbours = [ seq[0] for seq in rec_neighbours_tuples ]
            
        # if rec_items contain any locid(start with "loc") or "hometown", do something
        s1, s2 = set(rec_neighbours), set(unwantedList)
        shared = s1 & s2 # intersection, only the elements in both
                
        while (len(rec_neighbours)-len(shared)) < N:
            # increment output list size
            temp_N = N + (len(shared)*3)
            # get larger number of similar items
            rec_neighbours_tuples = model.most_similar(positive=[target_userid],topn=temp_N)
            rec_neighbours = [ seq[0] for seq in rec_neighbours_tuples ]
            s1, s2 = set(rec_neighbours), set(unwantedList)
            shared = s1 & s2 # intersection, only the elements in both
            
        # remove items which start with "loc"
        for loc_item in shared:
            rec_neighbours.remove(loc_item)
            
        # remove if too many items are collected    
        if len(rec_neighbours) > N:
            rec_neighbours = rec_neighbours[0:N]
                
        return rec_neighbours
    
    def recommend(self, outFolderName, outFileName, model, users_list, loc_list, hometown_list, k=10, N=30):
        rec_dict = dict()
        commons = Commons()
        temp_index = 0
        
        user_collected_list = list()
        for target_userid in users_list: 
            # get neighbours
            unwantedList1 = loc_list + hometown_list
            rec_neighbours = self.getNeighbors(model, target_userid, unwantedList1, N)
           
            # get similar locations that neighbours has visited
            unwantedList2 = users_list + hometown_list
            rec_items = self.find_rec_items(model, rec_neighbours, target_userid, unwantedList2, k)
                   
            # add to dict              
            rec_dict[target_userid] = rec_items
            user_collected_list.append(target_userid)
            
            # print for every 10 target users
            if (temp_index%100) == 0 and temp_index != 0:
                commons.printRecs(rec_dict, user_collected_list, outFolderName, outFileName)   
                temp_index = 0
                rec_dict.clear() 
                del user_collected_list[:]
                
            else: 
                temp_index = temp_index + 1    
                #time.sleep(0.5) # to reduce cpu, or what should i do? 
                
                
            
        # print the rest
        commons.printRecs(rec_dict, user_collected_list, outFolderName, outFileName)      
            