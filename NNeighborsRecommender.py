'''

@author: mgulcin
'''
from collections import Counter
from collections import defaultdict
import gc
import operator
import os
import time
from Commons import Commons
from sphinx.ext.todo import Todo

class NNeighborsRecommender(object):
    def create_inverted_list(self, data):
        index = defaultdict(list)
        for i, tokens in enumerate(data):
            for token in tokens:
                index[token].append(i)
        return index
    
    def  get_visited_loc_counter(self, rec_neighbours, checkins_map):  
        cnt = Counter()
        for neighbor in rec_neighbours:
            visited_loc_list = checkins_map[neighbor]
            for visited_loc in visited_loc_list:
                cnt[visited_loc] += 1
        
        return cnt
    
    '''
    Get top-k locn. items from  reverse_sorted_visited_loc_list
    Note that reverse_sorted_visited_loc_list is already sorted by vote of neighbors
    Like collaborative filtering
    '''
    def find_rec_items(self,reverse_sorted_visited_loc_list, k, unwantedList, target_userid):
        
        rec_items = reverse_sorted_visited_loc_list[0:(k)]
        # if rec_items contain any userid(start with "user"), do something
        unwantedList.append("") # empty string is also unwanted
        unwantedList.append(" ") # empty string is also unwanted
        s1, s2 = set(rec_items), set(unwantedList)
        shared = s1 & s2 # intersection, only the elements in both
                
        while (len(rec_items)-len(shared)) < k:
            # increment output list size
            temp_k = k + (len(shared)*3)
            # get larger number of similar items
            rec_items = reverse_sorted_visited_loc_list[0:(temp_k)]
            s1, s2 = set(rec_items), set(unwantedList)
            shared = s1 & s2 # intersection, only the elements in both
            
        # remove items which start with "user"
        for user_item in shared:
            rec_items.remove(user_item)
        rec_items = filter(lambda x: x not in shared, rec_items)
            
        # remove if too many items are collected    
        if len(rec_items) > k:
            rec_items = rec_items[0:k]
            
        return rec_items
    
    def find_rec_items_from_counter(self,reverse_sorted_visited_loc_counter, model, 
                                    k, users_list, target_userid):
        rec_items_tuples = reverse_sorted_visited_loc_counter.most_common(k)
        rec_items =  [i[0] for i in rec_items_tuples]
        
        # if rec_items contain any userid(start with "user"), do something
        s1, s2 = set(rec_items), set(users_list)
        shared = s1 & s2 # intersection, only the elements in both
                
        while (len(rec_items)-len(shared)) < k:
            # increment output list size
            temp_k = k + len(shared)
            # get larger number of similar items
            rec_items_tuples = reverse_sorted_visited_loc_counter.most_common(temp_k)
            rec_items =  [i[0] for i in rec_items_tuples]
            s1, s2 = set(rec_items), set(users_list)
            shared = s1 & s2 # intersection, only the elements in both
            
        # remove items which start with "user"
        for user_item in shared:
            rec_items.remove(user_item)
            
        return rec_items
    
    '''
    Get N neighbors of the target_userid (using loc_list?)
    '''
    def getNeighbors(self, model, target_userid, unwantedList, N):
        # if rec_neighbours_tuples contain any locid(start with "loc"),  do not return them as neighbor
        # I'm trying to do sth like do-while 
        
        # TODO do i need this?
        if(target_userid in model.vocab):
            pass #print(target_userid)
        else: 
            return []
        
        #WHEN use Doc2Vec
        rec_neighbours_tuples = model.docvecs.most_similar(positive=[target_userid],topn=N)
        
        #WHEN use Word2Vec
        rec_neighbours_tuples = model.most_similar(positive=[target_userid],topn=N)
        Todo
        
        rec_neighbours = [ seq[0] for seq in rec_neighbours_tuples ]
        s1, s2 = set(rec_neighbours), set(unwantedList)
        shared = s1 & s2 # intersection, only the elements in both
                
        # when there are not enough (less than N) neighbor recommendations
        # collect more recommendations from the model
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
                
        return rec_neighbours
    
    def recommend(self, outFolderName, outFileName, model, checkins_map, users_list, loc_list, hometown_list, k=10, N=30):
        
        users_list = filter(lambda a: a != " ", users_list)
        users_list = filter(lambda a: a != "", users_list)
        users_list = filter(lambda a: a != ' ', users_list)
        
        
        rec_dict = dict()
        commons = Commons()
        temp_index = 0
        
        user_collected_list = list()
        
        for target_userid in users_list:
            if target_userid == ' ' or target_userid == '' or target_userid == None:
                print("empty userid!!!")
                print("users_list size:", len(users_list))
                break;
            
            # get neighbours
            unwantedList = loc_list + hometown_list
            rec_neighbours = self.getNeighbors(model, target_userid, unwantedList, N)
           
            if (len(rec_neighbours) <= 0):
                continue
                
            # get visited locations by the neighbours and create map of loc--> visited count
            visited_loc_counter = self.get_visited_loc_counter(rec_neighbours, checkins_map)
            
            #count most visited
            #reverse_sorted_visited_loc_counter = sorted(visited_loc_counter.items(), key=operator.itemgetter(1),  
            #                                 reverse=True)
            #reverse_sorted_visited_loc_dict = sorted_visited_loc_dict[::-1]
            reverse_sorted_visited_loc_counter =  visited_loc_counter.most_common()
            reverse_sorted_visited_loc_list = [i[0] for i in reverse_sorted_visited_loc_counter]
            
            #recommend top-k of them
            unwantedList2 = users_list + hometown_list
            rec_items = self.find_rec_items(reverse_sorted_visited_loc_list, k,
                                            unwantedList2, target_userid);
            #rec_items = self.find_rec_items_from_counter(visited_loc_counter, 
            #                                             model, k, unwantedList2, target_userid);                                
            
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
            
           
            