import requests
import logging
from .google_sheets import get_sheet_values, save_data_to_sheet
from .transform_data import transform_data
import time

logger = logging.getLogger(__name__)

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
    logger.debug(f"Fetching BRC20 info from: {url}")

    response = requests.get(url)
    logger.debug(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Could not retrieve information for token ID '{token_id}'"}
    
def fetch_brc20_data_from_presets(sheet_id):
    """
    PresetsシートからBRC20データを取得する関数
    """
    try:
        # Google Sheetsのシート「Presets」からデータを取得します。例として100行まで取得します。
        presets = get_sheet_values(sheet_id, 'Presets!A1:F100')

        # 取得した各行について処理を行います。
        for row in presets:
            # A列が 'brc20' である場合のみ処理を行います。
            if row[0].lower() == 'brc20':
                # D列の値（symbol）を取得します。
                symbol = row[3]

                # 取得した symbol を使用して、CoinGecko APIのURLを作成します。
                url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
                
                # 作成したURLに対してGETリクエストを送信します。
                response = requests.get(url)
                
                # レスポンスのステータスコードが200（成功）であることを確認します。
                if response.status_code == 200:
                    # レスポンスのJSONデータを取得します。
                    data = response.json()
                    
                    # デバッグログとして取得したデータを出力します。
                    logger.debug(f"Fetched BRC20 data: {data}")
                    
                    # 取得したデータを変換します。
                    transformed_data = transform_data(data, 'brc20')
                    logger.debug(f"Transformed BRC20 data: {transformed_data}")

                    # 変換したデータをGoogle Sheetsに保存します。
                    save_data_to_sheet(sheet_id, 'BRC20', transformed_data, 'brc20')
                else:
                    # レスポンスのステータスコードが200でない場合、エラーログを出力します。
                    logger.error(f"Failed to retrieve information for symbol '{symbol}': {response.status_code}")
                
                # リクエスト後に30秒待機します。
                time.sleep(30)
            else:
                # A列が 'brc20' でない場合は処理をスキップし、デバッグログを出力します。
                logger.debug(f"Skipping non-brc20 row: {row}")
                
    except Exception as e:
        # 例外が発生した場合、エラーログを出力します。
        logger.error(f"Failed to fetch BRC20 data: {str(e)}")
