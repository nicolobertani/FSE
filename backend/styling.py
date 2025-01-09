from PyQt5.QtGui import QFont

# title style 
fontTitle = QFont()
fontTitle.setPointSize(25)

# font of the instructions
instructions_font = QFont()
instructions_font.setPointSize(18)

# font of buttons
fontButtons = QFont()
fontButtons.setPointSize(18)

# font of buttons
fontProceed = QFont()
fontProceed.setPointSize(18)
fontProceed.setItalic(True)


# style of the buttons
instructionStyle = """
    background-color: white; 
    color: black; 
    border-radius: 10px;
"""

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
    background-color: lightblue;
    color: darkblue;
    border: none;
    border-radius: 10px;
    padding: 60px; /* Increased padding for larger buttons */
}
"""
buttonProceed = """
    QPushButton {
    color : black;  
    background-color: white;
    border: none;
    border-radius: 10px;
    padding: 20px; /* Increased padding for larger buttons */
}
"""
