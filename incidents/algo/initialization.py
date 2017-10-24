
import pandas as pd
from incidents.models import knowledge
from incidents.algo import cleaning
import xlrd
import cython


class Initialize:

    # Get all the columns names to show on webpage for user to select
    def load_input(self, filename):
        # pd.read_csv(filename,  sep = ',', encoding = 'ISO-8859-1')
        excel_file = pd.ExcelFile(filename)
        df_input_raw = excel_file.parse(excel_file.sheet_names[0])
        df_input_raw = df_input_raw.dropna(how="all")
        df_input_raw = df_input_raw.fillna(0)
        return df_input_raw

    # From the column names selected by user, generate a clean input Data frame
    def generate_clean_dataframe(self, df_input_raw, desc_cols):
        df_clean_input = df_input_raw
        df_input_raw['machine_combined_desc'] = df_input_raw[desc_cols].apply(
            lambda x: ' \n '.join(x.astype(str)), axis=1)

        generate_summary = lambda incident_row: cleaning.get_clean_text(incident_row[
                                                                        'machine_combined_desc'])
        df_clean_input['machine_summary'] = df_input_raw.apply(
            generate_summary, axis=1)
        return df_clean_input

    # Load the Summary and Label from Knowledge
    def load_knowledge(self):
        knowledge_df = pd.DataFrame(
            list(knowledge.objects.all().values('summary', 'label')))
        return knowledge_df
