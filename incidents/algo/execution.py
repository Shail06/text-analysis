from incidents.algo.predictions import Learner
from incidents.algo.initialization import Initialize


class ExecuteScenario():

    def __init__(self):
        self.learner = Learner()
        self.learner.activate_classifier()
        self.initilize = Initialize()
        self.df_input = None
        self.df_cols = None
        self.df_clean = None

    def get_column_headers(self, filename):
        ini_object = self.initilize
        self.df_input = ini_object.load_input(filename)
        self.df_cols = list(self.df_input.columns)
        return self.df_cols

    ################################
    ## The MOST IMPORTANT METHOD  ##
    ################################
    def get_predicted_dataframe(self, desc_col):
        self.df_clean = self.initilize.generate_clean_dataframe(
            self.df_input, desc_col)
        output_df = self.learner.get_predictions_probs_all(self.df_clean)
        return output_df

    def get_first_incident(self, incid_col, desc_col):
        self.df_clean = self.initilize.generate_clean_dataframe(
            self.df_input, desc_col)
        data_display, riter = self.learner.process_single_incident(
            self.df_clean, incid_col)
        return data_display, riter

    def get_next_incident(self, riter):
        return self.learner.fetch_next_row(riter)
