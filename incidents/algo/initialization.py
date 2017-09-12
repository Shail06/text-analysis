
import pandas as pd
from incidents.models import knowledge
from incidents.algo import cleaning

class Initialize:

	# Get all the columns names to show on webpage for user to select
	def load_input(self, filename):
		df_input_raw = pd.read_csv(filename,  sep = ',', encoding = 'ISO-8859-1')
		return df_input_raw

	# From the column names selected by user, generate a clean input Data frame
	def generate_clean_dataframe(self, df_input_raw, desc_cols):
		df_clean_input                     = df_input_raw
		df_input_raw['combined_desc']      = df_input_raw[desc_cols].apply(lambda x: ' '.join(x.astype(str)),axis=1)
		generate_summary                   = lambda incident_row: cleaning.get_clean_text(incident_row['combined_desc'])
		df_clean_input['summary']            = df_input_raw.apply(generate_summary , axis=1)
		return df_clean_input

	# Load the Summary and Label from Knowledge
	def load_knowledge(self):
		knowledge_df = pd.DataFrame(list(knowledge.objects.all().values('summary','label')))
		return knowledge_df


