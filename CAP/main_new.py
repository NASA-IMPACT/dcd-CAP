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
        ''' Masterlist should be input in json format
        '''

        self.interpret_time()

        if cdi_masterlist:
            self.cdi_masterlist = cdi_masterlist
            self.archive_masterlist(cdi_masterlist)
        else:
            raise Exception("Please provide a master list")

    def archive_masterlist(self, cdi_masterlist):
        '''Add Date_ID to Original Masterlist JSON'''

        for og_ds in cdi_masterlist:
            og_ds['date_id'] = self.date_instance
        
        self.original_masterlist = cdi_masterlist

    def interpret_time(self):
        ''' This method interprets the quarter time that the instance was run
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
        date = self.date_instance

        for ds_json in masterlist_json:

            # Create Dataset Object
            dataset = CDI_Dataset(ds_json, date)

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
        '''This method uses self.cdi_datasets to run QA on the CDI Masterlist Datasets
        '''

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
        '''This method interprets the CDI Datasets and checks for it's climate tag in the CKAN API'''

        cdi_datasets = self.cdi_datasets

        notags = [] #Initialize list of notag datasets

        for cdi_dataset in cdi_datasets:

            notag = Climate_Tag_Check(cdi_dataset)

            if notag:
                notags.append(notag)

        self.notags = notags

        return self.notags

            
    def not_in_masterlist_check(self):
        '''This method interprets which datasets are in the Climate Collection that are not in the CDI
        Masterlist, as well as create the self.climate_collection instance variable which is a dataframe of
        the Climate Collection'''

        masterlist_json = self.cdi_masterlist
        date = self.date_instance
        extras, climate_collection = Extra_Data_Gov(masterlist_json, date)

        self.extras = extras
        self.climate_collection = climate_collection

        return self.extras

    def create_cdi_metrics(self):
        '''This method exports the CDI Metrics of the instance including Climate Count and Masterlist Count'''

        date = self.date_instance
        ml_count = len(self.cdi_datasets)
        cc_count = len(self.climate_collection)

        cdi_metrics_dict = {
                            "date_id": date,
                            "cdi_masterlist_count": ml_count,
                            "climate_collection_count": cc_count
        }

        self.cdi_metrics = cdi_metrics_dict

        return self.cdi_metrics

    def create_warnings_summary(self):
        '''This Method returns a dictionary of a CDI Warnings Summary Metrics
        '''
        ### Export Warnings Summary ###
        
        date = self.date_instance
        broken_datasets = self.broken_datasets
        notags = self.notags
        extras = self.extras

        total_warnings = len(broken_datasets) + len(notags) + len(extras)

        warnings_dict = {
                            "date_id": date,
                            "total_warnings": total_warnings,
                            "broken_url_count": len(broken_datasets),
                            "lost_climate_tag_count": len(notags),
                            "not_in_masterlist_count": len(extras)
        }

        self.warnings_summary = warnings_dict

        return self.warnings_summary

    def export_all(self):
        # return a dictionary with all required metrics

        date = self.date_instance

        #Get JSONs if Necessary
        updated_json = Export_Object_to_JSON(self.cdi_datasets)
        notags_json = Export_Object_to_JSON(self.notags)
        broken_json = Export_Object_to_JSON(self.broken_datasets)

        all_metrics = {

                        "CDI Metrics": self.cdi_metrics,
                        "Warnings Summary": self.warnings_summary,
                        "Updated Masterlist": updated_json,
                        "Original Masterlist": self.original_masterlist,
                        "Retag Datasets": notags_json,
                        "Broken API": broken_json,
                        "QA Updates": self.updates,
                        "Not in Masterlist": self.extras

        }

        return all_metrics










    

