import requests
import os

def get_crypto_ranking():
    """
    CoinRanking APIを使用して仮想通貨ランキングを取得する関数
    """
    api_key = os.getenv('COINRANKING_API_KEY')
    url = "https://api.coinranking.com/v2/coins"
    headers = {
        'x-access-token': api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Could not retrieve crypto rankings"}
