import os
import json

#################################################################################

def Export_Update_CDI_JSON(cdi_datasets, output_location):
	'''This function takes all of the CDI Dataset objects (updated)
	and exports them as the full Updated JSON
	'''

	# Set Outfile parameters

	output_path = os.path.join(output_location, 'updated_CDI_Masterlist.json')

	# Convert objects into JSON
	
	list_of_datasets = [] # Initialize list of dataset dictionaries (or json)

	for dataset in cdi_datasets:

		dataset_dict = dataset.export_dictionary() # Exports Dataset contents in dictionary

		list_of_datasets.append(dataset_dict)

	output_json = json.dumps(list_of_datasets, indent=4)

	with open(output_path, 'w+') as outfile:
		outfile.write(output_json)

	return output_path

#################################################################################