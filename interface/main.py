import sys
from backend.model_interface import Model
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


class MyWindow(QMainWindow):
    def __init__(self):
        """
        initialize the main window
        """
        super(MyWindow, self).__init__()
        # adding Folder_2 to the system path
        sys.path.insert(0, '/Users/mathieuleng/PycharmProjects/FSE/backend')
        self.iteration = 0
        self.xpos = 0
        self.ypos = 0
        self.width = 600
        self.height = 600
        self.sure_amount = 65.0
        self.lottery_1 = 10
        self.lottery_2 = 120
        self.proba = 90.0
        self.lottery = []
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)
        self.setWindowTitle("Lottery Check")
        self.model = Model()
        self.sentence_string = "Do you prefer to win for sure <b>{} </b> or play the lottery and win <b>{} </b> with <b>{}% probabilities </b> or <b>{} </b> if you lose the lottery"
        self.createCharts()
        self.initUI()

    def createCharts(self):
        """
        create the 2 charts
        :return:
        """
        #x1, x2, x3, x4 = self.lottery[self.questionCount]
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


    def updateCharts(self):
        """
        updates the charts
        :return:
        """
        self.series1.clear()
        self.series1.append("{}".format(self.sure_amount), 100)

        self.series2.clear()
        self.series2.append("{}".format(self.lottery_1), self.proba)
        self.series2.append("{}".format(self.lottery_2), 100-self.proba)

        # update the chart views
        self.chart1.update()
        self.chart2.update()

    def finished(self):
        """
        cleans the main window and shows end message
        :return:
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
        print(self.model.get_sim_answers())

    def toggleOption1(self):
        """
        toggle the state of the button for the 1st option
        :return:
        """
        self.option1Clicked = (self.option1Clicked + 1) % 2

    def toggleOption2(self):
        """
        toggle the state of the button for the 2nd option
        :return:
        """
        self.option2Clicked = (self.option2Clicked + 1) % 2

    def resetButtons(self):
        """
        reset the states of the 2 option buttons
        :return:
        """
        self.option1Clicked = False
        self.option2Clicked = False
        self.option1.setStyleSheet(self.buttonStyleOff)
        self.option2.setStyleSheet(self.buttonStyleOff)

    def confirmed(self):
        """
        handles the states when the choice has been confirmed
        :return:
        """
        if self.option2Clicked or self.option1Clicked:
            self.iteration += 1
            if self.model.get_epsilon() > 0.1:
                if self.option1Clicked:
                    self.sure_amount, self.proba = self.model.calculate(1)
                    #print("sure_amount")
                else:
                    self.sure_amount, self.proba = self.model.calculate(0)
                    #print("lottery")
                self.sure_amount = round(float(self.sure_amount),2)
                self.proba = round(float(self.proba) * 100,0)
                self.updateText()
                self.update()
                self.updateCharts()
                self.resetButtons()
                #print("s_a", self.sure_amount)
                #print("proba", self.proba)
                self.model.save_sim_answers()

            else:
                self.finished()




    def createButtons(self):
        """
        creates the different buttons
        :return:
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

    def initUI(self):
        """
        initialize all the UI elements
        :return:
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




    def updateText(self):
        """
        updates the different texts
        :return:
        """
        #x1, x2, x3, x4 = self.lottery[self.questionCount]
        x5 = 100 - int(self.proba)
        self.sentence.setText(self.sentence_string.format(self.sure_amount, self.lottery_1, self.proba, self.lottery_2))
        self.option1.setText('Win {}'.format(self.sure_amount))
        self.option2.setText('Win {} with {}% probabilities or {} with {}% probabilities '.format(self.lottery_1, self.proba, self.lottery_2,str(x5)))
        self.update()


    def clickedOption1(self):
        self.toggleOption1()
        if self.option1Clicked:
            self.option1.setStyleSheet(self.buttonStyleOn)
            if self.option2Clicked:
                self.toggleOption2()
                self.option2.setStyleSheet(self.buttonStyleOff)
        else:
            self.option1.setStyleSheet(self.buttonStyleOff)

    def clickedOption2(self):
        self.toggleOption2()
        if self.option2Clicked:
            self.option2.setStyleSheet(self.buttonStyleOn)
            if self.option1Clicked:
                self.toggleOption1()
                self.option1.setStyleSheet(self.buttonStyleOff)
        else:
            self.option2.setStyleSheet(self.buttonStyleOff)

    def update(self):
        self.sentence.adjustSize()
        self.option1.adjustSize()
        self.option2.adjustSize()

    def createLotteryChoices(self): # shouldnt be called anymore
        choice1 = (65, 120, 90, 10)
        choice2 = (65, 120, 10, 10)
        choice3 = (65, 120, 50, 10)
        choice4 = (71.5, 120, 74, 10)
        choice5 = (37.5, 120, 10, 10)
        choice6 = (38.6, 120, 44, 10)
        choice7 = (90.6, 120, 94, 10)
        choice8 = (30.1, 120, 19, 10)
        choice9 = (99.2, 120, 93, 10)
        choice10 = (24.9, 120, 6, 10)
        choice11 = (49.6, 120, 50, 10)
        choice12 = (20.9, 120, 7, 10)
        choice13 = (42.9, 120, 33, 10)

        self.sentence_string = "Do you prefer to win for sure <b>{} </b> or play the lottery and win <b>{} </b> with <b>{}% probabilities </b> or <b>{} </b> if you lose the lottery"
        self.lottery = [choice1, choice2, choice3, choice4, choice5, choice6, choice6, choice7, choice8, choice8, choice9, choice10, choice11, choice12, choice13]




def window():
    app = QApplication(sys.argv) # always start with
    win = MyWindow()
    win.showFullScreen()
    sys.exit(app.exec_())



window()


# @TODO
# check que c'est correct avec les tables