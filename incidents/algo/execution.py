from incidents.algo.predictions import Learner
from incidents.algo.initialization import Initialize
import cython

class ExecuteScenario():

    def __init__(self):
        self.learner = Learner()
        self.learner.activate_classifier()
        self.initialize = Initialize()
        self.df_input = None
        self.df_cols = None
        self.df_clean = None

    def get_input_dataframe(self, filename):
        self.df_input = self.initialize.load_input(filename)
        return self.df_input

    def get_column_headers(self, filename):
        ini_object = self.initialize
        self.df_input = ini_object.load_input(filename)
        self.df_cols = list(self.df_input.columns)
        return self.df_cols

    ################################
    ## The MOST IMPORTANT METHOD  ##
    ################################
    def get_predicted_dataframe(self, desc_col):
        self.learner.knowledge_df = self.initialize.load_knowledge() # To load the knowledge after any updates
        self.learner.activate_classifier()
        self.df_clean = self.initialize.generate_clean_dataframe(
            self.df_input, desc_col)
        output_df = self.learner.get_predictions_probs_all(self.df_clean)
        return output_df

    def get_prediction_statistics(self, df_output, incid_col):
        c_stats = self.learner.get_prediction_stats(df_output, incid_col)
        stat_list = []
        for index, value in c_stats.items():
            stat_list.append([index, value])
        return c_stats, stat_list

    def save_to_knowledge(self, summary, label):
        self.learner.enhance_knowledge(summary, label)

    def save_output(self, df_output, filename):
        self.learner.save_output(df_output, filename)

    def get_first_incident(self, incid_col, desc_col):
        self.df_clean = self.initialize.generate_clean_dataframe(
            self.df_input, desc_col)
        data_display, riter = self.learner.process_single_incident(
            self.df_clean, incid_col)
        return data_display, riter

    def get_next_incident(self, riter):
        return self.learner.fetch_next_row(riter)
