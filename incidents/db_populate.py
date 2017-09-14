from django.conf import settings
import sqlite3


class PopulateDB():

    def __init__(self):
        self.database_name = settings.DATABASES['default']['NAME']
        self.conn = sqlite3.connect(self.database_name)
        self.cur = self.conn.cursor()

    def fill_table(self, output_dataframe, table_name):
        output_dataframe.to_sql(
            table_name, con=self.conn, if_exists="replace")

    def get_rows(self, table_name):
        return self.cur.execute("SELECT * FROM " + table_name)

    def delete_table(self, table_name):
        self.cur.execute("DROP TABLE " + table_name)
