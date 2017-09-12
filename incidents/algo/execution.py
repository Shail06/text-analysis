from incidents.algo.predictions import Learner
from incidents.algo.initialization import Initialize


class ExecuteScenario():

    def __init__(self):
        self.learner = Learner()
        self.initilize = Initialize()

    def get_column_headers(self, filename):
        ini_object = self.initilize
        df_input = ini_object.load_input('uploads/' + uploaded_file)
