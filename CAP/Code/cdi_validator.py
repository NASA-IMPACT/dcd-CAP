import urllib
import requests
import json
import datetime
import os
import pandas as pd

from Code.cdi_checks import *

#################################################################################

def CDI_masterlist_QA(cdi_dataset):
	'''This Function uses the various checks in cdi_checks.py to validate 
	the CDI Masterlist attributes against the data.gov API
	'''

	change_dict = {}

	# Get API URL Contents
	api_json = cdi_dataset.full_api_json

	# Crossreference the CKAN API for dataset and check/update masterlist values
	name_change, catalog_change = check_name_and_update_caturl(cdi_dataset, api_json)
	title_change = check_title(cdi_dataset, api_json)
	org_change = check_organization(cdi_dataset, api_json)
	metadata_type_change = check_metadata_type(cdi_dataset, api_json)

	# Check for Climate Tag and gives True/False value for cdi_dataset.climate_tag
	check_climate_tag(cdi_dataset, api_json)

	# Check datagov_id against api_url
	datagov_id_change = check_datagov_id(cdi_dataset)

	# Compile the updates made and return them as a dictionary
	change_dict["cdi_id"] = cdi_dataset.cdi_id
	change_dict['name'] = invalid_updated_todict(name_change) # Index 0 correlates to Name
	change_dict['title'] = invalid_updated_todict(title_change)
	change_dict['organization'] = invalid_updated_todict(org_change)
	change_dict['catalog_url'] = invalid_updated_todict(catalog_change) # Index 1 correlates to cat url
	change_dict['metadata_type'] = invalid_updated_todict(metadata_type_change)
	change_dict['datagov_id'] = invalid_updated_todict(datagov_id_change)

	# Use below code to only return if the dictionary has updates
	 
	# Return dictionary IF there are values
	change_list = [name_change, catalog_change, title_change, org_change, metadata_type_change, datagov_id_change]

	for item in change_list:
		if item != None:
			return change_dict

	return None
	

#################################################################################

def invalid_updated_todict(listof_invalid_updated):
	'''This function takes a list of two lengths, and returns a dictionary
	of those two notated as Invalid and Updated respectively'''

	if listof_invalid_updated == None:
		return ''

	before, after = listof_invalid_updated

	invalid_updates_dict = {
							"Invalid":before,
							"Updated":after
							}

	return invalid_updates_dict

#################################################################################
def extra_data_gov(masterlist_json):
	''' This function checks all the datasets in the data.gov climate group 
	against the data gov ids in the masterlist to identify mislabeled data. '''

	not_in_master_full = pd.DataFrame({}) # Create empty dataframe

	# Call Full Climate Collection (CC) API
	api_call = requests.get('https://catalog.data.gov/api/3/action/package_search?fq=groups:climate5434&rows=2000').json()
	data_gov_id_df = (pd.json_normalize(api_call['result']['results'])) # Create a Dataframe of all Data.gov IDs in Data.gov CC
	climate_collection=data_gov_id_df
	# Set up list of all CDI Masterlist IDs
	masterlist_id_list = (pd.json_normalize(masterlist_json)['datagov_ID']).tolist()
	data_gov_id_df['API'] = ''
	data_gov_id_df['Catalog'] = ''

	# Loop through Climate Collection DataFrame
	for index,row in data_gov_id_df.iterrows():

		# Crossreference with CDI Masterlist (ML) and if not in ML, record dataset attributes
		if row['id'] in masterlist_id_list:
			pass
		else:
			row['API'] = 'https://catalog.data.gov/api/3/action/package_show?id={}'.format(row['id'])
			row['Catalog'] = 'https://catalog.data.gov/dataset/{}'.format(row['name'])
			not_in_master_full = not_in_master_full.append(row)

	# Reformat Output Dataframe and convert to Dictionary
	formatted_df = pd.DataFrame({'Title':not_in_master_full['title'],'Name':not_in_master_full['name'],'API':not_in_master_full['API'],'Catalog':not_in_master_full['Catalog']})
	dictionary = formatted_df.to_dict('index')
	extra_list_of_dictionaries= [value for value in dictionary.values()]
	
	return extra_list_of_dictionaries, climate_collection

#################################################################################
