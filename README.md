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

---
## Output

CAP produces an Output folder that contains several subfolders and subfiles summarizing the current status of the CDI Masterlist and Data.gov’s Climate Collection. Each file within a subfolder specifies the instance, or date and quarter (1, 2, 3, 4), of its production within the filename. For example, 2021_07_22_3 indicates that the file was produced during quarter 3 of July 22, 2021. The subfolders and subfiles contained within the Output folder are described below.

1. **BrokenAPI** > **Broken_API_URLs_(instance).json**: CAP provides a json file that includes a list of datasets with inactive Data.gov urls (i.e. links producing 404 errors). The file contains attributes of the dataset such as: cdi id, name, title, organization, catalog url, api url, cdi themes, metadata type, geoplatform id, status, and Data.gov ID.

2. **NotInMasterlist** > **Not_in_Masterlist_(instance).json**: CAP produces a json file containing datasets that are hosted within Data.gov’s Climate Collection but are not recorded within the CDI Masterlist. The file contains attributes of the dataset such as: title, name, api url, and catalog url.

3. **OriginalMasterlist** > **Original_CDI_Masterlist_(instance).json**: CAP provides a copy of the original CDI Masterlist (i.e. this file does not include any changes from the current run). The file contains attributes of the dataset such as: cdi id, name, title, organization, catalog url, api url, cdi themes, metadata type, geoplatform id, status, and Data.gov ID.

4. **QAUpdates** > **QA_Updates_(instance).json**: CAP produces a json file describing the quality assessment of the current CDI masterlist. This file contains information regarding fields that are currently invalid and their appropriate updates. 

5. **Retag** > **Retag_(instance).json**: CAP produces a json file that includes a list of datasets that have been dropped from Data.gov’s Climate Collection (i.e. they no longer have the climate tag). The file contains attributes of the dataset such as: cdi id, name, title, organization, catalog url, api url, cdi themes, metadata type, geoplatform id, status, and Data.gov ID.

6. **RetagRequests** > **Retag_Request_(instance).xlsx**: CAP produces an Excel spreadsheet with the necessary information to submit a Data.gov Retag Request. It includes the Dataset Title, Data.gov ID, CDI Theme Tags, and the Data.gov URL. By sending this file to Data.gov, the datasets listed can be re-added to the Climate Collection on Data.gov.

7. **UpdatedMasterlist** > **Updated_CDI_Masterlist_(instance).json**: CAP provides a copy of the updated CDI Masterlist (i.e. this file applies all updates to the original Masterlist). The file contains attributes of the dataset such as: cdi id, name, title, organization, catalog url, api url, cdi themes, metadata type, geoplatform id, status, and Data.gov ID.

8. **CDI_Metrics.json**: CAP produces a json file that provides a summary of CAP metrics. Each entry within the file includes the timestamp of the run, the number of datasets in the CDI Masterlist, and the number of datasets within Data.gov’s Climate Collection. Each run of CAP adds another entry to this file in order to maintain a record of these metrics. 

9. **Warnings_Summary.json**: CAP produces a json file that provides a summary of CAP’s warnings. Each entry within the file includes the timestamp of the run, the total number of warnings, the number of broken urls, the number of datasets that have been dropped from Data.gov’s Climate Collection, and the number of datasets that are hosted within Data.gov’s Climate Collection but not recorded in the CDI Masterlist.
