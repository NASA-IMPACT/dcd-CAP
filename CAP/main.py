import urllib
import requests
import json
import datetime
import os
import argparse
import pandas as pd
import sys


if __name__ == '__main__':
    from Code.cdi_class import CDI_Dataset
    from Code.cdi_validator import CDI_Masterlist_QA, Extra_Data_Gov
    from Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
    from Code.export_json import Export_Object_to_JSON, Export_Time_Series_JSON, Export_List_of_Dict_JSON, Export_Warnings_Summary_JSON, Export_Object_to_Dict
else:
    from .Code.cdi_class import CDI_Dataset
    from .Code.cdi_validator import CDI_Masterlist_QA, Extra_Data_Gov
    from .Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
    from .Code.export_json import Export_Object_to_JSON, Export_Time_Series_JSON, Export_List_of_Dict_JSON, Export_Warnings_Summary_JSON, Export_Object_to_Dict



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
        quarter4 = ['21','22','23','00','01','02']

        if hour in quarter1:
            quarter = '1'
        elif hour in quarter2:
            quarter = '2'   
        elif hour in quarter3:
            quarter = '3'   
        elif hour in quarter4:
            quarter = '4'

        self.date_instance = ('{}_{}'.format(date,quarter))

    def ingest_datasets(self, log=False):
        '''This method ingests the CDI masterlist as CDI Dataset Objects and Checks
        for Broken API Links
        '''
        #### Initialize list and add Dataset Objects ####
        if log:
            print("Ingesting Datasets")

        cdi_datasets = []
        broken_datasets = []
        all_datasets = []
        count = 1 # Initializes Count of Datasets for CDI_ID Renumbering

        masterlist_json = self.cdi_masterlist
        date = self.date_instance

        for ds_json in masterlist_json:
            
            # Standard Output
            if log:
                number = masterlist_json.index(ds_json) + 1
                percentage = round(number/len(masterlist_json) * 100, 2)
                print('\r\tPercentage Complete: {}%'.format(percentage), end="")

            # Create Dataset Object
            dataset = CDI_Dataset(ds_json, date)

            all_datasets.append(dataset)

            # API URL and JSON is broken, add to broken list
            if dataset.full_api_json == "Broken":
                broken_datasets.append(dataset)
                dataset.update_status('Not Active')
                continue
            elif dataset.full_api_json == "unavailable":
                continue

            # Renumber CDI_ID

            dataset.update_cdi_id(count)
            count += 1


            # Add dataset to list of dataset objects
            cdi_datasets.append(dataset)

        self.cdi_datasets = cdi_datasets
        self.broken_datasets = broken_datasets
        self.all_datasets = all_datasets

    def run_qa(self, log=False):
        '''This method uses self.cdi_datasets to run QA on the CDI Masterlist Datasets
        '''

        #### Start QA Analysis of CDI Masterlist ####
        if log:
            print("\nRunning QA Analysis")
        
        updates = []

        cdi_datasets = self.cdi_datasets

        for cdi_dataset in cdi_datasets:

            an_update = CDI_Masterlist_QA(cdi_dataset)

            if an_update: # Empty Dictionary = False Bool
                updates.append(an_update)

            if log:
                # Standard Output
                number = cdi_datasets.index(cdi_dataset) + 1
                percentage = round(number/len(cdi_datasets) * 100, 2)
                print('\r\tPercentage Complete: {}%'.format(percentage), end="")

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
        updated_json = Export_Object_to_Dict(self.all_datasets)
        notags_json = Export_Object_to_Dict(self.notags)
        broken_json = Export_Object_to_Dict(self.broken_datasets)

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



