import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ORDISCAN_API_KEY = os.getenv('ORDISCAN_API_KEY')

def get_brc20_token_info(tick):
    url = f"https://api.ordiscan.com/v1/brc20/{tick}"
    headers = {
        "Authorization": f"Bearer {ORDISCAN_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    logger.debug(f"Ordiscan API response: {response.text}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        logger.error(f"Failed to fetch BRC-20 token info: {response.status_code} {response.text}")
        return {"error": "Failed to fetch BRC-20 token info"}

def get_brc20_balances(bitcoin_address):
    url = f"https://api.ordiscan.com/v1/address/{bitcoin_address}/brc20"
    headers = {
        "Authorization": f"Bearer {ORDISCAN_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    logger.debug(f"Ordiscan API response: {response.text}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        logger.error(f"Failed to fetch BRC-20 balances: {response.status_code} {response.text}")
        return {"error": "Failed to fetch BRC-20 balances"}

def get_rune_market_info(name):
    url = f"https://api.ordiscan.com/v1/rune/{name}/market"
    headers = {
        "Authorization": f"Bearer {ORDISCAN_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    logger.debug(f"Ordiscan API response: {response.text}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        logger.error(f"Failed to fetch Rune market info: {response.status_code} {response.text}")
        return {"error": "Failed to fetch Rune market info"}

def get_brc20_transfer_activity(inscription_id):
    url = f"https://api.ordiscan.com/v1/inscription/{inscription_id}/activity"
    headers = {
        "Authorization": f"Bearer {ORDISCAN_API_KEY}"
    }
    response = requests.get(url, headers=headers)
    logger.debug(f"Ordiscan API response: {response.text}")
    if response.status_code == 200:
        return response.json()['data']
    else:
        logger.error(f"Failed to fetch BRC-20 transfer activity: {response.status_code} {response.text}")
        return {"error": "Failed to fetch BRC-20 transfer activity"}
