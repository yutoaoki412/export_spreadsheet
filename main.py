from pathlib import Path
import yaml
from google_api_handler import GoogleAPIHandler
from utils import get_daily_date_range, get_weekly_date_range, get_monthly_date_range

BASE_DIR = Path(__file__).resolve().parent

def load_config():
    with open(BASE_DIR / 'config.yml', 'r') as file:
        return yaml.safe_load(file)

def execute_export(frequency, date_range_func):
    config = load_config()
    project_id = config['project_id']
    api_handler = GoogleAPIHandler(project_id)
    start_date, end_date = date_range_func()

    for query in config['queries'][frequency]:
        query_file_path = BASE_DIR / query['file']
        sheet_id = query['sheet_id']
        
        try:
            query_result = api_handler.run_query_from_file(query_file_path, start_date, end_date)
            new_sheet_name = api_handler.save_to_spreadsheet(
                sheet_id, query_result, f"{start_date.strftime('%Y年%m月%d日分')}"
            )
            print(f"{query['file']}: {new_sheet_name}の作成が完了しました。")
        except Exception as e:
            print(f"エラー: {query['file']} の処理中にエラーが発生しました: {e}")

def monthly_export(event, context):
    execute_export('monthly', get_monthly_date_range)

def weekly_export(event, context):
    execute_export('weekly', get_weekly_date_range)

def daily_export(event, context):
    execute_export('daily', get_daily_date_range)

if __name__ == "__main__":
    monthly_export(None, None)