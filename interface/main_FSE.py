import sys
import os
import re

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
filtered_files = [f for f in result_files if re.match(r'^FSE_\d{4}\.csv$', f)]
numeric_parts = [re.search(r'\d{4}', f).group() for f in filtered_files]
max_numeric_part = max(map(int, numeric_parts)) if numeric_parts else 0
new_file_name = f"{experimental_design}_{max_numeric_part + 1:04d}.csv"

# import the necessary libraries
from backend.model_interface import Model
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QLabel, QFileDialog, QHBoxLayout
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

class CodeEntryWindow(QMainWindow):
    """
    This first window is responsible for asking a 4-digit code to the user. The code is checked for two things:
     - the code is really made out of 4 digit
     - the code has not been used yet in the same directory.
     The researcher can choose if the user can choose the directory or if the .csv file is saved in the default
        directory (same as the program)
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initiates the different components of the first window
        """
        self.askDir = False # change if prefer to have default directory
        self.directory = os.getcwd()
        self.initWindow()
        self.initLabel()

    def initWindow(self):
        """
        Initiates the components of the window
        """
        self.setWindowTitle('Code Entry')
        self.setGeometry(100, 100, 400, 200)
        self.font = QFont()
        self.font.setPointSize(25)

    def initButton(self):
        """
        Initiates the components of the button
        """
        self.button = QPushButton('Enter Code', self)
        self.button.setGeometry(150, 80, 100, 30)
        self.buttonStyle = """
            QPushButton {
            background-color: white;
            border: none;
            border-radius: 10px;
            padding: 10px;
        }
        """
        fontButtons = QFont()
        fontButtons.setPointSize(15)
        self.button.setFont(fontButtons)
        self.button.setStyleSheet(self.buttonStyle)
        self.button.clicked.connect(self.checkCode)

    def initLabel(self):
        """
        Initiates the components of the box in which you can write the 4-digit code
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.label = QLabel('Please enter a 4-digit code:', self)
        self.label.setFont(self.font)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)  # Center the label horizontally
        self.input_field = QLineEdit(self)
        self.input_field.setFont(self.font)
        layout.addWidget(self.input_field, alignment=Qt.AlignmentFlag.AlignHCenter)  # Center the input field horizontally
        self.initButton()
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignHCenter)  # Center the button horizontally

    def checkFileExists(self):
        """
        Checks that the file does not already exist in the chosen directory
        :return:
            boolean indicating if the file already exists or not
        """
        return os.path.exists(os.path.join(self.directory, self.code + ".csv"))

    def checkCode(self):
        """
        Checks that the code is correct:
            - correct format
            - does not exist already
        """
        self.code = self.input_field.text()
        if len(self.code) == 4 and self.code.isdigit():
            if self.askDir:
                self.directory = QFileDialog.getExistingDirectory(self, "Choose Directory", os.path.expanduser("~"))

            if self.checkFileExists():
                QMessageBox.warning(self, 'Invalid Code', 'This code already exists')

            else:
                self.close()
                self.openSecondWindow()
        else:
            QMessageBox.warning(self, 'Invalid Code', 'Invalid code format. Please enter a 4-digit numeric code.')

    def openSecondWindow(self):
        """
        Opens the second window
        """
        self.main_window = MyWindow()
        self.main_window.setCodeDirectory(self.code, self.directory)
        self.main_window.show()


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
        self.width = 600
        self.height = 600

        # initial values, may be changed for other applications
        self.sure_amount = 65.0
        self.lottery_1 = 10
        self.lottery_2 = 120
        self.proba = 90.0

        self.amount_currency = "£"  # Define the currency here

        self.code = None
        self.directory = None
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)
        self.setWindowTitle("Lottery Check")
        self.model = Model()
        self.sentence_string = "Do you prefer to win for sure <b>{} </b> or play the lottery and win <b>{} </b> with <b>{}% probabilities </b> or <b>{} </b> if you lose the lottery"
        self.initUI()

    def initUI(self):
        """
        Initializes all the UI elements
        """
        font = QFont()
        font.setPointSize(25)
        # Set the new font on the label
        self.sentence = QtWidgets.QLabel()
        self.sentence.setFont(font)
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
        self.buttonStyleOff = """
            QPushButton {
            background-color: white;
            border: none;
            border-radius: 10px;
            padding: 20px; /* Increased padding for larger buttons */
        }
        """

        self.buttonStyleOn = """
            QPushButton {
            background-color: grey;
            border: none;
            border-radius: 10px;
            padding: 20px; /* Increased padding for larger buttons */
        }
        """
        fontButtons = QFont()
        fontButtons.setPointSize(18)  # Increased font size

        self.option1 = QtWidgets.QPushButton(self)
        self.option1.clicked.connect(self.clickedOption1)
        self.option1Clicked = False
        self.option1.setFont(fontButtons)
        self.option2 = QtWidgets.QPushButton(self)
        self.option2.clicked.connect(self.clickedOption2)
        self.option2Clicked = False
        self.option2.setFont(fontButtons)

        self.option1.setStyleSheet(self.buttonStyleOff)
        self.option2.setStyleSheet(self.buttonStyleOff)

        self.confirm = QtWidgets.QPushButton(self)
        self.confirm.clicked.connect(self.confirmed)
        self.confirm.setText("Confirm choice")
        self.confirm.setStyleSheet(self.buttonStyleOff)
        self.confirm.setFont(fontButtons)

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
        x5 = 100 - int(self.proba)
        self.sentence.setText(self.sentence_string.format(
            f"{self.amount_currency}{self.sure_amount}", 
            f"{self.amount_currency}{self.lottery_1}", 
            self.proba, 
            f"{self.amount_currency}{self.lottery_2}"
        ))
        self.option1.setText(f"Win <b>{self.amount_currency}{self.sure_amount}</b>")
        self.option2.setText(f"Win <b>{self.amount_currency}{self.lottery_1}</b> with <b>{self.proba}%</b> probabilities or <b>{self.amount_currency}{self.lottery_2}</b> with <b>{x5}%</b> probabilities")
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
        self.option1.setStyleSheet(self.buttonStyleOff)
        self.option2.setStyleSheet(self.buttonStyleOff)

    def clickedOption1(self):
        """
        Handles the states of the buttons when button 1 is clicked on
        """
        self.toggleOption1()
        if self.option1Clicked: # if should be clicked now
            self.option1.setStyleSheet(self.buttonStyleOn)
            if self.option2Clicked:
                self.toggleOption2()
                self.option2.setStyleSheet(self.buttonStyleOff)
        else: # if was already clicked before
            self.option1.setStyleSheet(self.buttonStyleOff)

    def clickedOption2(self):
        """
        Handles the states of the buttons when button 2 is clicked on
        """
        self.toggleOption2()
        if self.option2Clicked: # if should be clicked now
            self.option2.setStyleSheet(self.buttonStyleOn)
            if self.option1Clicked:
                self.toggleOption1()
                self.option1.setStyleSheet(self.buttonStyleOff)
        else: # if was already clicked before
            self.option2.setStyleSheet(self.buttonStyleOff)

    def confirmed(self):
        """
        Handles the states when the choice has been confirmed
        """
        if self.option2Clicked or self.option1Clicked:
            if self.option1Clicked:
                self.sure_amount, self.proba = self.model.calculate(1)
            else:
                self.sure_amount, self.proba = self.model.calculate(0)
            self.sure_amount = round(float(self.sure_amount),2)
            self.proba = round(float(self.proba) * 100,0)
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




def window():
    app = QApplication(sys.argv) # always start with
    win = CodeEntryWindow()
    win.showFullScreen()
    sys.exit(app.exec_())



window()
