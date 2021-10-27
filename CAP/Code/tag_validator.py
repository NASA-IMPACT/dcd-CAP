import os
import pandas as pd
import xlsxwriter
import openpyxl

#################################################################################

def Climate_Tag_Check(cdi_dataset):
	'''Checks the CDI Dataset Object's climate tag value and
	returns Boolean value
	'''
	
	# Checks for Climate Tag and gives True/False value for cdi_dataset.climate_tag
	Check_Tag_Status(cdi_dataset)

	climate_bool = cdi_dataset.climate_tag

	if climate_bool == True:
		return False
	elif climate_bool == False:
		return cdi_dataset

#################################################################################

def Check_Tag_Status(cdi_dataset):

	# Check Climate Tag

	api_json = cdi_dataset.full_api_json
	
	api_groups = api_json['result']['groups']

	for i in range(len(api_groups)):
		api_group_name = api_groups[i]['name']

		if api_group_name == 'climate5434':
			cdi_dataset.update_climate_tag_status(True)
			return

	cdi_dataset.update_climate_tag_status(False)

#################################################################################

def Format_Retag_Request_Excel(path_to_document):
	'''This function formats the created excel file by: 
	Adjusting column width and applying "Wrap Text" styling
	'''

	workbook = openpyxl.load_workbook(path_to_document)

	worksheet = workbook.active

	# set the width of each column
	worksheet.column_dimensions['A'].width = 35
	worksheet.column_dimensions['B'].width = 65
	worksheet.column_dimensions['C'].width = 55
	worksheet.column_dimensions['D'].width = 55

	for row in worksheet.iter_rows():
		for cell in row:      
			cell.alignment = openpyxl.styles.Alignment(wrapText=True)
  
	# save the file
	workbook.save(path_to_document)

#################################################################################

def Export_Retag_Request(cdi_datasets, output_location, filename):
	'''This function takes the cdi objects that do not have the climate tag and
	outputs them to an excel file
	'''
	
	# Set Outfile parameters

	output_path = os.path.join(output_location, filename)

	output_json = [] # Initialize list of dataset dictionaries (or json)

	for notag_dataset in cdi_datasets:

		dataset_dict = notag_dataset.export_dictionary() # Exports Dataset contents in dictionary

		# Filter/Recreate OutputJson for desired output
		filter_dict = {'id':dataset_dict['datagov_ID'], 
						'Dataset Name': dataset_dict['name'],
						'Data.gov URL':dataset_dict['catalog_url'], 
						'CDI Theme':dataset_dict['cdi_themes']}

		output_json.append(filter_dict)

	# Convert Output Json to Pandas DataFrame
	output_df = pd.DataFrame(output_json)

	# Create Excel Writer and export document
	writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

	output_df.to_excel(writer, sheet_name='Retag Request', index=False)

	writer.save()

	Format_Retag_Request_Excel(output_path)

	return output_path

#################################################################################