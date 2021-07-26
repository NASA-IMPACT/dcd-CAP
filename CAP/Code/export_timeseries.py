import os
import json

#################################################################################

def Export_Time_Series_JSON(time_series_dictionary, output_location):
	'''This function exports a consistent metric json by creating a new or 
	appending to the existing one
	'''
	
	output_path = os.path.join(output_location, "CDI_Metrics.json")

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