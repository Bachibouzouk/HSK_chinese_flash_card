# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 12:27:18 2016

IMPROVEMENT :
Then give the user possibilities to browse HSK * words only (without including all the lower HSK words)
Or browse only the liked words

@author: pfduc
"""

from PyQt4.QtGui import QFont, QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QPushButton, QMessageBox, QFileDialog, QInputDialog
from PyQt4.QtCore import SIGNAL
import sys
import os
import numpy as np
import csv

# This are global variables used by HSKGui
ASK_WORD = 2
ASK_PRON = 3
ASK_DEF = 4
ASSESS = 5

KNOWN_WORD = '1'
UNKNOWN_WORD = '0'

SCORE_ID = 'Score'
FAV_HDR_ID = 'Favorite'

FAV_ID = '1'
NOT_FAV_ID = '0'


class HSKGui(QWidget):
    """
    GUI to display flash cards and browse through them.
    The description of how this class works lies in the method on_browseButton_clicked()
    """

    def __init__(self, parent=None, fname=None):

        super(HSKGui, self).__init__(parent)

        # main layout of the form is the verticallayout
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # main layout of the form is the verticallayout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.charLayout = QHBoxLayout()
        self.charLayout.setObjectName("charLayout")
        # labels which will be used to display the score, the character, its
        # prononciation and its definition

        self.headerLabel = QLabel(self)

        self.scoreLabel = QLabel(self)

        self.numwordLabel = QLabel(self)
        self.numwordLabel.setText("#Words : 0")

        self.horizontalLayout.addWidget(self.headerLabel)
        self.horizontalLayout.addWidget(self.scoreLabel)
        self.horizontalLayout.addWidget(self.numwordLabel)

        self.charLabel = QLabel(self)
        self.charLabel.setFont(QFont("Helvetica", 45))

        # checkbox used to say that we would like to set this character in our
        # favorite ones
        self.favBox = QCheckBox(self)

        self.charLayout.addWidget(self.charLabel)
        self.charLayout.addWidget(self.favBox)

        self.prononciationLabel = QLabel(self)
        self.prononciationLabel.setFont(QFont("Helvetica", 20))

        self.defLabel = QLabel(self)
        self.defLabel.setFont(QFont("Helvetica", 15))
        self.defLabel.setWordWrap(True)
        # sets all labels to empty strings
        self.clear_fields()

        # adding the labels to thelayout
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.charLayout)
        self.verticalLayout.addWidget(self.prononciationLabel)
        self.verticalLayout.addWidget(self.defLabel)

        # button to interact with the user
        self.browseButton = QPushButton(parent=self)
        self.browseButton.setText("Start")
        self.assessButton = QPushButton(parent=self)
        self.assessButton.setText("Options...")

        self.verticalLayout.addWidget(self.browseButton)
        self.verticalLayout.addWidget(self.assessButton)

        self.setLayout(self.verticalLayout)

        # link the click of the buttons to the execution of a method
        self.connect(self.browseButton, SIGNAL(
            'clicked()'), self.on_browseButton_clicked)
        self.connect(self.assessButton, SIGNAL(
            'clicked()'), self.on_assessButton_clicked)

        self.load_voc_list(fname)

        # a variable to contain the word asked
        self.current_word = None
        # this variable value indicates at which stage of the question we are
        self.question_stage = ASK_WORD
        # these are the options availiable
        self.option_list = {"Save current session": self.save_learning,
                            "Credits(disabled)": None, 
                            "Read the help(disabled)": None,
                            "Reset the known voc": self.reset_voc_list, 
                            "Load another list": self.load_voc_list}
        # this is the number of word one went through during one session
        self.numword = 0

    def load_voc_list(self, fname=None):
        """loads a vocabulary list from a user choosen location"""
        if fname == None:
            fname = str(QFileDialog.getOpenFileName(
                self, 'Load vocabulary list as', './'))

        if not fname == None:
            # a class responsible to browswe through a list of vocabulary
            self.browser = FlashCardBrowser(fname)
            # update the score
            prev_score = self.browser.calculate_score()
            self.change_score(*prev_score)

            # change the label of the header according to the filename
            self.headerLabel.setText(self.browser.get_fname())

            # resets the number of words done during the session
            self.numword = 0

    def reset_voc_list(self):
        """resets the number of known words to 0"""
        reply = QMessageBox.question(
            self, 'Message', "Do you want to reset your learning?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.browser.reset_word_learned()
            # update the score
            prev_score = self.browser.calculate_score()
            self.change_score(*prev_score)

    def increment_numword(self):
        """increment the number of words browsed"""
        self.numword = self.numword + 1
        self.numwordLabel.setText("#Words : %i" % (self.numword))

    def closeEvent(self, event):
        """when exiting the widget we are prompt with this question"""

        reply = QMessageBox.question(
            self, 'Message', "Do you want to save your learning?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # save the learning of the words
            self.save_learning()

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

            # update the state of the favorite word box
            self.update_favBox(self.current_word, self.favBox.isChecked())

            # picks a new word and displays only the character
            self.current_word = self.browser.word_picking()
            self.charLabel.setText(u"%s" % (self.current_word[ASK_WORD]))
            # update the state of the favorite word box
            self.update_favBox()

            # prepares the button to display the prononciation upon next click
            self.browseButton.setText("Show prononciation")
            self.question_stage = ASK_PRON

        elif self.question_stage == ASK_PRON:
            # displays the prononciation of the character
            self.prononciationLabel.setText(
                u"%s" % (self.current_word[ASK_PRON]))

            # prepares the button to display the definition upon next click
            self.browseButton.setText("Show definition")
            self.question_stage = ASK_DEF

        elif self.question_stage == ASK_DEF:
            # displays the definition of the character
            self.defLabel.setText(u"%s" % (self.current_word[ASK_DEF]))

            # prepares the buttons to ask the users whether they know the
            # character or not
            self.browseButton.setText("Don't Know")
            self.assessButton.setText("Know")
            self.question_stage = ASSESS

        elif self.question_stage == ASSESS:
            # The user clicked on "Don't Know"

            # prepares the buttons to ask the users to pick a new word
            self.browseButton.setText("Pick another word")
            self.assessButton.setText("Options...")
            self.question_stage = ASK_WORD

            self.increment_numword()

    def on_assessButton_clicked(self):
        """the button is alternatively "Know" or "Options..." """
        if self.question_stage == ASSESS:
            # the user clicked on "Know", so we update the score of the word in
            # the voc list
            self.current_word[-1] = KNOWN_WORD
            new_score = self.browser.word_learning(self.current_word)
            self.change_score(*new_score)

            # prepares the buttons to ask the users to pick a new word
            self.browseButton.setText("Pick another word")
            self.assessButton.setText("Options...")
            self.question_stage = ASK_WORD

            self.increment_numword()
        else:
            # this button is then used as an option menu trigger
            item, ok = QInputDialog.getItem(self, self.trUtf8("Options"),
                                            self.trUtf8("Choose an option"),
                                            self.option_list.keys())

            if ok:
                # execute the option from the list
                self.option_list[str(item)]()

    def change_score(self, known_num, tot_num):
        """update the label with the score"""
        self.scoreLabel.setText("Known words : %i/%i" % (known_num, tot_num))

    def save_learning(self):
        """prompt the user to save the current session in a file"""

        fname = str(QFileDialog.getSaveFileName(self, 'Save as', './%s'%(os.path.basename(self.browser.fname)), "*.csv"))
        if fname:
            self.browser.save_voc_list(fname)
        else:
            self.browser.save_voc_list("Flash_card_backup.csv")

    def update_favBox(self, word=None, fav_state=None):
        """update the state of the checkbox"""
        if word == None:
            # there is no word for which to update status
            if self.current_word == None:
                # the current word is None (very first iteration)
                self.favBox.setChecked(False)
            elif len(self.current_word) == 7:
                # there is a fav column, so we update the favBox
                if self.current_word[6] == FAV_ID:
                    self.favBox.setChecked(True)
                else:
                    self.favBox.setChecked(False)
            else:
                # there is no fav column
                self.favBox.setChecked(False)
        else:
            # there is a word in the argument
            if not len(self.current_word) == 7:
                word = np.append(word, 0)

            if fav_state:
                word[6] = FAV_ID
            else:
                word[6] = NOT_FAV_ID

            if len(self.current_word) == 7:
                #               #there is a fav column
                self.browser.add_fav_word(word)

            else:
                # there is no fav column
                self.browser.add_fav_word(word)


class FlashCardBrowser(object):
    """this class takes care of managing the flash cards and browsing through them"""

    def __init__(self, fname=None):
        if not fname == None:
            self.fname = fname
        else:
            self.fname = 'HSK_Level_5.txt'

        self.voc_list = self.import_voc_list(self.fname)

    def get_fname(self):
        """formatsthe fname for display"""

        fname = os.path.basename(self.fname)[:-4]
        fname = fname.replace('_', ' ')
        return fname

    def import_voc_list(self, fname='HSK_Level_5.txt'):
        """ 
        this function loads the vocabulary list from a given csv file
        it expects the following format from the file : 'Order','HSK Level-Order','Word','Pronunciation','Definition','score'
        It will return an array of array ignoring the first 2 columns    
        """
        hsk_data = []
        with open(fname, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                hsk_data.append(row)

        # finds the column number corresponding to the score
        self.index_score = hsk_data[0].index(SCORE_ID)

        return np.array(hsk_data)

    def save_voc_list(self, fname=None):
        """ this function save the hsk data from a session back to a csv file"""
        if fname == None:
            fname = self.fname

        with open(fname, "wb") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.voc_list)

    def word_picking(self):
        """ this function chooses a word with a score of 0 from the word list"""

        # choose only from the words which have a 0 in the score column (i.e.
        # unknowns)
        unknown_words = self.voc_list[self.voc_list[
            :, self.index_score] == UNKNOWN_WORD, :]
        # pick a random integer between 0 and the size of the unknows list
        index_picked = np.random.random_integers(0, len(unknown_words) - 1)

        # find the index of the word inside the whole list
        index_picked = unknown_words[index_picked, 0]

        # extract the word from the whole list
        word = np.squeeze(
            self.voc_list[self.voc_list[:, 0] == index_picked, :])
        return word

    def word_learning(self, word):
        """this function recieves a word after its interaction with the user and updates its score in the vocabulary list"""
        self.voc_list[self.voc_list[:, 0] == word[0], :] = word
        return self.calculate_score()

    def add_fav_word(self, word):
        """flag a word as favorite"""
        if np.size(self.voc_list[self.voc_list[:, 0] == word[0], :]) == 6:
            # if the favorite flag option didn't exist we create it with the
            # flag to 0 automatically
            self.voc_list = np.hstack([self.voc_list, np.zeros(
                (len(self.voc_list[:, 0]), 1), dtype=np.int8)])
            # add the header name for this new column
            self.voc_list[0, -1] = FAV_HDR_ID

        # update the word
        self.voc_list[self.voc_list[:, 0] == word[0], :] = word

    def reset_word_learned(self):
        """this function sets back all the scores to UNKNOWN_WORD"""
        for i in range(len(self.voc_list) - 1):
            self.voc_list[i + 1, self.index_score] = UNKNOWN_WORD

    def calculate_score(self):
        """this function computes the total score and number of known words"""

        unknown_words_num = len(
            self.voc_list[self.voc_list[:, self.index_score] == UNKNOWN_WORD, :])
        known_words_num = len(
            self.voc_list[self.voc_list[:, self.index_score] == KNOWN_WORD, :])

        total_words_num = known_words_num + unknown_words_num
        return known_words_num, total_words_num

if __name__ == "__main__":

    app = QApplication(sys.argv)
    ex = HSKGui(fname="HSK_Level_5_PF.csv")
    ex.show()
    sys.exit(app.exec_())
