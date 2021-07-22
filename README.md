# CDI Analysis Platform (CAP)


## Introduction
The [Climate Collection](https://data.gov/climate) on Data.gov originated from the [Climate Data Initiative (CDI)](https://obamawhitehouse.archives.gov/the-press-office/2014/03/19/fact-sheet-president-s-climate-data-initiative-empowering-america-s-comm), which was an effort to make federal climate datasets freely available. Furthermore, the Climate Collection was designed to maintain a catalog of climate resilience datasets in nine curated themes: Arctic, Coastal Flooding, Ecosystem Vulnerability, Energy Infrastructure, Food Resilience, Human Health, Transportation, Tribal Nations, and Water.

The CDI Analysis Platform (CAP) was developed to automate the analysis and maintenance of the data.gov Climate Collection through preserving the integrity of the originally curated [CDI Masterlist](https://github.com/NASA-IMPACT/cdi_master/blob/master/cdi_master_update_2020.json). For future use and questions, please contact Andrew Weis at adw0059@uah.edu.



# User's Guide

>***Note:*** This program requires `Python 3.8` installed on your system.

---
## Install and Create a Virtual Environment

**Clone the repo:** [https://github.com/NASA-IMPACT/dcd-CAP](https://github.com/NASA-IMPACT/dcd-CAP)

**Go to the project directory:** `cd CAP`

**Create a python virtual environment:** `python -m venv env`

**Activate the environment:** `source env/bin/activate`

**Install the requirements:** `pip install -r requirements.txt`

>*Note: The above example is for a Unix or macOS operating system. [Click here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) for more information on creating python virtual environments for your system*

---
## Running the Program


**Run `main.py`:**
```
$ python main.py -h

usage: main.py [-h] [-test]

Optional Arguments:
  -test, --test  Include to run CDI Scripts on Test Json File
```

To run on the full CDI masterlist simply run _main.py_
```
$ python main.py
```

To test a local json file, use the `--test` argument.
```
$ python main.py -test
```