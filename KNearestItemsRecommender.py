'''
Created on Mar 23, 2015


@author: mgulcin
'''
import copy
import os
from Commons import Commons

class KNearestItemRecommender(object):
    
    def find_rec_items(self, model, target_userid, unwantedList, k):
         
        # I'm trying to do sth like do-while 
        postiveList = [target_userid]
        
        # remove unwanted items
        commons = Commons()
        items = commons.removeUnwantedItems( model = model, postiveList = postiveList, 
                                         topn = k, unwantedItemsList = unwantedList)
        
        # find items to recommend
        rec_items = items
            
        # return 
        return rec_items

    
    def recommend(self, outFolderName, outFileName, model, users_list, loc_list, hometown_list, k=10):
        for target_userid in users_list:
            #temp_user_list =  copy.deepcopy(users_list)
            #try:
            #    temp_user_list.remove(target_userid)
            #except ValueError:
            #    pass
                        
            # find rec items
            unwantedList = users_list + hometown_list
            rec_items = self.find_rec_items(model, target_userid, unwantedList, k)
                
            # print the results to a file
            #print(target_userid, " : ", rec_items)
            out = os.path.join(os.path.dirname(__file__), outFolderName, outFileName);
            
            rec_items_str = ','.join(rec_items) 
            
            outFile = open(out, "a+")
            outFile.write(target_userid+",")
            outFile.write(rec_items_str)
            outFile.write("\n")
            
            