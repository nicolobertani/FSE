from PyQt5.QtGui import QFont

# text style 
fontTitle = QFont()
fontTitle.setPointSize(25)

# font of all buttons
fontButtons = QFont()
fontButtons.setPointSize(18)
fontButtons.setItalic(True)


# style of the buttons
buttonStyleOff = """
    QPushButton {
    background-color: white;
    border: none;
    border-radius: 10px;
    padding: 60px; /* Increased padding for larger buttons */
}
"""
buttonStyleOn = """
    QPushButton {
    background-color: grey;
    border: none;
    border-radius: 10px;
    padding: 60px; /* Increased padding for larger buttons */
}
"""
buttonProceed = """
    QPushButton {
    background-color: white;
    border: none;
    border-radius: 10px;
    padding: 30px; /* Increased padding for larger buttons */
}
"""
