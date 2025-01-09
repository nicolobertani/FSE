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
    Responsible of handling the view of the main window. 
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
        self.instructions_label = QtWidgets.QLabel(experiment_text["instructions"])
        self.instructions_label.setFont(instructions_font)
        self.instructions_label.setAlignment(QtCore.Qt.AlignLeft)
        
        # Create a container widget for the instructions label
        self.instructions_container = QWidget()
        self.instructions_container.setStyleSheet(instructionStyle)
        self.instructions_layout = QVBoxLayout()
        self.instructions_layout.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.instructions_layout.addWidget(self.instructions_label)
        self.instructions_container.setLayout(self.instructions_layout)
        
        # Create the proceed button
        self.proceed_button = QtWidgets.QPushButton("Proceed")
        self.proceed_button.setFont(fontProceed)
        self.proceed_button.setStyleSheet(buttonProceed)  # Apply the buttonProceed style
        self.proceed_button.clicked.connect(self.setPracticeQuestionScreen)
        
        # Set up the layout for the welcome screen
        self.welcome_widget = QWidget()
        self.welcome_layout = QVBoxLayout()
        self.welcome_layout.addWidget(self.welcome_label)
        self.welcome_layout.addWidget(self.instructions_container)  # Add the container instead of the label
        self.welcome_layout.addWidget(self.proceed_button, alignment=QtCore.Qt.AlignCenter)
        self.welcome_widget.setLayout(self.welcome_layout)
        
        self.setCentralWidget(self.welcome_widget)

    def setPracticeQuestionScreen(self):
        """
        Sets up the practice question screen with the same structure as the question screen,
        but the buttons do not interact with the model.
        """
        self.practice_sentence = QtWidgets.QLabel("This is a practice question.")
        self.practice_sentence.setFont(fontTitle)
        self.practice_sentence.setAlignment(QtCore.Qt.AlignCenter)

        # Create the practice buttons
        # Option 1
        lottery_text = experiment_text["sentence_lottery"].format(
            f"{experiment_text['amount_currency']}{shared_info['x']}",
            "60%",
            f"{experiment_text['amount_currency']}{shared_info['y']}",
            "40%",
        )
        self.option1 = QtWidgets.QPushButton(lottery_text)
        self.option1.setFont(fontButtons)
        self.option1.setStyleSheet(buttonStyleOff)
        self.option1.clicked.connect(self.clickedOption1)
        self.option1Clicked = False

        # Option 2
        sure_amount_text = experiment_text["sentence_sure"].format(
            f"{experiment_text['amount_currency']}{"50"}"
        )
        self.option2 = QtWidgets.QPushButton(sure_amount_text)
        self.option2.setFont(fontButtons)
        self.option2.setStyleSheet(buttonStyleOff)
        self.option2.clicked.connect(self.clickedOption2)
        self.option2Clicked = False

        # Confirm button
        self.practice_confirm = QtWidgets.QPushButton(experiment_text["confirm"])
        self.practice_confirm.setFont(fontProceed)
        self.practice_confirm.setStyleSheet(buttonProceed)
        self.practice_confirm.clicked.connect(self.confirmedPractice)

        # Set up the layout for the practice question screen
        self.practice_widget = QWidget()
        self.practice_layout = QVBoxLayout()
        self.practice_widget.setLayout(self.practice_layout)
        self.practice_layout.addWidget(self.practice_sentence, alignment=QtCore.Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.option1)
        button_layout.addWidget(self.option2)
        self.practice_layout.addLayout(button_layout)

        self.practice_layout.addWidget(self.practice_confirm, alignment=QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.practice_widget)

    def confirmedPractice(self):
        if self.option2Clicked or self.option1Clicked:
            self.setComprehensionScreen()

    def setComprehensionScreen(self):
        """
        Sets up the comprehension screen.
        """
        self.comprehension_label = QtWidgets.QLabel("Comprehension question")
        self.comprehension_label.setFont(fontTitle)
        self.comprehension_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create the instructions label for the comprehension screen
        self.comprehension_instructions_label = QtWidgets.QLabel("Please read the instructions carefully and answer the question below.")
        self.comprehension_instructions_label.setFont(instructions_font)
        self.comprehension_instructions_label.setAlignment(QtCore.Qt.AlignLeft)

        # Create a container widget for the comprehension instructions label
        self.comprehension_instructions_container = QWidget()
        self.comprehension_instructions_container.setStyleSheet(instructionStyle)
        self.comprehension_instructions_layout = QVBoxLayout()
        self.comprehension_instructions_layout.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.comprehension_instructions_layout.addWidget(self.comprehension_instructions_label)
        self.comprehension_instructions_container.setLayout(self.comprehension_instructions_layout)

        # Create the multiple-option question
        self.question_label = QtWidgets.QLabel("What is the capital of France?")
        self.question_label.setFont(fontButtons)
        self.question_label.setAlignment(QtCore.Qt.AlignCenter)

        self.option_group = QtWidgets.QButtonGroup(self)
        self.option1 = QtWidgets.QRadioButton("Paris")
        self.option2 = QtWidgets.QRadioButton("London")
        self.option3 = QtWidgets.QRadioButton("Berlin")

        self.option_group.addButton(self.option1)
        self.option_group.addButton(self.option2)
        self.option_group.addButton(self.option3)

        # Create a vertical layout for the question and options
        self.options_layout = QVBoxLayout()
        self.options_layout.addWidget(self.question_label, alignment=QtCore.Qt.AlignCenter)
        self.options_layout.addWidget(self.option1)
        self.options_layout.addWidget(self.option2)
        self.options_layout.addWidget(self.option3)

        # Create a container widget for the options layout
        self.options_container = QWidget()
        self.options_container.setLayout(self.options_layout)
        self.options_container.setStyleSheet("background-color: white; border: 1px solid darkgrey; padding: 10px; border-radius: 10px;")

        # Create the proceed button for the comprehension screen
        self.proceed_to_exp = QtWidgets.QPushButton("Proceed")
        self.proceed_to_exp.setFont(fontProceed)
        self.proceed_to_exp.setStyleSheet(buttonProceed)
        self.proceed_to_exp.clicked.connect(self.setProceedToExpScreen)

        # Set up the layout for the comprehension screen
        self.comprehension_widget = QWidget()
        self.comprehension_layout = QVBoxLayout()
        self.comprehension_widget.setLayout(self.comprehension_layout)
        self.comprehension_layout.addWidget(self.comprehension_label, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.comprehension_instructions_container)
        self.comprehension_layout.addWidget(self.question_label, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.options_container, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.proceed_to_exp, alignment=QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.comprehension_widget)

    def setProceedToExpScreen(self):
        """
        This screen introduces the experiment
        """
        self.practice_label = QtWidgets.QLabel("The experiment is about to start!")
        self.practice_label.setFont(fontTitle)
        self.practice_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create the instructions label for the practice question screen
        self.practice_instructions_label = QtWidgets.QLabel(experiment_text["instructions_reminder"])
        self.practice_instructions_label.setFont(instructions_font)
        self.practice_instructions_label.setAlignment(QtCore.Qt.AlignLeft)

        # Create a container widget for the practice instructions label
        self.practice_instructions_container = QWidget()
        self.practice_instructions_container.setStyleSheet(instructionStyle)
        self.practice_instructions_layout = QVBoxLayout()
        self.practice_instructions_layout.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.practice_instructions_layout.addWidget(self.practice_instructions_label)
        self.practice_instructions_container.setLayout(self.practice_instructions_layout)

        # Create the proceed button for the practice question screen
        self.proceed_to_exp = QtWidgets.QPushButton("Proceed to Experiment")
        self.proceed_to_exp.setFont(fontProceed)
        self.proceed_to_exp.setStyleSheet(buttonProceed)
        self.proceed_to_exp.clicked.connect(self.setQuestionScreen)

        # Set up the layout for the practice question screen
        self.practice_widget = QWidget()
        self.practice_layout = QVBoxLayout()
        self.practice_widget.setLayout(self.practice_layout)
        self.practice_layout.addWidget(self.practice_label, alignment=QtCore.Qt.AlignCenter)
        self.practice_layout.addWidget(self.practice_instructions_container)  # Add the container
        self.practice_layout.addWidget(self.proceed_to_exp, alignment=QtCore.Qt.AlignCenter)
        self.practice_widget.setLayout(self.practice_layout)

        self.setCentralWidget(self.practice_widget)

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
        self.confirm.setText(experiment_text["confirm"])
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
            f"{experiment_text['amount_currency']}{shared_info['y']}",
            f"{(1 - self.proba) * 100:.0f}%",
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
        self.messageFinished = QtWidgets.QLabel(experiment_text["final_message"])
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
