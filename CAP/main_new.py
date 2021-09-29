import urllib
import requests
import json
import datetime
import os
import argparse
import pandas as pd


if __name__ == '__main__':
    from Code.cdi_class import CDI_Dataset
    from Code.cdi_validator import CDI_Masterlist_QA, Extra_Data_Gov
    from Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
    from Code.export_json import Export_Object_to_JSON, Export_Time_Series_JSON, Export_List_of_Dict_JSON, Export_Warnings_Summary_JSON
else:
    from .Code.cdi_class import CDI_Dataset
    from .Code.cdi_validator import CDI_Masterlist_QA, Extra_Data_Gov
    from .Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
    from .Code.export_json import Export_Object_to_JSON, Export_Time_Series_JSON, Export_List_of_Dict_JSON, Export_Warnings_Summary_JSON



class CAP():
    '''
    Takes a Climate Collection Masterlist and Creates a Maintenance Instance with multiple
    checking methods
    '''

    def __init__(self, cdi_masterlist):
        '''Masterlist should be input in json format
        '''
        if cdi_masterlist:
            self.cdi_masterlist = cdi_masterlist
        else:
            raise Exception("Please provide a master list")

        self.interpret_time()


    def interpret_time(self):
        '''
        '''

        today = datetime.datetime.today()
        hour = today.strftime("%H")
        date = today.strftime("%Y_%m_%d")

        quarter1 = ['03','04','05','06','07','08']
        quarter2 = ['09','10','11','12','13','14']
        quarter3 = ['15','16','17','18','19','20']
        quarter4 = ['21','22','23','24','01','02']

        if hour in quarter1:
            quarter = '1'
        elif hour in quarter2:
            quarter = '2'   
        elif hour in quarter3:
            quarter = '3'   
        elif hour in quarter4:
            quarter = '4'

        self.date_instance = ('{}_{}'.format(date,quarter))

    def ingest_datasets(self):
        '''This method ingests the CDI masterlist as CDI Dataset Objects and Checks
        for Broken API Links
        '''
        #### Initialize list and add Dataset Objects ####

        cdi_datasets = []
        broken_datasets = []
        count = 1 # Initializes Count of Datasets for CDI_ID Renumbering

        masterlist_json = self.cdi_masterlist

        for ds_json in masterlist_json:

            # Create Dataset Object
            dataset = CDI_Dataset(ds_json)

            # API URL and JSON is broken, add to broken list
            if dataset.full_api_json == "Broken":
                broken_datasets.append(dataset)
                continue

            # Renumber CDI_ID

            dataset.update_cdi_id(count)
            count += 1


            # Add dataset to list of dataset objects
            cdi_datasets.append(dataset)

        self.cdi_datasets = cdi_datasets
        self.broken_datasets = broken_datasets

    def run_qa(self):
        '''Method should use Main.py lines 143-165 and the self.cdi_datasets instance variable to run the QA Checks
        Method should create an instance variable self.updates and return self.updates'''

        #### Start QA Analysis of CDI Masterlist ####
        
        updates = []

        cdi_datasets = self.cdi_datasets

        for cdi_dataset in cdi_datasets:

            an_update = CDI_Masterlist_QA(cdi_dataset)

            if an_update: # Empty Dictionary = False Bool
                updates.append(an_update)

        self.updates = updates

        return self.updates

    def climate_tag_check(self):
        '''Method should use Main.py lines 167-187 and self.cdi_datasets instance variable to run the Climate Tag Check
        Method should create an instance variable self.notags and return self.notags'''
        self.notags = []

    def not_in_masterlist_check(self):
        '''Method should use Main.py lines 188-192 and self.masterlist instance variable to run the Not in masterlist check
        Method should create two instance variables self.extras and self.climate_collection and return self.extras'''
        self.extras = []

    def create_cdi_metrics(self):
        '''Method should use the instance variables self.cdi_datasets and self.climate_collection to create the self.cdi_metrics
        instance variable and return it'''
        
        ml_count = len(CDI_Today.cdi_datasets)
        cc_count = len(CDI_Today.climate_collection)

    def create_warnings_summary(self):
        '''Method should use the relavent instance variables to create the self.warnings_summary instance variable and return it
        '''
        ### Export Warnings Summary ###
        
        date = self.date_instance
        broken_datasets = self.broken_datasets
        notags = self.notags
        extras = self.extras

        total_warnings = len(broken_datasets) + len(notags) + len(extras)

        warnings_dict = {
                            "Date": date,
                            "Total Warnings": total_warnings,
                            "Broken URLs Count": len(broken_datasets),
                            "Lost Climate Tag Count": len(notags),
                            "Not in Masterlist Count": len(extras)
        }

        self.warnings_summary = warnings_dict

        return self.warnings_summary

    def export_all(self):
        # return a dictionary with all required metrics
        return 
    

