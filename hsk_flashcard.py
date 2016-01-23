# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 12:27:18 2016

@author: pfduc
"""

from PyQt4.QtGui import QFont,QWidget, QVBoxLayout, QLabel,QApplication,QPushButton, QMessageBox
from PyQt4.QtCore import SIGNAL
import sys
import numpy as np
import csv

#This are global variables used by HSKGui
ASK_WORD = 1
ASK_PRON = 2
ASK_DEF = 3
ASSESS = 4

KNOWN_WORD = '1'
UNKNOWN_WORD = '0'

class HSKGui(QWidget):
    """
    GUI to display flash cards and browse through them.
    The description of how this class works lies in the method on_browseButton_clicked()
    """
    def __init__(self, parent = None, fname = None):
        
        super(HSKGui, self).__init__(parent) 
        
        #a class responsible to browswe through a list of vocabulary
        self.browser=FlashCardBrowser(fname)
        #a variable to contain the word asked
        self.current_word=None
        #this variable value indicates at which stage of the question we are
        self.question_stage=ASK_WORD
        
        
        #main layout of the form is the verticallayout        
        self.verticalLayout = QVBoxLayout()      
        self.verticalLayout.setObjectName("verticalLayout")

        #labels which will be used to display the character, its prononciation and its definition
        self.charLabel = QLabel (self)
        newfont = QFont("Times", 30, QFont.Bold) 
        self.charLabel.setFont(newfont)
        
        self.prononciationLabel = QLabel (self)
        
        self.defLabel = QLabel (self)

        #sets all labels to empty strings
        self.clear_fields()
        
        #adding the labels to thelayout
        self.verticalLayout.addWidget(self.charLabel)
        self.verticalLayout.addWidget(self.prononciationLabel)
        self.verticalLayout.addWidget(self.defLabel)
        
        #button to interact with the user
        self.browseButton = QPushButton(parent = self)
        self.browseButton.setText("Pick a word")
        self.assessButton = QPushButton(parent = self)
        
        self.verticalLayout.addWidget(self.browseButton)
        self.verticalLayout.addWidget(self.assessButton)
        self.assessButton.setDisabled(True)
  
        self.setLayout(self.verticalLayout)
                        
        #link the click of the buttons to the execution of a method
        self.connect(self.browseButton,SIGNAL('clicked()'),self.on_browseButton_clicked)
        self.connect(self.assessButton,SIGNAL('clicked()'),self.on_assessButton_clicked)


    def closeEvent(self, event): 
        """when exiting the widget we are prompt with this question"""
        
        reply = QMessageBox.question(self, 'Message',"Do you want to save your learning?", QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            #save the learning of the words
            self.browser.save_voc_list("HSK_Level_5.txt")
        
        event.accept()

    def clear_fields(self):
        """resets the label fields to empty"""
        
        self.charLabel.setText("")
        self.prononciationLabel.setText("")
        self.defLabel.setText("")
        
    def on_browseButton_clicked(self):
        """called upon interaction of the user with the browseButton"""
        
        if self.question_stage == ASK_WORD:     
            
            self.clear_fields()
            
            #picks a new word and displays only the character
            self.current_word = self.browser.word_picking()
            self.charLabel.setText(u"%s"%(self.current_word[ASK_WORD]))
            
            #prepares the button to display the prononciation upon next click
            self.browseButton.setText("Show prononciation")
            self.question_stage = ASK_PRON
            
        elif self.question_stage == ASK_PRON:
            #displays the prononciation of the character
            self.prononciationLabel.setText(u"%s"%(self.current_word[ASK_PRON]))
            
            #prepares the button to display the definition upon next click
            self.browseButton.setText("Show definition")
            self.question_stage = ASK_DEF
            
        elif self.question_stage == ASK_DEF:
            #displays the definition of the character
            self.defLabel.setText(u"%s"%(self.current_word[ASK_DEF]))
            
            #prepares the buttons to ask the users whether they know the character or not
            self.browseButton.setText("Know")            
            self.assessButton.setDisabled(False)
            self.assessButton.setText("Don't Know")
            self.question_stage = ASSESS
            
        elif self.question_stage == ASSESS:
            #the user clicked on "Know", so we update the score of the word in the voc list
            self.current_word[-1] = KNOWN_WORD            
            self.browser.word_learning(self.current_word)
            
            #prepares the buttons to ask the users to pick a new word
            self.browseButton.setText("Pick a word")
            self.assessButton.setText("")
            self.assessButton.setDisabled(True)
            self.question_stage = ASK_WORD
            
            
    def on_assessButton_clicked(self):
        """the user clicked on "Don't know" button so we do nothing with this word"""
        
        #prepares the buttons to ask the users to pick a new word
        self.browseButton.setText("Pick a word")
        self.assessButton.setText("")
        self.assessButton.setDisabled(True)
        self.question_stage = ASK_WORD
        

class FlashCardBrowser(object):
    """this class takes care of managing the flash cards and browsing through them"""
    def __init__(self,fname = None):
        if not fname == None :
            self.voc_list = self.import_voc_list(fname)
            self.fname = fname
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
        
    def save_voc_list(self,fname = None):
        """ this function save the hsk data from a session back to a csv file"""
        if fname == None :
            fname = self.fname
            
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
        
    def word_learning(self,word):
        """this function recieve a word after its interaction with the user and updates its score in the vocabulary list"""
        self.voc_list[self.voc_list[:,0] == word[0],:] = word
        
       
if __name__=="__main__":
    
    app = QApplication(sys.argv)
    ex = HSKGui()
    ex.show()
    sys.exit(app.exec_())