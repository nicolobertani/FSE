import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.xpos = 0
        self.ypos = 0
        self.width = 600
        self.height = 600
        self.lottery = []
        self.questionCount = 0
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)
        self.setWindowTitle("Lottery Check")
        self.createLotteryChoices()
        self.createCharts()
        self.initUI()

    def createCharts(self):
        x1, x2, x3, x4 = self.lottery[self.questionCount]
        self.series1 = QPieSeries()
        self.series1.append("{}".format(x1), 100)
        self.chart1 = QChart()
        self.chart1.addSeries(self.series1)
        self.chart1.setTitle("Option 1")
        self.chart1.setTitleFont(QFont("Arial", 16))

        self.series2 = QPieSeries()
        self.series2.append("{}".format(x2), x3)
        self.series2.append("{}".format(x4), 100-x3)
        self.chart2 = QChart()
        self.chart2.addSeries(self.series2)
        self.chart2.setTitle("Option 2")
        self.chart2.setTitleFont(QFont("Arial", 16))


    def updateCharts(self):
        print(self.questionCount)
        x1, x2, x3, x4 = self.lottery[self.questionCount]
        self.series1.clear()
        self.series1.append("{}".format(x1), 100)

        self.series2.clear()
        self.series2.append("{}".format(x2), x3)
        self.series2.append("{}".format(x4), 100-x3)

        # update the chart views
        self.chart1.update()
        self.chart2.update()

    def initUI(self):
        self.sentence = QtWidgets.QLabel()
        self.option1 = QtWidgets.QPushButton(self)
        self.option1.clicked.connect(self.clickedOption1)
        self.option2 = QtWidgets.QPushButton(self)
        self.option2.clicked.connect(self.clickedOption2)
        #self.result = QtWidgets.QLabel(self)
        #self.result.setText("No result yet")


        self.widget = QWidget()
        self.layout = QGridLayout()
        self.widget.setLayout(self.layout)
        self.layout.addWidget(self.sentence, 0, 0, 1, 3, QtCore.Qt.AlignCenter)
        self.layout.addWidget(QChartView(self.chart1), 1, 0)
        self.layout.addWidget(QChartView(self.chart2), 1, 2)
        self.layout.addWidget(self.option1, 2, 0)
        self.layout.addWidget(self.option2, 2, 2)
        #self.layout.addWidget(self.result, 3, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 3)
        self.layout.setRowStretch(2, 3)
        #self.layout.setRowStretch(3, 1)
        self.setCentralWidget(self.widget)
        self.updateText()





    def updateText(self):
        x1, x2, x3, x4 = self.lottery[self.questionCount]
        x5 = 100 - int(x3)
        self.sentence.setText(self.sentence_string.format(x1, x2, x3, x4))
        self.option1.setText('Win {}'.format(x1))
        self.option2.setText('Win {} with {}% chances or {} with {}% chances '.format(x2, x3, x4,str(x5)))
        self.update()


    def clickedOption1(self):
        self.updateText()
        #self.result.setText("You chose the first option")
        self.update()
        self.updateCharts()
        if self.questionCount <= 11:
            self.questionCount += 1

    def clickedOption2(self):
        self.updateText()
        #self.result.setText("You chose the second option")
        self.update()
        self.updateCharts()
        if self.questionCount <= 11:
            self.questionCount += 1

    def update(self):
        self.sentence.adjustSize()
        #self.result.adjustSize()
        self.option1.adjustSize()
        self.option2.adjustSize()

    def createLotteryChoices(self):
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

        self.sentence_string = "Do you prefer to win for sure {} or play the lottery and win {} with {}% chances or {} if you lose the lottery"
        self.lottery = [choice1, choice2, choice3, choice4, choice5, choice6, choice6, choice7, choice8, choice8, choice9, choice10, choice11, choice12, choice13]




def window():
    app = QApplication(sys.argv) # always start with
    win = MyWindow()
    win.showFullScreen()
    sys.exit(app.exec_())



window()