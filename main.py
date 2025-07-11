import requests
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

WB_API = os.getenv('WB_API')
URL_API = 'https://marketplace-api.wildberries.ru/api'


# Возвращаем 1 поставку
def get_supply_info() -> dict:
    url = f"{URL_API}/v3/supplies"
    headers = {'Authorization': WB_API}
    params = {'limit': 1, 'next': 143021301}

    response = requests.get(url,
                            params,
                            headers=headers)

    if response.status_code == 200:
        supply_data = response.json()
        return supply_data
    else:
        print('Ошибка в запросе поставки')


def get_supply_orders(supply_id: str) -> dict:
    url = f"{URL_API}/v3/supplies/{supply_id}/orders"
    headers = {'Authorization': WB_API}

    response = requests.get(url,
                            headers=headers)

    if response.status_code == 200:
        supply_data = response.json()
        return supply_data
    else:
        print(f'Ошибка в запросе поставки {response.status_code}')


print(get_supply_orders('WB-GI-166688607'))