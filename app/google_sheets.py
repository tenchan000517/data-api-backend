# google_sheets.py

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_service():
    try:
        service_account_info = json.loads(os.getenv('REACT_APP_SERVICE_ACCOUNT_INFO2'))
        creds = service_account.Credentials.from_service_account_info(service_account_info)
        logger.debug(f"Google API Key: {creds}")
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        raise RuntimeError(f"Failed to create Google Sheets service: {str(e)}")

def get_sheet_values(sheet_id, range_name):
    service = get_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    logger.debug(f"Fetched sheet values for range {range_name}: {values}")
    return values

def save_data_to_sheet(sheet_id, sheet_name, data, data_type):
    service = get_service()
    sheet = service.spreadsheets()
    
    range_name = f'{sheet_name}!A1'
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    existing_values = result.get('values', [])
    
    # Create header if not exists
    if not existing_values:
        headers = ['タイムスタンプ'] + list(data[0].keys())
        sheet.values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
    
    # Add new data
    range_name = f'{sheet_name}!A{len(existing_values) + 1}'
    timestamp = datetime.now().isoformat()
    logger.debug(f"Data to be saved: {data}")

    values = [[timestamp] + list(item.values()) for item in data]
    logger.debug(f"Saving data to sheet {sheet_name}: {values}")
    sheet.values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': values}
    ).execute()