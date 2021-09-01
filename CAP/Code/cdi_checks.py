import os
import requests

#################################################################################

'''
All the Functions in this section are in relation to the cdi_validator.py CDI_masterlist_QA function
- check_name_and_update_caturl
- check_title
- check_organization
- check_metadata_type
- check_climate_tag
- check_cdi_themes (Not Currently Needed)
'''

#################################################################################

def url_checker(url):
	'''This function checks and url for its current status
	'''
	try:
		status = requests.get(url).status_code

		if status == 200:
			working = True
		else:
			working = False
	except requests.ConnectionError as e:
		working = False

	return working

#################################################################################

def check_catalog_url_status(cdi_dataset, catalog_change_list):

	# Check Catalog_Url Status
	cat_url = cdi_dataset.catalog_url
	url_status = url_checker(cat_url)

	if url_status == True:
		return catalog_change_list
	else:
		cdi_dataset.update_catalog_url("broken")
		return [cat_url,"broken"]

#################################################################################

def check_name_and_update_caturl(cdi_dataset, api_json):

	# Check name & update caturl if name change
	api_name = api_json['result']['name']
	cdi_name = cdi_dataset.name
	cdi_catalog_url = cdi_dataset.catalog_url
	

	if cdi_name == api_name:
		return [None, None] # Necessary since success requires multiple assignment
	else:
		cdi_dataset.update_name(api_name) # Updates Name Value

		new_caturl = 'https://catalog.data.gov/dataset/{}'.format(api_name) # Creates new Catalog URL

		cdi_dataset.update_catalog_url(new_caturl) # Updates Catalog URL Value

		return[[cdi_name, api_name],[cdi_catalog_url, new_caturl]]

#################################################################################

def check_title(cdi_dataset, api_json):

	# Check title
	api_title = api_json['result']['title']
	cdi_title = cdi_dataset.title

	if cdi_title == api_title:
		return None
	else:
		cdi_dataset.update_title(api_title) # Updates Name Value

		return [cdi_title, api_title]

#################################################################################

def check_organization(cdi_dataset, api_json):
	#Check organization
	api_org = api_json['result']['organization']['name']
	cdi_org = cdi_dataset.organization

	if cdi_org == api_org:
		return None
	else:
		cdi_dataset.update_organization(api_org) # Updates Name Value

		return [cdi_org, api_org]

#################################################################################

def check_metadata_type(cdi_dataset, api_json):
	api_extras = api_json['result']['extras']
	cdi_metadata_type = cdi_dataset.metadata_type
	found_key = False
	for i in range(len(api_extras)):
		extra_key = api_extras[i]['key']
		api_extra_value = api_extras[i]['value']

		if extra_key == 'metadata_type':
			found_key=True
			if cdi_metadata_type == api_extra_value:
				return None
			else:
				cdi_dataset.update_metadata_type(api_extra_value)

				return [cdi_metadata_type, api_extra_value]
	if found_key == False and cdi_metadata_type != 'No metadata type':
		cdi_dataset.update_metadata_type('No metadata type')
		return [cdi_metadata_type, 'No metadata type']

#################################################################################

def check_datagov_id(cdi_dataset):
	api_url = cdi_dataset.api_url
	datagov_id = cdi_dataset.datagov_ID
	
	api_url_id = api_url.replace("https://catalog.data.gov/api/3/action/package_show?id=", "")

	if datagov_id == api_url_id:
		return None
	else:
		cdi_dataset.update_datagov_ID(api_url_id)
		return [datagov_id, api_url_id]


#################################################################################

def check_climate_tag(cdi_dataset, api_json):
	# Check Tag

	if not api_json['result']['groups'] or not any(d['name']=='climate5434' for d in api_json['result']['groups']):
		cdi_dataset.update_climate_tag_status(False)
	else:
		cdi_dataset.update_climate_tag_status(True)

	'''
	api_groups = api_json['result']['groups']

	for i in range(len(api_groups)):
		api_group_name = api_groups[i]['name']

		if api_group_name == 'climate5434':
			cdi_dataset.update_climate_tag_status(True)
			return

	cdi_dataset.update_climate_tag_status(False)
	'''

#################################################################################
# Not Currently Needed
'''
def check_cdi_themes(cdi_dataset, api_json):
	api_extras = api_json['result']['extras']

	for i in range(len(api_extras)):
		extra_key = api_extras[i]['key']
		api_extra_value = api_extras[i]['value']
		#print(extra_key, api_extra_value)

		if 'category_tag' in extra_key:
			
			cdi_compare_value = str(cdi_dataset.cdi_themes.split(';')[0])

			if str(cdi_compare_value) == str(api_extra_value):
				return None
			else:
				cdi_dataset.update_cdi_themes(api_extra_value)
'''
			
#################################################################################