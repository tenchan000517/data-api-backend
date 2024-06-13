from apscheduler.schedulers.background import BackgroundScheduler
from .google_sheets import get_sheet_values, save_data_to_sheet
from .data_fetcher import fetch_data_from_presets
import logging

logger = logging.getLogger(__name__)

def fetch_and_save_data():
    sheet_id = '1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk'
    presets = get_sheet_values(sheet_id, 'Presets!A1:F20')
    logger.debug(f"Presets fetched: {presets}")

    # 全てのデータを取得
    data = fetch_data_from_presets(presets)
    
    if data['nft']:
        save_data_to_sheet(sheet_id, 'nft', data['nft'], 'nft')
    if data['ordinals']:
        save_data_to_sheet(sheet_id, 'ordinals', data['ordinals'], 'ordinals')
    if data['brc20']:
        logger.debug("Saving BRC20 data to sheet")
        save_data_to_sheet(sheet_id, 'brc20', data['brc20'], 'brc20')

def start_scheduler():
    try:
        scheduler = BackgroundScheduler()
        sheet_id = '1B4X_by7BD2ROPsXHNmgTsCyIultzcy1425JNKEYvbNk'  # シートIDを指定
        setting_values = get_sheet_values(sheet_id, 'Setting!B2')  # 設定時間をB2セルから取得
        schedule_time = setting_values[0][0]  # 設定時間を取得
        hour, minute = map(int, schedule_time.split(':'))

        # メインのデータ取得ジョブ
        scheduler.add_job(fetch_and_save_data, 'cron', hour=hour, minute=minute)

        scheduler.start()
        
        logger.info(f"Scheduler started to run at {schedule_time} every day.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
