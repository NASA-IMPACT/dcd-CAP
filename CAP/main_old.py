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

#################################################################################

def getparser():
	'''Collect command line arguments
	'''

	parser = argparse.ArgumentParser()
	parser._action_groups.pop()

	optionalargs = parser.add_argument_group("Optional Arguments")
	optionalargs.add_argument("-test", "--test", action='store_true',required=False, help="Include to run CDI Scripts on Test Json File")

	return parser

#################################################################################

def interpret_time(today):
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

	return('{}_{}'.format(date,quarter))

##################################################################################
    
def main():

	# Get Command Arguments
	parser = getparser()
	args = parser.parse_args()

	today = datetime.datetime.today()
	today_quartered = interpret_time(today)
	print("\nCDI Integrity Scripts\n\nDate: {}".format(today_quartered))


	#### Define Directories ####

	current_working_dir = os.getcwd()

	# Create Directories
	directories = ['Output', 'Output/Retag','Output/RetagRequests','Output/OriginalMasterlist',
					'Output/UpdatedMasterlist','Output/QAUpdates','Output/BrokenAPI','Output/NotInMasterlist']
	directory_dict = create_directories(current_working_dir, directories)


	#### Create Connection to Masterlist JSON ####

	if args.test:
		# Ingests from test JSON
		testloc = os.path.join(current_working_dir, 'test/test_json.json')
		with open(testloc) as testfile:
			masterlist_json = json.load(testfile)
	else:
		# Ingest from Live Github Repo (https://github.com/NASA-IMPACT/cdi_master/blob/master/cdi_master_update_2020.json)
		github_response = urllib.request.urlopen(r'https://raw.githubusercontent.com/NASA-IMPACT/cdi_master/master/cdi_master_update_2020.json')
		masterlist_json = json.load(github_response)
	

	### Export Original JSON ###
	og_json_filename = 'Original_CDI_Masterlist_{}.json'.format(today_quartered)
	og_output_path = os.path.join(directory_dict['Output/OriginalMasterlist'], og_json_filename)
	og_output_json = json.dumps(masterlist_json, indent=4)

	with open(og_output_path, 'w+') as og_outfile:
		og_outfile.write(og_output_json)

	print('\n\nExported Original CDI JSON: {}\n'.format(og_output_path))



	#### Initialize list and add Dataset Objects ####

	all_datasets = []
	cdi_datasets = []
	broken_datasets = []
	count = 1 # Initializes Count of Datasets for CDI_ID Renumbering

	print("Starting Dataset Ingest")

	for ds_json in masterlist_json:

		# Create Dataset Object
		dataset = CDI_Dataset(ds_json, today_quartered)
		all_datasets.append(dataset)


		# API URL and JSON is broken, add to broken list
		if dataset.full_api_json == "Broken":
			broken_datasets.append(dataset)
			continue

		# Renumber CDI_ID

		dataset.update_cdi_id(count)
		count += 1


		# Add dataset to list of dataset objects
		cdi_datasets.append(dataset)

		# Standard Output
		number = masterlist_json.index(ds_json) + 1
		percentage = round(number/len(masterlist_json) * 100, 2)
		print('\r\tPercentage Complete: {}%'.format(percentage), end="")

	print()		
	print('\tIngest Complete\n\n')

	#### Start QA Analysis of CDI Masterlist ####
	
	print("Starting CDI Masterlist QA Check")

	updates = []

	for cdi_dataset in cdi_datasets:

		an_update = CDI_Masterlist_QA(cdi_dataset)

		if an_update: # Empty Dictionary = False Bool
			updates.append(an_update)
		
		# Standard Output
		number = cdi_datasets.index(cdi_dataset) + 1
		percentage = round(number/len(cdi_datasets) * 100, 2)
		print('\r\tPercentage Complete: {}%'.format(percentage), end="")


	print()		
	print('\tQA Check Complete\n\n')



	#### Check for Climate Tag ####

	print("Starting CDI Climate Tag Check")

	notags = [] #Initialize list of notag datasets

	for cdi_dataset in cdi_datasets:

		notag = Climate_Tag_Check(cdi_dataset)

		if notag:
			notags.append(notag)

		# Standard Tracking Output
		number = cdi_datasets.index(cdi_dataset) + 1
		percentage = round(number/len(cdi_datasets) * 100, 2)
		print('\r\tPercentage Complete: {}%'.format(percentage), end="")

	print()
	print('\tClimate Check Complete\n\n')

	#### Check for Datasets in CC, not in Masterlist ####

	print('Checking for Datasets in the Data.gov Climate Collection\nthat are not in the CDI Master List....\n\n')
	extras, climate_collection = Extra_Data_Gov(masterlist_json, today_quartered)

	############################################
	################# EXPORTS ##################

	#### Export QA Updates ####
	qa_filename = 'QA_Updates_{}.json'.format(today_quartered)
	qa_loc = Export_List_of_Dict_JSON(updates, directory_dict['Output/QAUpdates'], qa_filename)
	print('Exported QA Updates Made: {}\n'.format(qa_loc))


	#### Export Retag Dataset ####
	retag_filename = 'Retag_{}.json'.format(today_quartered)
	retag_loc = Export_Object_to_JSON(notags, directory_dict['Output/Retag'], retag_filename)
	print('Export Retag Datasets: {}\n'.format(retag_loc))

	
	#### Export Retag Request Excel ####
	retag_req_filename = 'Retag_Request_{}.xlsx'.format(today_quartered)
	retag_loc = Export_Retag_Request(notags, directory_dict['Output/RetagRequests'],retag_req_filename)
	print('Exported Retag Request: {}\n'.format(retag_loc))
	

	#### Export Updated JSON ####
	updated_json_filename = 'Updated_CDI_Masterlist_{}.json'.format(today_quartered)
	json_loc = Export_Object_to_JSON(cdi_datasets, directory_dict['Output/UpdatedMasterlist'], updated_json_filename)
	print('Exported Updated CDI JSON: {}\n'.format(json_loc))


	#### Export Broken Datasets ####
	broken_filename = 'Broken_API_URLs_{}.json'.format(today_quartered)
	broken_loc = Export_Object_to_JSON(broken_datasets, directory_dict['Output/BrokenAPI'], broken_filename, broken=True)
	print('Exported Updated CDI JSON: {}\n'.format(broken_loc))


	#### Export Extra CDI Datasets #### FIXX
	extra_filename = 'Not_in_Masterlist_{}.json'.format(today_quartered)
	extra_loc = Export_List_of_Dict_JSON(extras, directory_dict['Output/NotInMasterlist'], extra_filename)
	print('Exported json of datasets not in the masterlist but on data.gov: {}\n'.format(extra_loc))

	#### Exporting Time Series Metrics ####

	'''
	Come back to this way of counting Active Masterlist - 
	Currently we are not updating the is_active attribute in the masterlist

	cdi_datasets_df = obj_to_df(all_datasets)
	ml_count = len(cdi_datasets_df[cdi_datasets_df['is_active']=="True"])# Only Including Working API links
	'''

	date = today.strftime("%m/%d/%Y %I:%M %p")
	ml_count = len(cdi_datasets) # List of objects which do not have broken API urls
	cc_count = len(climate_collection) # from data.gov Climate Collection

	timeseries_dict = {
						"Date":today_quartered,
						"Masterlist_Count":ml_count,
						"Climate_Collection_Count":cc_count
	}
	
	timeseries_loc = Export_Time_Series_JSON(timeseries_dict, directory_dict["Output"])
	print('Exported CDI Metrics: {}\n'.format(timeseries_loc))

	### Export Warnings Summary Master File ###
	
	date = today.strftime("%m/%d/%Y %I:%M %p")
	total_warnings = len(broken_datasets) + len(notags) + len(extras)

	warnings_dict = {
						"Date": today_quartered,
						"Total Warnings": total_warnings,
						"Broken URLs Count": len(broken_datasets),
						"Lost Climate Tag Count": len(notags),
						"Not in Masterlist Count": len(extras)
	}
	
	warnings_loc = Export_Warnings_Summary_JSON(warnings_dict, directory_dict["Output"])
	print('Exported Warnings: {}\n'.format(warnings_loc))


#################################################################################

def create_directories(main_dir, directories_list):
	'''This function creates the directories based on the input 
	directory list
	'''

	directories = {}

	for dr in directories_list:
		path = os.path.join(main_dir, dr)
		try:
			os.mkdir(path)
		except:
			pass

		directories[dr] = path

	return directories

#################################################################################

def obj_to_df(cdi_datasets):
	'''This function creates a panda dataframe from an input list
	of CDI Objects
	'''

	list_of_datasets = [] # Initialize list of dataset dictionaries (or json)

	for dataset in obj:

		dataset_dict = dataset.export_dictionary() # Exports Dataset contents in dictionary

		list_of_datasets.append(dataset_dict)

	cdi_df = pd.DataFrame(list_of_datasets)

	return(cdi_df)

#################################################################################



if __name__ == '__main__' :
	main()













