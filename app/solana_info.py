import requests

def get_collections(offset=0, limit=200):
    """
    SolanaのMagicEden APIを使用してコレクション情報を取得する関数
    """
    url = "https://api-mainnet.magiceden.dev/v2/collections"
    headers = {
        "accept": "application/json"
    }
    params = {
        "offset": offset,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Could not retrieve collections, status code: {response.status_code}"}
