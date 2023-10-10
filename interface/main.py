import sys
import os
from backend.model_interface import Model
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, QMessageBox, QLabel, QFileDialog
from PyQt5.QtChart import QChart, QChartView, QPieSeries
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
    the 2 options for the user, the two charts, 2 buttons to pick one of the two option, and a button to confirm.

    Attributes:
            -xpos, ypos, width, height: different attributes for the UI, see PyQt documentation
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
        sys.path.insert(0, '/Users/mathieuleng/PycharmProjects/FSE/backend') # needs no be changed on other machines, needed for the import of packages
        self.xpos = 0
        self.ypos = 0
        self.width = 600
        self.height = 600

        # initial values, may be chnaged for other applications
        self.sure_amount = 65.0
        self.lottery_1 = 10
        self.lottery_2 = 120
        self.proba = 90.0

        self.code = None
        self.directory = None
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)
        self.setWindowTitle("Lottery Check")
        self.model = Model()
        self.sentence_string = "Do you prefer to win for sure <b>{} </b> or play the lottery and win <b>{} </b> with <b>{}% probabilities </b> or <b>{} </b> if you lose the lottery"
        self.createCharts()
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
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.sentence, 0, 0, 1, 3, QtCore.Qt.AlignCenter)
        self.layout.addWidget(QChartView(self.chart1), 2, 0)
        self.layout.addWidget(QChartView(self.chart2), 2, 2)
        self.layout.addWidget(self.option1, 1, 0)
        self.layout.addWidget(self.option2, 1, 2)
        self.layout.addWidget(self.confirm, 3, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 3)
        self.layout.setRowStretch(2, 3)
        self.layout.setRowStretch(3, 1)
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
            padding: 10px;
        }
        """

        self.buttonStyleOn = """
            QPushButton {
            background-color: grey;
            border: none;
            border-radius: 10px;
            padding: 10px;
        }
        """
        fontButtons = QFont()
        fontButtons.setPointSize(15)

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

    def createCharts(self):
        """
        Creates the 2 charts
        """
        self.series1 = QPieSeries()
        self.series1.append("{}".format(self.sure_amount), 100)
        self.chart1 = QChart()
        self.chart1.addSeries(self.series1)
        self.chart1.setTitle("Sure Option")
        self.chart1.setTitleFont(QFont("Arial", 20))

        self.series2 = QPieSeries()
        self.series2.append("{}".format(self.lottery_1), self.proba)
        self.series2.append("{}".format(self.lottery_2), 100-self.proba)
        self.chart2 = QChart()
        self.chart2.addSeries(self.series2)
        self.chart2.setTitle("Lottery")
        self.chart2.setTitleFont(QFont("Arial", 20))

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

    def updateCharts(self):
        """
        Updates the charts
        """
        self.series1.clear()
        self.series1.append("{}".format(self.sure_amount), 100)
        self.series2.clear()
        self.series2.append("{}".format(self.lottery_1), self.proba)
        self.series2.append("{}".format(self.lottery_2), 100-self.proba)

        # update the chart views
        self.chart1.update()
        self.chart2.update()

    def updateText(self):
        """
        Updates the different texts
        """
        x5 = 100 - int(self.proba)
        self.sentence.setText(self.sentence_string.format(self.sure_amount, self.lottery_1, self.proba, self.lottery_2))
        self.option1.setText('Win {}'.format(self.sure_amount))
        self.option2.setText('Win {} with {}% probabilities or {} with {}% probabilities '.format(self.lottery_1, self.proba, self.lottery_2,str(x5)))
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
            self.updateCharts()
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


# @TODO
# check que c'est correct avec les tables

# overwrites work --> shoudlnt
# looks like the last value is not stored because ask one extra question but it is not saved