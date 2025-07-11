import requests
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

WB_API = os.getenv('WB_API')


# Родительский класс для всех методов запроса к WB API
class WBAPI():
    def __init__(
            self,
            key: str = None,
    ):
        self.base_url = 'https://marketplace-api.wildberries.ru/api'
        self._headers = {
            'Authorization': key,
            'Content-Type': 'application/json',
        }

        self._key = key

    def _request(self,
                 method: str,
                 params: dict = None) -> tuple[bool, any]:
        url = self.base_url + method

        try:
            response = requests.get(
                url=url,
                headers=self._headers,
                params=params,
            )

            response_data = response.json()

            if response.status_code == 200:
                return True, response_data
            else:
                print(f'Ошибка в осуществлении запроса в методе: {method}, {str(response.status_code)}')

                return False, response_data
        except Exception as ex:
            print(f'Ошибка в осуществлении запроса в методе: {method}, {ex}')

            return False, str(ex)


# API методы для запроса в marketplace-api
class WBMarketPlaceAPI(WBAPI):
    def __init__(
            self,
            key: str = None,
    ):
        super().__init__(key)

        self.base_url = 'https://marketplace-api.wildberries.ru/api'

    # Получение списка поставок
    # https://dev.wildberries.ru/openapi/orders-fbs#tag/Postavki-FBS/paths/~1api~1v3~1supplies/get
    def get_supplies(self,
                     limit: int = 1,
                     next: int = 0) -> dict:
        """Получение списка поставок

        Args:
            limit (int, optional): Параметр пагинации. Устанавливает предельное количество возвращаемых данных. Defaults to 1.
            next (int, optional): Параметр пагинации. Устанавливает значение, с которого надо получить следующий пакет данных. Для получения полного списка данных должен быть равен 0 в первом запросе. Для следующих запросов необходимо брать значения из одноимённого поля в ответе. Defaults to 0.

        Returns:
            dict: Список поставок
        """

        status, response = self._request('/v3/supplies',
                                         params={'limit': limit,
                                                 'next': next})

        if status:
            return response
        else:
            print(f'Ошибка в получении поставок, {str(response)}')

            return {}

    # Получение информации о поставке по supplyId
    # https://dev.wildberries.ru/openapi/orders-fbs#tag/Postavki-FBS/paths/~1api~1v3~1supplies~1%7BsupplyId%7D/get
    def get_supply(self,
                   supplyId: str) -> dict:
        """Получение информации об одной поставке по supplyId

        Args:
            supplyId (str): Пример: WB-GI-1234567 ID поставки

        Returns:
            dict: Данные об одной поставке
        """

        status, response = self._request(f'/v3/supplies/{supplyId}')

        if status:
            return response
        else:
            print(f'Ошибка в получении информации о поставке, {str(response)}')

            return {}


# API методы для запроса в supplies-api
class WBSuppliesAPI(WBAPI):
    def __init__(
            self,
            key: str = None,
    ):
        super().__init__(key)

        self.base_url = 'https://supplies-api.wildberries.ru/api'

    # Получение коэф. приёмки
    # https://dev.wildberries.ru/openapi/orders-fbw#tag/Postavki/paths/~1api~1v1~1acceptance~1coefficients/get
    def get_coefficients(self,
                         warehouseIDs: str = '') -> dict:
        """Получение списка складов и их коэффициентов приёмки

        Args:
            warehouseIDs (str, optional): Список складов по их ID список 123,321,123. Defaults to ''.

        Returns:
            dict: Список складов и их коэф. приёмки
        """

        if warehouseIDs:
            status, response = self._request('/v1/acceptance/coefficients',
                                             params={
                                                 'warehouseIDs': warehouseIDs
                                                 })
        else:
            status, response = self._request('/v1/acceptance/coefficients')

        if status:
            return response
        else:
            print(f'Ошибка в получении коэф. поставки, {str(response)}')

            return {}

    # Получение складов приёмки
    # https://dev.wildberries.ru/openapi/orders-fbw#tag/Postavki/paths/~1api~1v1~1warehouses/get
    def get_warehouses(self) -> dict:
        """Получение складов приёмки

        Returns:
            dict: Полный список складов
        """
        status, response = self._request('/v1/warehouses')

        if status:
            return response
        else:
            print(f'Ошибка в получении списка складов, {str(response)}')

            return {}

supply_requests = WBMarketPlaceAPI(WB_API)

print(supply_requests.get_supplies(limit=4))

warehouses = WBSuppliesAPI(WB_API)

print(warehouses.get_warehouses())