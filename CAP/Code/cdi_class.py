import urllib
import requests
import json

class CDI_Dataset:

	def __init__(self, dataset, date):
		'''Parameter "dataset" is expected to be python dictionary type'''

		self.date_id = date
		self.cdi_id = dataset['cdi_id']
		self.name = dataset['name']
		self.title = dataset['title']
		self.organization = dataset['organization']
		self.catalog_url = dataset['catalog_url']
		self.api_url = dataset['api_url']
		self.cdi_themes = dataset['cdi_themes']
		self.metadata_type = dataset['metadata_type']
		self.geoplatform_id = dataset['geoplatform_id']
		self.is_active = dataset['is_active']
		self.datagov_ID = dataset['datagov_ID']
		self.load_api_json()

	def __str__(self):
		return "{}".format(self.datagov_ID)

	def load_api_json(self):
		'''This method loads the API URL json - if the link is broken it 
		will apply a "broken" value to the full_api_json attribute'''
		
		api_url = self.api_url
		try:
			api_request = urllib.request.urlopen(api_url)
			api_json = json.load(api_request)
			self.full_api_json = api_json

		except urllib.error.HTTPError:
			self.full_api_json = "Broken"

	def update_cdi_id(self, new_value):
		self.cdi_id = new_value

	def update_name(self, new_value):
		self.name = new_value

	def update_title(self, new_value):
		self.title = new_value

	def update_organization(self, new_value):
		self.organization = new_value

	def update_catalog_url(self, new_value):
		self.catalog_url = new_value

	def update_metadata_type(self, new_value):
		self.metadata_type = new_value

	def update_cdi_themes(self, new_value):
		self.cdi_themes = new_value

	def update_is_active(self, new_value):
		self.is_active = new_value

	def update_datagov_ID(self, new_value):
		self.datagov_ID = new_value

	def update_climate_tag_status(self, new_value):
		self.climate_tag = new_value


	def export_dictionary(self):
		'''This method exports the cdi_object into a dictionary (json)'''

		dataset_dict = {}

		dataset_dict['date_id'] = self.date_id
		dataset_dict['cdi_id'] = self.cdi_id
		dataset_dict['name'] = self.name
		dataset_dict['title'] = self.title
		dataset_dict['organization'] = self.organization
		dataset_dict['catalog_url'] = self.catalog_url
		dataset_dict['api_url'] = self.api_url
		dataset_dict['cdi_themes'] = self.cdi_themes
		dataset_dict['metadata_type'] = self.metadata_type
		dataset_dict['geoplatform_id'] = self.geoplatform_id
		dataset_dict['is_active'] = self.is_active 
		dataset_dict['datagov_ID'] = self.datagov_ID

		return dataset_dict


