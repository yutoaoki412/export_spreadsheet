from google.cloud import bigquery
import gspread
from gspread_dataframe import set_with_dataframe
from google.auth import default

class BigQueryClient:
    def __init__(self, project_id):
        self.client = bigquery.Client(project=project_id)

    def execute_query(self, query):
        query_job = self.client.query(query)
        return query_job.to_dataframe()

    def execute_query_from_file(self, query_file_path, start_date, end_date):
        with open(query_file_path, 'r') as file:
            query_template = file.read()
        formatted_query = query_template.format(start_date=start_date, end_date=end_date)
        return self.execute_query(formatted_query)

class GoogleSheetsClient:
    def __init__(self):
        credentials, _ = default()
        self.client = gspread.authorize(credentials)

    def write_data_to_spreadsheet(self, spreadsheet_id, data_frame, worksheet_title):
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        try:
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="1", cols="1")
        except gspread.exceptions.APIError:
            worksheet = spreadsheet.worksheet(worksheet_title)
            spreadsheet.del_worksheet(worksheet)
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="1", cols="1")
        set_with_dataframe(worksheet, data_frame)
        return worksheet_title

class GoogleAPIHandler:
    def __init__(self, project_id):
        self.bigquery_client = BigQueryClient(project_id)
        self.sheets_client = GoogleSheetsClient()

    def run_query(self, query):
        return self.bigquery_client.execute_query(query)

    def run_query_from_file(self, query_file_path, start_date, end_date):
        return self.bigquery_client.execute_query_from_file(query_file_path, start_date, end_date)

    def save_to_spreadsheet(self, spreadsheet_id, data_frame, worksheet_title):
        return self.sheets_client.write_data_to_spreadsheet(spreadsheet_id, data_frame, worksheet_title)