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

	# Open API URL Contents
	api_url = cdi_dataset.api_url
	api_request = urllib.request.urlopen(api_url)
	api_json = json.load(api_request)

	# Crossreference the CKAN API for dataset and check/update masterlist values
	name_cat_change = check_name_and_update_caturl(cdi_dataset, api_json)
	title_change = check_title(cdi_dataset, api_json)
	org_change = check_organization(cdi_dataset, api_json)
	metadata_type_change = check_metadata_type(cdi_dataset, api_json)

	# Check for Climate Tag and gives True/False value for cdi_dataset.climate_tag
	check_climate_tag(cdi_dataset, api_json)

	# Compile the updates made and return them as a dictionary
	if name_cat_change:
		name_change = name_cat_change[0]
		catalog_url_change = name_cat_change[1]

		change_dict['name'] = name_change
		change_dict['catalog_url'] = catalog_url_change

	if title_change:
		change_dict['title'] = title_change

	if org_change:
		change_dict['organization'] = org_change

	if metadata_type_change:
		change_dict['metadata_type'] = metadata_type_change


	return change_dict

#################################################################################
def extra_data_gov(masterlist_json):
	''' This function checks all the datasets in the data.gov climate group against the data gov ids in the masterlist to identify mislabeled data. '''
	not_in_master_full=pd.DataFrame({})
	api_call=requests.get('https://catalog.data.gov/api/3/action/package_search?fq=groups:climate5434&rows=2000').json()
	data_gov_id_df=(pd.json_normalize(api_call['result']['results']))
	masterlist_id_list=(pd.json_normalize(masterlist_json)['datagov_ID']).tolist()
	data_gov_id_df['API']=''
	data_gov_id_df['Catalog']=''

	for index,row in data_gov_id_df.iterrows():
		if row['id'] in masterlist_id_list:
			pass
		else:
			row['API']='https://catalog.data.gov/api/3/action/package_show?id={}'.format(row['id'])
			row['Catalog']='https://catalog.data.gov/dataset/{}'.format(row['name'])
			not_in_master_full=not_in_master_full.append(row)	

	formatted_df=pd.DataFrame({'Title':not_in_master_full['title'],'Name':not_in_master_full['name'],'API':not_in_master_full['API'],'Catalog':not_in_master_full['Catalog']})
	dictionary=formatted_df.to_dict('index')
	return dictionary


#################################################################################

def Export_QA_Updates(update_dict, output_location):
	'''This function takes the compiled dictionary of QA Updates and
	outputs them to a readable text file
	'''

	# Output File Parameters

	today = datetime.datetime.today().strftime("%m/%d/%Y %I:%M %p")

	output_path = os.path.join(output_location, 'CDI_QA.txt'.format(today))

	# Open Output Document
	output_doc = open(output_path, 'w+')
	output_doc.write('CDI Masterlist QA Export\n\nUpdated: {}\n\n\n'.format(today))

	# Loop through updated_records write the "Before" and "After" to text file
	for updated_record in update_dict.items():
		ur_cdi_id = updated_record[0] # First item in tuple is cdi id
		ur_dict = updated_record[1] # Second item in tuple is dictionary containing all updates

		output_doc.write('CDI_ID: {}\n\n'.format(ur_cdi_id))

		for key in ur_dict.keys():
			output_doc.write('{}\n'.format(key))
			before, after = ur_dict[key] # Splits list into 2

			output_doc.write('\tInvalid: {}\n'.format(before))
			output_doc.write('\tUpdated: {}\n\n'.format(after))

		output_doc.write('\n\n\n')


	output_doc.close()

	return output_path


#################################################################################

def Export_Extra_CSV(dictionary, output_location):
	'accepts dictionary and output location, converts to csv'
	dataframe=(pd.DataFrame.from_dict(dictionary, orient='index'))
	output_path = os.path.join(output_location, 'data_gov_not_master.csv')
	dataframe.to_csv(output_path, index=False)
	return output_path

#################################################################################