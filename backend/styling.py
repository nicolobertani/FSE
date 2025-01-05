from PyQt5.QtGui import QFont

# text style 
fontTitle = QFont()
fontTitle.setPointSize(25)

# font of buttons
fontButtons = QFont()
fontButtons.setPointSize(18)

# font of buttons
fontProceed = QFont()
fontProceed.setPointSize(18)
fontProceed.setItalic(True)


# style of the buttons
buttonStyleOff = """
    QPushButton {
    background-color: white;
    color: darkblue;
    border: none;
    border-radius: 10px;
    padding: 60px; /* Increased padding for larger buttons */
}
"""
buttonStyleOn = """
    QPushButton {
    background-color: grey;
    color: darkblue;
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
    padding: 20px; /* Increased padding for larger buttons */
}
"""
