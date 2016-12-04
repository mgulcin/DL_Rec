'''
Created on Mar 23, 2015

Single document, extractive summarization using Word2Vec 

@author: makbule.ozsoy
'''
from collections import Counter
from collections import defaultdict
import gc
import operator
import os
import time


class Commons(object):
    
    def printRecs(self, recDict, users_list, outFolderName,outFileName):
        for target_userid in users_list:
            # print the results to a file
            #print(target_userid, " : ", rec_items)
            out = os.path.join(os.path.dirname(__file__), outFolderName,outFileName);
            
            rec_items = recDict.get(target_userid)
            if rec_items != None:
                rec_items_str = ','.join(rec_items) 
                
                outFile = open(out, "a")
                outFile.write(target_userid+",")
                outFile.write(rec_items_str)
                outFile.write("\n")
    
        return
         
    def removeUnwantedItems(self, model, postiveList, topn, unwantedItemsList):
        # filter unknown words, e.g. user0--> w=user0, o.w. I get an error: e.g. KeyError: "word 'loc7775' not in vocabulary"
        w = filter(lambda x: x in model.vocab, postiveList)
        
        wNot = filter(lambda x: x not in model.vocab, postiveList)
        if(len(wNot) > 0):
            print(wNot)
        
        # because of filtering there can be empty list
        if(len(w) <= 0):
            return []
        
        # if rec_items contain any item from unwantedItemsList, do something
        # I'm trying to do sth like do-while 
        ret_item_tuples = model.most_similar(positive=w,topn=topn)
        ret_items = [ seq[0] for seq in ret_item_tuples ]
        s1, s2 = set(ret_items), set(unwantedItemsList)
        shared = s1 & s2 # intersection, only the elements in both
                

        while (len(ret_items)-len(shared)) < topn:
           
            # increment output list size
            temp_k = topn + (len(shared)*3)
            #print(temp_k)
            # get larger number of similar items
            ret_item_tuples = model.most_similar(positive=postiveList,topn=temp_k)
            ret_items = [ seq[0] for seq in ret_item_tuples ]
            s1, s2 = set(ret_items), set(unwantedItemsList)
            shared = s1 & s2 # intersection, only the elements in both
            
               
       
        
        # remove items which start with "user"
        #for item in shared:
        #    ret_items.remove(item)
        ret_items = filter(lambda x: x not in shared, ret_items)
             
        # remove if too many items are collected    
        if len(ret_items) > topn:
            ret_items = ret_items[0:topn]

        
        return ret_items
        
           
            