if __name__ == "__main__":

    # Create Directories for Local Run #

    cwd = os.getcwd()

    # parse command line arguments (argparse)
    # --test

    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    optionalargs = parser.add_argument_group("Optional Arguments")
    optionalargs.add_argument("-test", "--test", action='store_true',required=False, help="Include to run CDI Scripts on Test Json File")
    optionalargs.add_argument("-local", "--local", action="store", required=False, help="Include Local JSON Masterlist Path")

    args = parser.parse_args()

    if args.test:
        test_loc = os.path.join(cwd, 'test/test_json.json')

        try:
            with open(test_loc) as testfile:
                masterlist_json = json.load(testfile)
        except:
            print('The expected test file location is missing: "{}"'.format(test_loc))
            sys.exit()
    elif args.local:
        local_loc = args.local

        if os.path.exists(local_loc):
            try:
                with open(local_loc) as localfile:
                    masterlist_json = json.load(localfile)
            except:
                print('Please ensure "{}"" is a file and not a directory'.format(local_loc))
                sys.exit()
        else:
            print('{}" is not a valid file'.format(local_loc))
            sys.exit()
    else:
        # Ingest from Live Github Repo (https://github.com/NASA-IMPACT/cdi_master/blob/master/cdi_master_update_2020.json)
        #github_response = urllib.request.urlopen(r'https://raw.githubusercontent.com/NASA-IMPACT/cdi_master/master/cdi_master_update_2020.json')
        github_response = urllib.request.urlopen(r'https://raw.githubusercontent.com/NASA-IMPACT/cdi_master/master/UpdatedMasterList_Aug2021.json')
        masterlist_json = json.load(github_response)

    # Create Directories

    directories = ['Output', 'Output/Retag','Output/RetagRequests','Output/OriginalMasterlist',
                    'Output/UpdatedMasterlist','Output/QAUpdates','Output/BrokenAPI','Output/NotInMasterlist']

    directory_dict = {}
    for dr in directories:
        path = os.path.join(cwd, dr)
        try:
            os.mkdir(path)
        except:
            pass

        directory_dict[dr] = path

    # Run the CAP Process on the provided Masterlist #
    print("Running CDI Analysis Platform...\n")

    cap = CAP(masterlist_json)
    cap.ingest_datasets(log=True)

    # Run QA
    cap.run_qa(log=True)

    # Execute Climate Tag Check
    cap.climate_tag_check()

    # Not in Masterlist Check
    cap.not_in_masterlist_check()

    # Create Metrics
    cap.create_cdi_metrics()
    cap.create_warnings_summary()

    # Gather Metrics
    all_metrics = cap.export_all()
    date_instance = cap.date_instance
 
    # Export All Metrics #

    output_dir = os.path.join(cwd, 'Output')

    #### Export Original JSON ####
    og_json_filename = 'Original_CDI_Masterlist_{}.json'.format(date_instance)
    og_output_path = os.path.join(directory_dict['Output/OriginalMasterlist'], og_json_filename)
    og_output_json = json.dumps(masterlist_json, indent=4)

    with open(og_output_path, 'w+') as og_outfile:
        og_outfile.write(og_output_json)
    
    print('\nExported Original CDI JSON: {}'.format(og_output_path))

    #### Exporting Time Series Metrics ####
    timeseries_loc = Export_Time_Series_JSON(all_metrics['CDI Metrics'], directory_dict["Output"])
    print('Exported CDI Metrics: {}'.format(timeseries_loc))

    #### Export Warnings Summary Master File ####
    warnings_loc = Export_Warnings_Summary_JSON(all_metrics['Warnings Summary'], directory_dict["Output"])
    print('Exported Warnings: {}'.format(warnings_loc))

    #### Export QA Updates ####
    qa_filename = 'QA_Updates_{}.json'.format(date_instance)
    qa_loc = Export_List_of_Dict_JSON(all_metrics["QA Updates"], directory_dict['Output/QAUpdates'], qa_filename)
    print('Exported QA Updates Made: {}'.format(qa_loc))

    #### Export Retag Dataset ####
    retag_filename = 'Retag_{}.json'.format(date_instance)
    retag_loc = Export_List_of_Dict_JSON(all_metrics["Retag Datasets"], directory_dict['Output/Retag'], retag_filename)
    print('Export Retag Datasets: {}'.format(retag_loc))

    #### Export Retag Request Excel ####
    retag_req_filename = 'Retag_Request_{}.xlsx'.format(date_instance)
    retag_loc = Export_Retag_Request(cap.notags, directory_dict['Output/RetagRequests'],retag_req_filename)
    print('Exported Retag Request: {}'.format(retag_loc))
    
    #### Export Updated JSON ####
    updated_json_filename = 'Updated_CDI_Masterlist_{}.json'.format(date_instance)
    json_loc = Export_List_of_Dict_JSON(all_metrics["Updated Masterlist"], directory_dict['Output/UpdatedMasterlist'], updated_json_filename)
    print('Exported Updated CDI JSON: {}'.format(json_loc))

    #### Export Broken Datasets ####
    broken_filename = 'Broken_API_URLs_{}.json'.format(date_instance)
    broken_loc = Export_List_of_Dict_JSON(all_metrics["Broken API"], directory_dict['Output/BrokenAPI'], broken_filename, broken=True)
    print('Exported Updated CDI JSON: {}'.format(broken_loc))

    #### Export Extra CDI Datasets #### 
    extra_filename = 'Not_in_Masterlist_{}.json'.format(date_instance)
    extra_loc = Export_List_of_Dict_JSON(all_metrics["Not in Masterlist"], directory_dict['Output/NotInMasterlist'], extra_filename)
    print('Exported json of datasets not in the masterlist but on data.gov: {}'.format(extra_loc))

    





    

