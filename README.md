# Fast and Simple Adaptive Elicitations

## Introduction

The goal of this project is to offer a procedure for a laboratory experiment. The aim of the laboratory experiment is to measure decision models. 
This code has been used for the paper: https://www.zbw.eu/econis-archiv/bitstream/11159/431240/1/EBP07639140X_0.pdf 

## Installation

Python version: Python 3.7

Packages needed and link for installation:
  - pandas https://pandas.pydata.org/docs/getting_started/install.html 
  - numpy https://www.edureka.co/blog/install-numpy/
  - scipy https://scipy.org/install/
  - PyQt5 https://pypi.org/project/PyQt5/

## Usage

### What to change to make it work 

In order to make it work on your computer, it is needed that you change this line `sys.path.insert(0, '/Users/mathieuleng/PycharmProjects/FSE/backend')` by `sys.path.insert(0, 'your_path_to_the_project/FSE/backend')`.
        
### How to use 

To launch the program, run **interface/main.py**. A first window should open, asking the user for a 4-digit code. Here, a window might open or not depending on **CodeEntryWindow.askDir**, asking for a directory to save the results in. If **askDir** is *False*, the results will be saved in the same directory as the code. The user confirms the code and the code is checked, if a file having this code already exists in the directory, the user will be asked for another code. If the code is correct, the first window closes and a second one opens. On this window, the user can see a sentence explaining the choice offered, 2 charts illustrating the odds, 2 buttons to make a choice, and finally a button to confirm. The user executes a sequence of choices until a result has been calculated and the application stops, thanking the user for its input.

The user's results are saved after each choice so there is no fear to have regarding crashes during the process. The results can then be found in the file having as its name the code provided by the user. 

### How to change 

The *constants* in the **model_interface.py** may be changed for different applications. The *initial values* in **main.py** can also be changed if needed.
It is also possible to change the kind of code needed. By default, it is a 4-digit code but for certain applications, it might not be enough. It can be changed ***CodeEntryWindow.checkCode()***.
It is also possible to choose whether the user can choose the directory to save the results, just change **CodeEntryWindow.askDir**. 

### Acknowledgments

Acknowledgments to Pr. Nicolo Bertani without whom this project would not have been possible, he has been extremely helpful and a pedagogue.

### Contact

Mathieu Leng: 
  - Linkedin: www.linkedin.com/in/mathieu-leng-b5556a1b1
  - email: s-mleng@ucp.pt
