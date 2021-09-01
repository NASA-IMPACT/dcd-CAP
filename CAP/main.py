import urllib
import requests
import json
import datetime
import os
import argparse
import pandas as pd

from Code.cdi_class import CDI_Dataset
from Code.cdi_validator import CDI_masterlist_QA, extra_data_gov
from Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
from Code.export_json import Export_Update_CDI_JSON, Export_Time_Series_JSON, Export_Broken_JSON, Export_Original_CDI_JSON, export_list_of_dict_JSON, Export_Warnings_Summary_JSON, Export_Object_to_JSON




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
	hour=today.strftime("%H")
	date=(today.strftime("%Y_%m_%d"))
	quarter1=['03','04','05','06','07','08']
	quarter2=['09','10','11','12','13','14']
	quarter3=['15','16','17','18','19','20']
	quarter4=['21','22','23','24','01','02']
	if hour in quarter1:
		quarter='1'
	elif hour in quarter2:
		quarter='2'	
	elif hour in quarter3:
		quarter='3'	
	elif hour in quarter4:
		quarter='4'	
	return(date+"_"+quarter)

##################################################################################
def obj_to_df(obj):

	list_of_datasets = [] # Initialize list of dataset dictionaries (or json)

	for dataset in obj:

		dataset_dict = dataset.export_dictionary() # Exports Dataset contents in dictionary

		list_of_datasets.append(dataset_dict)

	return(pd.DataFrame(list_of_datasets))

##################################################################################

def main():

	# Get Command Arguments
	parser = getparser()
	args = parser.parse_args()

	today = datetime.datetime.today()
	today_quartered=interpret_time(today)
	print("\nCDI Integrity Scripts\n\nDate: {}\n\n\n".format(today_quartered))


	#### Define Directories ####

	current_working_dir = os.getcwd()

	# Create Directories
	instance_dir = 'Output/{}'.format(today_quartered)



	directories = ['Output', instance_dir]
	directory_dict = create_directories(current_working_dir, directories)


	#### Create Masterlist JSON ####

	if args.test:
		# Ingests from test JSON
		testloc = os.path.join(current_working_dir, 'test/test_json.json')
		with open(testloc) as testfile:
			masterlist_json = json.load(testfile)
	else:
		# Ingest from Live Github Repo (https://github.com/NASA-IMPACT/cdi_master/blob/master/cdi_master_update_2020.json)
		github_response = urllib.request.urlopen(r'https://raw.githubusercontent.com/NASA-IMPACT/cdi_master/master/cdi_master_update_2020.json')
		masterlist_json = json.load(github_response)


	#### Initialize list and add Dataset Objects ####

	cdi_datasets = []
	broken_datasets = []
	count = 1 # Initializes Count of Datasets for CDI_ID Renumbering

	print("Starting Dataset Ingest")

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

		# Standard Output
		number = masterlist_json.index(ds_json) + 1
		percentage = round(number/len(masterlist_json) * 100, 2)
		print('\r\tPercentage Complete: {}%'.format(percentage), end="")
  	
	# Export Original JSON
	og_json_loc = Export_Original_CDI_JSON(cdi_datasets, directory_dict[instance_dir], today_quartered)
	print('\n\nExported Original CDI JSON: {}\n'.format(og_json_loc))


	#### Start QA Analysis of CDI Masterlist ####

	print("Starting CDI Masterlist QA Check")

	updates = []

	for cdi_dataset in cdi_datasets:

		an_update = CDI_masterlist_QA(cdi_dataset)

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
	extras, climate_collection = extra_data_gov(masterlist_json)

	############################################
	################# EXPORTS ##################

	#### Export QA Updates ####


	qa_loc = export_list_of_dict_JSON(updates, directory_dict[instance_dir], "QA_Updates", today_quartered)

	print('Exported QA Updates Made: {}\n'.format(qa_loc))

	#### Export Retag Dataset ####

	retag_filename = 'retag_{}.json'.format(today_quartered)
	retag_loc = Export_Object_to_JSON(notags, directory_dict[instance_dir], retag_filename)
	print('Export Retag Datasets: {}\n'.format(retag_loc))

	
	#### Export Retag Request Excel ####


	retag_loc = Export_Retag_Request(notags, directory_dict[instance_dir],today_quartered)
	print('Exported Retag Request: {}\n'.format(retag_loc))
	

	#### Export Updated JSON ####

	json_loc = Export_Update_CDI_JSON(cdi_datasets, directory_dict[instance_dir],today_quartered)
	print('Exported Updated CDI JSON: {}\n'.format(json_loc))

	#### Export Broken Datasets ####

	broken_loc = Export_Broken_JSON(broken_datasets, directory_dict[instance_dir],today_quartered)
	print('Exported Updated CDI JSON: {}\n'.format(broken_loc))

	#### Export Extra CDI Datasets ####
	extra_loc = export_list_of_dict_JSON(extras, directory_dict[instance_dir], 'data_gov_not_master_', today_quartered)
	print('Exported CSV of datasets not in the masterlist but on data.gov: {}\n'.format(extra_loc))

	#### Exporting Time Series Metrics ####

	date = today.strftime("%m/%d/%Y %I:%M %p")
	
	cdi_datasets_df=obj_to_df(cdi_datasets)
	ml_count = len(cdi_datasets_df[cdi_datasets_df['is_active']=="True"])# Only Including Working API links
	cc_count = len(climate_collection) # from data.gov Climate Collection

	timeseries_dict = {
						"Date":today_quartered,
						"Masterlist_Count":ml_count,
						"Climate_Collection_Count":cc_count
	}
	
	timeseries_loc = Export_Time_Series_JSON(timeseries_dict, directory_dict["Output"],today_quartered)
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

def create_directories(main_dir, directoryies_list):


	directories = {}

	for dr in directoryies_list:
		path = os.path.join(main_dir, dr)
		try:
			os.mkdir(path)
		except:
			pass

		directories[dr] = path

	return directories

#################################################################################




if __name__ == '__main__' :
	main()













