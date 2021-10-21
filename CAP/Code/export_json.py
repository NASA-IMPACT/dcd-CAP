import os
import json

#################################################################################

def Export_Object_to_JSON(cdi_datasets, output_location=False, filename=False, broken=False):
	'''This function takes all of the CDI Dataset objects (original)
	and exports them as the full Original JSON
	'''

	# Check Optional Parameters
	if broken:
		if len(cdi_datasets) == 0:
			return "No Broken Datasets Found"

	# Convert objects into JSON
	
	list_of_datasets = [] # Initialize list of dataset dictionaries (or json)

	for dataset in cdi_datasets:

		dataset_dict = dataset.export_dictionary() # Exports Dataset contents in dictionary

		list_of_datasets.append(dataset_dict)

	output_json = json.dumps(list_of_datasets, indent=4)

	if output_location:
		# Set Outfile parameters
		output_path = os.path.join(output_location, filename)

		with open(output_path, 'w+') as outfile:
			outfile.write(output_json)

		return output_path

	return output_json

#################################################################################

def Export_Object_to_Dict(cdi_datasets):
	# Convert objects into JSON
	
	list_of_datasets = [] # Initialize list of dataset dictionaries (or json)

	for dataset in cdi_datasets:

		dataset_dict = dataset.export_dictionary() # Exports Dataset contents in dictionary

		list_of_datasets.append(dataset_dict)

	return list_of_datasets


#################################################################################

def Export_Time_Series_JSON(time_series_dictionary, output_location):
	'''This function exports a consistent metric json by creating a new or 
	appending to the existing one
	'''
	
	output_path = os.path.join(output_location, 'CDI_Metrics.json')

	try: # Will Try to add to existing Metric File

		with open(output_path) as archive_file:
			archive_json = json.load(archive_file)
		
		# Make sure the same time is only in the json once

		for instance in archive_json:

			if instance["Date"] == time_series_dictionary["Date"]:
				return output_path
			else:
				continue

		# Adds New to Archive and Writes Files

		archive_json.append(time_series_dictionary)
		output_json = json.dumps(archive_json, indent=4)

		with open(output_path, 'w+') as writefile:
			writefile.write(output_json)

	
	except: # Will create new metric file if it does not exist

		output_json = json.dumps([time_series_dictionary], indent=4) # For Formatting

		with open(output_path, 'w+') as writefile:
			writefile.write(output_json)
	
	return output_path


#################################################################################

def Export_List_of_Dict_JSON(input_list_dict, output_location, filename, broken=False):
	'''This function takes any input list of dictionaries and outputs them into a 
	JSON format with the provied output_location and filename
	'''
	
	# Check Optional Parameters
	if broken:
		if len(input_list_dict) == 0:
			return "No Broken Datasets Found"

	output_path = os.path.join(output_location, filename)

	# Convert List of Dictionaries to JSON

	output_json = json.dumps(input_list_dict, indent=4)

	# Output JSON

	with open(output_path, 'w+') as outfile:
		outfile.write(output_json)

	return output_path


#################################################################################

def Export_Warnings_Summary_JSON(warnings_dictionary, output_location):
	'''This function exports a warnings summary json by creating a new file or 
	appending to the existing one
	'''
	
	output_path = os.path.join(output_location, "Warnings_Summary.json")

	try: # Will Try to add to existing Metric File

		with open(output_path) as archive_file:
			archive_json = json.load(archive_file)
		
		# Make sure the same time is only in the json once

		for instance in archive_json:

			if instance["Date"] == warnings_dictionary["Date"]:
				return output_path
			else:
				continue

		# Adds New to Archive and Writes Files

		archive_json.append(warnings_dictionary)
		output_json = json.dumps(archive_json, indent=4)

		with open(output_path, 'w+') as writefile:
			writefile.write(output_json)

	
	except: # Will create new metric file if it does not exist

		output_json = json.dumps([warnings_dictionary], indent=4) # For Formatting

		with open(output_path, 'w+') as writefile:
			writefile.write(output_json)
	
	return output_path

############################################################################################

