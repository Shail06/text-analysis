from django.conf import settings
import sqlite3
import pandas as pd


class PopulateDB():

    def __init__(self):
        self.database_name = settings.DATABASES['default']['NAME']
        self.conn = sqlite3.connect(self.database_name)
        self.cur = self.conn.cursor()

    def fill_table(self, output_dataframe, table_name):
        output_dataframe.to_sql(
            table_name, con=self.conn, if_exists="replace")

    def get_table_as_dataframe(self, table_name):
        #res =  self.cur.execute("SELECT * FROM " + table_name)
        df_output = pd.read_sql_query("SELECT * FROM " + table_name, self.conn)
        return  df_output

    def delete_table(self, table_name):
        self.cur.execute("DROP TABLE " + table_name)

    def table_exists(self, table_name):
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='"+table_name+"';")
        if(len(res.fetchall()) == 0):
            return False
        else:
            return True
