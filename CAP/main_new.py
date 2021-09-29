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
    def __init__(self, master_list):
        if master_list:
            self.master_list = master_list
        else:
            raise Exception("Please provide a master list")

        interpret_time()

    def interpret_time(self):
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
        '''Method should use Main.py lines 105-142 to ingest the self.masterlist as Dataset Objects
        Method should create an instance variables self.cdi_datasets and self.broken_datasets'''
        pass

    def run_qa(self):
        '''Method should use Main.py lines 143-165 and the self.cdi_datasets instance variable to run the QA Checks
        Method should create an instance variable self.updates and return self.updates'''
        pass

    def climate_tag_check(self):
        '''Method should use Main.py lines 167-187 and self.cdi_datasets instance variable to run the Climate Tag Check
        Method should create an instance variable self.notags and return self.notags'''
        pass

    def not_in_masterlist_check(self):
        '''Method should use Main.py lines 188-192 and self.masterlist instance variable run the Not in masterlist check
        Method should create two instance variables self.extras and self.climate_collection and return self.extras'''
        pass


    def create_cdi_metrics(self):
        '''Method should use the instance variables self.cdi_datasets and self.climate_collection to create the self.cdi_metrics
        instance variable and return it'''
        
        ml_count = len(CDI_Today.cdi_datasets)
        cc_count = len(CDI_Today.climate_collection)

    def create_warnings_summary(self):
        '''Method should use the relavent instance variables to create the self.warnings_summary instance variable and return it
        '''
        pass

    def export(self):
        # return a dictionary with all required metrics
        return
    

