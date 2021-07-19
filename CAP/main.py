import urllib
import requests
import json
import datetime
import os
import argparse

from Code.cdi_class import CDI_Dataset
from Code.cdi_validator import CDI_masterlist_QA, Export_QA_Updates
from Code.tag_validator import Climate_Tag_Check, Export_Retag_Request
from Code.export_json import Export_Update_CDI_JSON

#################################################################################

# Test

def getparser():
	'''Collect command line arguments
	'''

	parser = argparse.ArgumentParser()
	parser._action_groups.pop()

	optionalargs = parser.add_argument_group("Optional Arguments")
	optionalargs.add_argument("-test", "--test", action='store_true',required=False, help="Include to run CDI Scripts on Test Json File")

	return parser	

#################################################################################

def main():

	today = datetime.datetime.today()
	print("\nCDI Integrity Scripts\n\nDate: {}\n\n\n".format(today.strftime("%m/%d/%Y %I:%M %p")))

	# Get Command Arguments
	parser = getparser()
	args = parser.parse_args()


	#### Define Directories ####

	current_working_dir = os.getcwd()

	# Create Directories
	instance_dir = 'Output/{}'.format(today.strftime("%Y_%m_%d_%I%M_%p"))
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

	for ds_json in masterlist_json:
		dataset = CDI_Dataset(ds_json)
		cdi_datasets.append(dataset)




	#### Start QA Analysis of CDI Masterlist ####

	print("Starting CDI Masterlist QA Check")

	updates = {} #Initiatlize dictionary of updates (Uses CDI_ID as key)

	for cdi_dataset in cdi_datasets:

		an_update = CDI_masterlist_QA(cdi_dataset)

		if an_update: # Empty Dictionary = False Bool
			updates[cdi_dataset.cdi_id] = an_update # Creates dictionary entry with CDI_ID of dataset as key)

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



	#### Export QA Updates ####
	qa_loc = Export_QA_Updates(updates, directory_dict[instance_dir])
	print('Exported QA Updates Made: {}\n'.format(qa_loc))

	
	#### Export Retag Request ####
	retag_loc = Export_Retag_Request(notags, directory_dict[instance_dir])
	print('Exported Retag Request: {}\n'.format(retag_loc))
	

	#### Export Updated JSON ####
	json_loc = Export_Update_CDI_JSON(cdi_datasets, directory_dict[instance_dir])
	print('Exported Updated CDI JSON: {}\n'.format(json_loc))

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













