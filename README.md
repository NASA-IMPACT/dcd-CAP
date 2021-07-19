# CDI Analysis Platform (CAP)


## Introduction
The [Climate Collection](https://data.gov/climate) on Data.gov was born out of the [Climate Data Initiative (CDI)](https://obamawhitehouse.archives.gov/the-press-office/2014/03/19/fact-sheet-president-s-climate-data-initiative-empowering-america-s-comm) in efforts maintaining a quality catalog of climate resiliance datasets in nine currated themes.

The CDI Analysis Platform (CAP) was developed to automate the analysis and maintenance of the data.gov Climate Collection in efforts of maintaining the integrity of the originally curated [CDI Masterlist](https://github.com/NASA-IMPACT/cdi_master/blob/master/cdi_master_update_2020.json).



# User's Guide

***Note:*** This program requires `Python 3.8` installed in your system.

---
## Install and Create a Virtual Environment

**Clone the repo:** [https://github.com/NASA-IMPACT/dcd-CAP](https://github.com/NASA-IMPACT/dcd-CAP)

**Go to the project directory:** `cd CAP`

### Create a python Virtual Environment and Install Packages

>**Create a python virtual environment:** `python -m venv env`

>**Activate the environment:** `source env/bin/activate`

>**Install the requirements:** `pip install -r requirements.txt`

### OR Create an anaconda Virtual Environment and Install Packages

***Note:*** This requires anaconda3 installation.

>**Create an anaconda virtual environment:** `conda create --name {envname} python=3.8`

>**Activate the environment:** `conda activate {envname}`

>**Install the requirements:** `pip install -r requirements.txt`

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









