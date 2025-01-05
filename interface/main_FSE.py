import sys
import os
import re
import random

# define the path to the folder
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
parent_folder_path = os.path.dirname(folder_path)
sys.path.insert(0, parent_folder_path) 

# define name of the file
experimental_design = 'FSE'
results_folder = os.path.join(parent_folder_path, 'results')
if os.path.exists(results_folder) and os.path.isdir(results_folder):
    result_files = os.listdir(results_folder)
else:
    raise FileNotFoundError("Results folder does not exist.")
filtered_files = [f for f in result_files if re.match(rf'^{experimental_design}_\d{{4}}\.csv$', f)]
numeric_parts = [re.search(r'\d{4}', f).group() for f in filtered_files]
max_numeric_part = max(map(int, numeric_parts)) if numeric_parts else 0
new_file_name = f"{experimental_design}_{max_numeric_part + 1:04d}"

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtCore import Qt
from backend.model_interface import FSE
from backend.shared_info import *
from backend.styling import *


class MyWindow(QMainWindow):
    """
    Responsible of handling the view of the main window. The main window is composed by the main sentence stating
    the 2 options for the user, the two buttons for picking an option, and a button to confirm.

    Attributes:
            -sure_amount: value of the sure amount that can be chosen
            -lottery_1: value of the 1st amount offered in the lottery choice
            -lottery_2: value of the 2nd amount offered in the lottery choice
            -proba: probability to win the 1st amount in the lottery choice
            -code: code of the user
            -directory: directory to save the results in
            -model: the model used to calculate the results
            -sentence_string: the sentence showed above
    """

    def __init__(self):
        """
        Initializes the main window
        """
        super(MyWindow, self).__init__()
        self.xpos = 0
        self.ypos = 0
        self.width = 1200
        self.height = 600
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)
        self.setWindowTitle("Lottery Check")

        # Set empty attributes
        self.code = None
        self.directory = None

        # Initialize the model and the first question
        self.model = FSE()
        self.sure_amount = self.model.getSimAnswers().iloc[-1]['z']
        self.proba = self.model.getSimAnswers().iloc[-1]['p_x']
        
        # Initialize the UI
        self.initUI()
        

    def initUI(self):
        """
        Initializes all the UI elements
        """
        self.setWelcomeScreen()

    def setWelcomeScreen(self):
        """
        Sets up the welcome screen
        """
        # Create the welcome label
        self.welcome_label = QtWidgets.QLabel(experiment_text["welcome"])
        self.welcome_label.setFont(fontTitle)
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create the instructions label
        instructions_font = QFont()
        instructions_font.setPointSize(18)
        self.instructions_label = QtWidgets.QLabel("These are the instructions.")
        self.instructions_label.setFont(instructions_font)
        self.instructions_label.setAlignment(QtCore.Qt.AlignLeft)
        
        # Create a container widget for the instructions label
        self.instructions_container = QWidget()
        self.instructions_container.setStyleSheet("background-color: white; border-radius: 10px;")
        self.instructions_layout = QVBoxLayout()
        self.instructions_layout.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.instructions_layout.addWidget(self.instructions_label)
        self.instructions_container.setLayout(self.instructions_layout)
        
        # Create the proceed button
        self.proceed_button = QtWidgets.QPushButton("Proceed")
        self.proceed_button.setFont(fontProceed)
        self.proceed_button.setStyleSheet(buttonProceed)  # Apply the buttonProceed style
        self.proceed_button.clicked.connect(self.setQuestionScreen)
        
        # Set up the layout for the welcome screen
        self.welcome_widget = QWidget()
        self.welcome_layout = QVBoxLayout()
        self.welcome_layout.addWidget(self.welcome_label)
        self.welcome_layout.addWidget(self.instructions_container)  # Add the container instead of the label
        self.welcome_layout.addWidget(self.proceed_button, alignment=QtCore.Qt.AlignCenter)
        self.welcome_widget.setLayout(self.welcome_layout)
        
        self.setCentralWidget(self.welcome_widget)

    def setQuestionScreen(self):
        """
        Sets up the question screen
        """
        self.sentence = QtWidgets.QLabel()
        self.sentence.setFont(fontTitle)
        
        self.createButtons()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.sentence, alignment=QtCore.Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.option1)
        button_layout.addWidget(self.option2)
        self.layout.addLayout(button_layout)

        self.layout.addWidget(self.confirm, alignment=QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.widget)
        self.updateText()

    def createButtons(self):
        """
        Creates the different buttons
        """
        # Create the buttons for the options
        self.option1 = QtWidgets.QPushButton(self)
        self.option1.clicked.connect(self.clickedOption1)
        self.option1Clicked = False
        self.option1.setFont(fontButtons)
        self.option2 = QtWidgets.QPushButton(self)
        self.option2.clicked.connect(self.clickedOption2)
        self.option2Clicked = False
        self.option2.setFont(fontButtons)

        # Apply style
        self.option1.setStyleSheet(buttonStyleOff)
        self.option2.setStyleSheet(buttonStyleOff)

        # confirm button
        self.confirm = QtWidgets.QPushButton(self)
        self.confirm.clicked.connect(self.confirmed)
        self.confirm.setText("I confirm my choice.")
        self.confirm.setStyleSheet(buttonProceed)
        self.confirm.setFont(fontProceed)

    def setCodeDirectory(self, code, directory):
        """
        Sets the values for the directory and the code
        :param code: the code of the user
        :param directory: directory to save the results in
        """
        self.code = code
        self.directory = directory
        self.model.setDirectoryFileName(directory, code)

    def updateTextButtons(self):
        """
        Updates the text and the buttons
        """
        self.sentence.adjustSize()
        self.option1.adjustSize()
        self.option2.adjustSize()

    def updateText(self):
        """
        Updates the different texts
        """
        self.sentence.setText(experiment_text["sentence_string"].format(
            f"{self.model.getSimAnswers().shape[0]:.0f}"
        ))
        lottery_text = experiment_text["sentence_lottery"].format(
            f"{experiment_text['amount_currency']}{shared_info['x']}",
            f"{self.proba * 100:.0f}%",
            f"{experiment_text['amount_currency']}{shared_info['y']}"
        )
        sure_amount_text = experiment_text["sentence_sure"].format(
            f"{experiment_text['amount_currency']}{self.sure_amount:.2f}".rstrip('0').rstrip('.')
        )
        sentences = [lottery_text, sure_amount_text]
        self.question_order = random.sample([0, 1], 2)
        self.option1.setText(sentences[self.question_order[0]])
        self.option2.setText(sentences[self.question_order[1]])
        self.updateTextButtons()

    def toggleOption1(self):
        """
        Toggles the state of the button for the 1st option
        """
        self.option1Clicked = (self.option1Clicked + 1) % 2

    def toggleOption2(self):
        """
        Toggles the state of the button for the 2nd option
        """
        self.option2Clicked = (self.option2Clicked + 1) % 2

    def resetButtons(self):
        """
        Resets the states of the 2 option buttons
        :return:
        """
        self.option1Clicked = False
        self.option2Clicked = False
        self.option1.setStyleSheet(buttonStyleOff)
        self.option2.setStyleSheet(buttonStyleOff)

    def clickedOption1(self):
        """
        Handles the states of the buttons when button 1 is clicked on
        """
        self.toggleOption1()
        if self.option1Clicked: # if should be clicked now
            self.option1.setStyleSheet(buttonStyleOn)
            if self.option2Clicked:
                self.toggleOption2()
                self.option2.setStyleSheet(buttonStyleOff)
        else: # if was already clicked before
            self.option1.setStyleSheet(buttonStyleOff)

    def clickedOption2(self):
        """
        Handles the states of the buttons when button 2 is clicked on
        """
        self.toggleOption2()
        if self.option2Clicked: # if should be clicked now
            self.option2.setStyleSheet(buttonStyleOn)
            if self.option1Clicked:
                self.toggleOption1()
                self.option1.setStyleSheet(buttonStyleOff)
        else: # if was already clicked before
            self.option2.setStyleSheet(buttonStyleOff)

    def confirmed(self):
        """
        Handles the states when the choice has been confirmed
        """
        if self.option2Clicked or self.option1Clicked: # don't do anything if no option has been clicked
            if self.option1Clicked:
                self.sure_amount, self.proba = self.model.calculate(self.question_order[0])
            else:
                self.sure_amount, self.proba = self.model.calculate(self.question_order[1])
            self.updateText()
            self.updateTextButtons()
            self.resetButtons()
            self.model.saveSimAnswers()
            if not self.model.getEpsilon() > 0.1:
                self.finished()

    def finished(self):
        """
        Cleans the main window and shows end message
        """
        centralWidget = self.centralWidget()
        if centralWidget is not None:
            centralWidget.deleteLater()
        self.messageFinished = QtWidgets.QLabel("The experiment is over, thank you for your help !")
        self.messageFinished.setAlignment(QtCore.Qt.AlignCenter)
        self.messageFinished.setFont(QFont("Arial", 20))
        messageLayout = QVBoxLayout()
        messageLayout.addWidget(self.messageFinished)
        messageWidget = QWidget()
        messageWidget.setLayout(messageLayout)
        self.setCentralWidget(messageWidget)
        print(self.model.getSimAnswers())

def __main__():
    app = QApplication(sys.argv) # always start with
    win = MyWindow()
    win.setCodeDirectory(new_file_name, results_folder)
    win.show()
    # win.showFullScreen()
    sys.exit(app.exec_())

__main__()
