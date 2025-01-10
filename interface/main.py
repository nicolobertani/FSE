import sys
import os
import re
import random
import datetime
import json
import pandas as pd


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
filtered_files = [f for f in result_files if re.match(rf'^{experimental_design}_\d{{4}}\.json$', f)]
numeric_parts = [re.search(r'\d{4}', f).group() for f in filtered_files]
max_numeric_part = max(map(int, numeric_parts)) if numeric_parts else 0
new_file_name = f"{experimental_design}_{max_numeric_part + 1:04d}"

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtWidgets
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

        # Initialize the model and the first question
        self.model = FSE(set_z=shared_info["set_z"])
        self.sure_amount = self.model.get_train_answers().iloc[-1]['z']
        self.proba = self.model.get_train_answers().iloc[-1]['p_x']
        
        # Set timer
        self.timestamps = pd.DataFrame(
            dict(zip(['step', 'timestamp'], [['started'], [datetime.datetime.now()]]))
        )
        self.comprehension_results = None
        self.saveProgress()

        # Initialize the UI
        self.initUI()
        
    def saveProgress(self):
        # Save timestamps and model answers to a JSON file
        results = {
            "timestamps": self.timestamps.to_dict(orient='records'),
            "comprehension_results": self.comprehension_results,
            "train_answers": self.model.get_train_answers().dropna(subset=['s']).to_dict(orient='records'),
            "test_answers": self.model.get_test_answers().dropna(subset=['s']).to_dict(orient='records')
        }
        with open(os.path.join(results_folder, f"{new_file_name}.json"), 'w') as f:
            json.dump(results, f, indent=4, default=str)

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
        # Set the timer
        self.timestamps = pd.concat(
            [self.timestamps, 
             pd.DataFrame([{'step': 'practice_question', 'timestamp': datetime.datetime.now()}])], 
             ignore_index=True)
        self.saveProgress()

        # Create the practice sentence
        self.practice_sentence = QtWidgets.QLabel("This is a practice question.")
        self.practice_sentence.setFont(fontTitle)
        self.practice_sentence.setAlignment(QtCore.Qt.AlignCenter)

        # Create the practice buttons
        # Option 1
        self.practice_lottery_text = experiment_text["sentence_lottery"].format(
            f"{experiment_text['amount_currency']}{shared_info['x']}",
            f"{shared_info['practice_p'] * 100:.0f}%",
            f"{experiment_text['amount_currency']}{shared_info['y']}",
            f"{(1 - shared_info['practice_p']) * 100:.0f}%",
        )
        self.option1 = QtWidgets.QPushButton(self.practice_lottery_text)
        self.option1.setFont(fontButtons)
        self.option1.setStyleSheet(buttonStyleOff)
        self.option1.clicked.connect(self.clickedOption1)
        self.option1Clicked = False

        # Option 2
        self.practice_sure_text = experiment_text["sentence_sure"].format(
            f"{experiment_text['amount_currency']}{shared_info["practice_z"]:.2f}".rstrip('0').rstrip('.')
        )
        self.option2 = QtWidgets.QPushButton(self.practice_sure_text)
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
        else:
            QtWidgets.QMessageBox.warning(self, "Incomplete", "Please select an option before confirming.")

    def setComprehensionScreen(self):
        """
        Sets up the comprehension screen.
        """
        # Set the timer
        self.timestamps = pd.concat(
            [self.timestamps, 
             pd.DataFrame([{'step': 'comprehension_question', 'timestamp': datetime.datetime.now()}])], 
             ignore_index=True)
        self.saveProgress()

        self.comprehension_label = QtWidgets.QLabel("Comprehension questions")
        self.comprehension_label.setFont(fontTitle)
        self.comprehension_label.setAlignment(QtCore.Qt.AlignCenter)

        # Create the instructions label for the comprehension screen
        self.comprehension_instructions_label = QtWidgets.QLabel(experiment_text['comp_instructions'])
        self.comprehension_instructions_label.setFont(instructions_font)
        self.comprehension_instructions_label.setAlignment(QtCore.Qt.AlignLeft)

        # Create a container widget for the comprehension instructions label
        self.comprehension_instructions_layout = QVBoxLayout()
        self.comprehension_instructions_layout.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.comprehension_instructions_layout.addWidget(self.comprehension_instructions_label)
        self.comprehension_instructions_container = QWidget()
        self.comprehension_instructions_container.setStyleSheet(instructionStyle)
        self.comprehension_instructions_container.setLayout(self.comprehension_instructions_layout)

        # Comprehension question 1
        self.q1_container = QVBoxLayout()
        self.q1_container.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.q1_container.setSpacing(10)  # Add spacing between elements
        self.q1_container_wgt = QWidget()
        self.q1_container_wgt.setStyleSheet(instructionStyle)
        self.q1_container_wgt.setLayout(self.q1_container)

        self.q1_label = QtWidgets.QLabel(experiment_text["comp_q1"].format(self.practice_lottery_text.rstrip('.').replace('\n', ' ')))
        self.q1_label.setFont(instructions_font)
        self.q1_label.setAlignment(QtCore.Qt.AlignLeft)

        ## Create the options for the first comprehension question
        self.q1_answers = QtWidgets.QButtonGroup(self)
        self.q1_opt1 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['x']}")
        self.q1_opt2 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['practice_z']}")
        self.q1_opt3 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['y']}")
        for opt in [self.q1_opt1, self.q1_opt2, self.q1_opt3]:
            opt.setFont(instructions_font)

        self.q1_answers.addButton(self.q1_opt1)
        self.q1_answers.addButton(self.q1_opt2)
        self.q1_answers.addButton(self.q1_opt3)

        ## Create a horizontal layout for the options
        self.q1_opt_layout = QHBoxLayout()
        self.q1_opt_layout.addWidget(self.q1_opt1)
        self.q1_opt_layout.addWidget(self.q1_opt2)
        self.q1_opt_layout.addWidget(self.q1_opt3)

        ## Create a container widget for the options layout
        self.q1_opt_container = QWidget()
        self.q1_opt_container.setLayout(self.q1_opt_layout)
        self.q1_opt_container.setStyleSheet("background-color: white; border: 1px solid darkgrey; padding: 10px; border-radius: 10px;")

        self.q1_container.addWidget(self.q1_label, alignment=QtCore.Qt.AlignLeft)
        self.q1_container.addWidget(self.q1_opt_container, alignment=QtCore.Qt.AlignCenter)

        # Comprehension question 2
        self.q2_container = QVBoxLayout()
        self.q2_container.setContentsMargins(30, 30, 30, 30)  # Add padding
        self.q2_container.setSpacing(10)  # Add spacing between elements
        self.q2_container_wgt = QWidget()
        self.q2_container_wgt.setLayout(self.q2_container)
        self.q2_container_wgt.setStyleSheet("background-color: white; padding: 10px; border-radius: 10px;")
        self.q2_container_wgt.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.q2_label = QtWidgets.QLabel(experiment_text["comp_q2"].format(self.practice_sure_text.rstrip('.').replace('\n', ' ')))
        self.q2_label.setFont(fontButtons)
        self.q2_label.setAlignment(QtCore.Qt.AlignLeft)

        ## Create the options for the second comprehension question
        self.q2_answers = QtWidgets.QButtonGroup(self)
        self.q2_opt1 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['x']}")
        self.q2_opt2 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['practice_z']}")
        self.q2_opt3 = QtWidgets.QRadioButton(f"{experiment_text['amount_currency']}{shared_info['y']}")
        for opt in [self.q2_opt1, self.q2_opt2, self.q2_opt3]:
            opt.setFont(instructions_font)

        self.q2_answers.addButton(self.q2_opt1)
        self.q2_answers.addButton(self.q2_opt2)
        self.q2_answers.addButton(self.q2_opt3)

        ## Create a horizontal layout for the options
        self.q2_opt_layout = QHBoxLayout()
        self.q2_opt_layout.addWidget(self.q2_opt1)
        self.q2_opt_layout.addWidget(self.q2_opt2)
        self.q2_opt_layout.addWidget(self.q2_opt3)

        ## Create a container widget for the options layout
        self.q2_opt_container = QWidget()
        self.q2_opt_container.setLayout(self.q2_opt_layout)
        self.q2_opt_container.setStyleSheet("background-color: white; border: 1px solid darkgrey; padding: 10px; border-radius: 10px;")

        self.q2_container.addWidget(self.q2_label, alignment=QtCore.Qt.AlignLeft)
        self.q2_container.addWidget(self.q2_opt_container, alignment=QtCore.Qt.AlignCenter)

        # Create the proceed button for the comprehension screen
        self.proceed_to_exp = QtWidgets.QPushButton("Proceed")
        self.proceed_to_exp.setFont(fontProceed)
        self.proceed_to_exp.setStyleSheet(buttonProceed)
        self.proceed_to_exp.clicked.connect(self.checkComprehensionAnswers)

        # Set up the layout for the comprehension screen
        self.comprehension_layout = QVBoxLayout()
        self.comprehension_layout.addWidget(self.comprehension_label, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.comprehension_instructions_container)
        self.comprehension_layout.addWidget(self.q1_container_wgt, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.q2_container_wgt, alignment=QtCore.Qt.AlignCenter)
        self.comprehension_layout.addWidget(self.proceed_to_exp, alignment=QtCore.Qt.AlignCenter)

        self.comprehension_widget = QWidget()
        self.comprehension_widget.setLayout(self.comprehension_layout)
        self.setCentralWidget(self.comprehension_widget)

    def checkComprehensionAnswers(self):
        selected_q1 = self.q1_answers.checkedButton()
        selected_q2 = self.q2_answers.checkedButton()

        if selected_q1 is None or selected_q2 is None:
            QtWidgets.QMessageBox.warning(self, "Incomplete", "Please answer all comprehension questions before proceeding.")
        else:
            self.comprehension_results = {
                "q1": selected_q1.text(),
                "q2": selected_q2.text()
            }
            self.setProceedToExpScreen()

    def setProceedToExpScreen(self):
        """
        This screen introduces the experiment
        """
        # Set the timer
        self.timestamps = pd.concat(
            [self.timestamps, 
             pd.DataFrame([{'step': 'proceed_to_exp', 'timestamp': datetime.datetime.now()}])], 
             ignore_index=True)
        self.saveProgress()

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
        # Set the timer
        self.timestamps = pd.concat(
            [self.timestamps, 
             pd.DataFrame([{'step': 'start_exp', 'timestamp': datetime.datetime.now()}])], 
             ignore_index=True)
        self.saveProgress()

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
        question_number = self.model.get_train_answers().shape[0] + self.model.get_test_answers().shape[0]
        self.sentence.setText(experiment_text["sentence_string"].format(
            f"{question_number:.0f}"
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
                self.sure_amount, self.proba = self.model.next_question(self.question_order[0])
            else:
                self.sure_amount, self.proba = self.model.next_question(self.question_order[1])

            self.updateText()
            self.updateTextButtons()
            self.resetButtons()
            self.saveProgress()

            if (not self.model.getEpsilon() > 0.1) and (self.model.get_test_iteration() == shared_info['number_test']):
                self.finished()
        
        else:
            QtWidgets.QMessageBox.warning(self, "Incomplete", "Please select an option before confirming.")


    def finished(self):
        """
        Cleans the main window and shows end message
        """
        # Set the timer
        self.timestamps = pd.concat(
            [self.timestamps, 
             pd.DataFrame([{'step': 'done', 'timestamp': datetime.datetime.now()}])], 
             ignore_index=True)

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
        self.saveProgress()
        QtCore.QTimer.singleShot(5000, self.close)
    
def __main__():
    app = QApplication(sys.argv) # always start with
    win = MyWindow()
    win.show()
    # win.showFullScreen()
    sys.exit(app.exec_())

__main__()
