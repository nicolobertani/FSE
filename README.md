# Fast and Simple Adaptive Elicitations
## Software for Laboratory Experiments

### Introduction

This repo contains the code to implement the Fast and Simple Elicitation method of [Bertani, Diecidue, Perny, and Viappiani (WP)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3569625).
More specifically, it provides Python code to locally run FSE and the competing methods described in Section 4.3.
If you are interested in running these methods online, please refer to [this different repo](https://github.com/nicolobertani/FSE_online_horserace), where you can find implementations using otree and Python.


### Installation

After cloning/forking, and assuming you have Python installed, ensure that you have the required packages by running:

```bash
pip install -r requirements.txt
```


### Usage

To launch the experiment, simply run:

```bash
python main.py
```

By default, the software executes FSE.
The elicitation procedure can be specified to FSE, bisection or Bayesian elicitation as follows:

```bash
python main.py FSE
python main.py bisection
python main.py Bayesian
```

These commands are not case sensitive.

Answers are recorded using an automatically generated progressive number 
They are recorded progressively, meaning that the results of incomplete elicitations will not be lost.


### Personalization

The module [`backend/shared_info.py`](backend/shared_info.py) conveniently gathers and defines several experimental details that the researcher might wish to alter. 
These include stimuli, participation fee, currency, and instructions. 
Changes to this file are automatically reflected in the experimental interface.


### Acknowledgments

The initial version of this code was developed by my excellent student and research assistant [Mathieu Leng](www.linkedin.com/in/mathieu-leng-b5556a1b1) and I am thankful for his help.


### License

Copyright (C) 2023-present  Nicolò Bertani

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but without any warranty; without even the implied warranty of merchandability or fitness for a particular purpose.  See the GNU General Public License for more details.

For the GNU General Public License see <https://www.gnu.org/licenses/>. You should also find a [copy](LICENSE) of this license in this repository.

If you use this software, please cite the associated paper. You can find the [BibTeX citation](cite.bib) in this repository.