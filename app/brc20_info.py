import requests

def get_brc20_token_id(symbol):
    """
    BRC20トークンのIDを取得する関数
    """
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        coins_list = response.json()
        for coin in coins_list:
            if coin['symbol'] == symbol.lower():
                return coin['id']
    return None

def get_brc20_info(symbol):
    """
    BRC20トークンの情報を取得する関数
    """
    token_id = get_brc20_token_id(symbol)
    if not token_id:
        return {"error": f"Token with symbol '{symbol}' not found"}
    
    url = f"https://api.coingecko.com/api/v3/coins/{token_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Could not retrieve information for token ID '{token_id}'"}
