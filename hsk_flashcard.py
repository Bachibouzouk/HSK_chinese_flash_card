# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 12:27:18 2016

@author: pfduc
"""

import numpy as np
import csv

class FlashCardBrowser(object):
    """this class takes care of managing the flash cards and browsing through them"""
    def __init__(self,fname = None):
        if not fname == None :
            self.voc_list = self.import_voc_list(fname)
        else:
            self.voc_list = self.import_voc_list()
            
            
    def import_voc_list(self,fname='HSK_Level_5.csv'):
        """ 
        this function loads the vocabulary list from a given csv file
        it expects the following format from the file : 'Order','HSK Level-Order','Word','Pronunciation','Definition','score'
        It will return an array of array ignoring the first 2 columns    
        """
        hsk_data=[]
        with open(fname, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                #get rid of the HSK level order as I am not using it
                row.pop(1)
                hsk_data.append(row)
        return np.array(hsk_data)            
        
    def save_voc_list(self,fname="HSK_Level_5.txt"):
        """ this function save the hsk data from a session back to a csv file"""
        with open(fname,"wb") as csvfile:
        
            writer = csv.writer(csvfile)
            writer.writerows(self.voc_list)
        
    def word_picking(self):
        """ this function chooses a word with a score of 0 from the word list"""   
        
        #choose only from the words which have a 0 in the score column (i.e. unknowns)
        unknown_words = self.voc_list[self.voc_list[:,4] == '0',:]
        #pick a random integer between 0 and the size of the unknows list
        index_picked = np.random.random_integers(0,len(unknown_words)-1)
        
        #find the index of the word inside the whole list
        index_picked = unknown_words[index_picked,0]
        
        #extract the word from the whole list
        word = np.squeeze(self.voc_list[self.voc_list[:,0] == index_picked,:])
        return word

if __name__=="__main__":
    
    test=FlashCardBrowser()    
    print test.word_picking()