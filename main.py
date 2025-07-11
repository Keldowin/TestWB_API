import requests
import os
from dotenv import load_dotenv

from dataclasses import dataclass
from typing import Optional

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
                     next: int = 0) -> list['Supply']:
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
            supplies = [
                Supply(
                    id=supply['id'],
                    done=supply['done'],
                    created_at=supply['createdAt'],
                    closed_at=supply['closedAt'],
                    scan_dt=supply['scanDt'],
                    name=supply['name'],
                    cargo_type=supply['cargoType']
                )
                for supply in response.get("supplies", [])
            ]

            return supplies
        else:
            print(f'Ошибка в получении поставок, {str(response)}')

            return {}

    # Получение информации о поставке по supplyId
    # https://dev.wildberries.ru/openapi/orders-fbs#tag/Postavki-FBS/paths/~1api~1v3~1supplies~1%7BsupplyId%7D/get
    def get_supply(self,
                   supplyId: str) -> "Supply":
        """Получение информации об одной поставке по supplyId

        Args:
            supplyId (str): Пример: WB-GI-1234567 ID поставки

        Returns:
            dict: Данные об одной поставке
        """

        status, response = self._request(f'/v3/supplies/{supplyId}')

        if status:
            supply = Supply(
                id=response['id'],
                done=response['done'],
                created_at=response['createdAt'],
                closed_at=response['closedAt'],
                scan_dt=response['scanDt'],
                name=response['name'],
                cargo_type=response['cargoType']
            )

            return supply
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
    def get_coefficients_warehouses(self,
                                    warehouseIDs: str = '') -> list["SortingCenter"]:
        """Получение списка складов и их коэффициентов приёмки

        Args:
            warehouseIDs (str, optional): Список складов по их ID список 123,321,123. Defaults to ''.

        Returns:
            dict: Список складов и их коэф. приёмки
        """

        status, response = self._request('/v1/acceptance/coefficients',
                                         params={'warehouseIDs': warehouseIDs}
                                         if warehouseIDs else None,)

        if status:
            sorting_center = [
                SortingCenter(
                    date=center["date"],
                    coefficient=center.get("coefficient"),
                    warehouse_id=center["warehouseID"],
                    warehouse_name=center["warehouseName"],
                    allow_unload=center["allowUnload"],
                    box_type_name=center["boxTypeName"],
                    box_type_id=center["boxTypeID"],
                    is_sorting_center=center["isSortingCenter"]
                )
                for center in response
            ]

            return sorting_center
        else:
            print(f'Ошибка в получении коэф. поставки, {str(response)}')

            return {}

    # Получение складов приёмки
    # https://dev.wildberries.ru/openapi/orders-fbw#tag/Postavki/paths/~1api~1v1~1warehouses/get
    def get_warehouses(self) -> list["Warehouse"]:
        """Получение складов приёмки

        Returns:
            dict: Полный список складов
        """
        status, response = self._request('/v1/warehouses')

        if status:
            warehouses = [
                Warehouse(
                    id=wh["ID"],
                    name=wh["name"],
                    address=wh["address"],
                    work_time=wh["workTime"],
                    accepts_qr=wh["acceptsQR"],
                    is_active=wh["isActive"],
                    is_transit_active=wh["isTransitActive"]
                )
                for wh in response
            ]

            return warehouses
        else:
            print(f'Ошибка в получении списка складов, {str(response)}')

            return {}

    # Получение складов по их имени
    def get_warehouses_by_name(self, name_filter: str) -> list["Warehouse"]:
        """Получение списка складов по определённому имени,
        для дальнейшего использования получения коэф. приёмки

        Returns:
            Warehouse filtered: Отфильтрованный список складов с id
        """
        warehouses: list["Warehouse"] = self.get_warehouses()

        filtered = [
            warehouse
            for warehouse in warehouses
            if name_filter.lower() in warehouse.name.lower()
        ]

        return filtered

    # Получение желаемых складов приёмки, доступные для отправки и с нужным коэф. приёмки
    def get_available_coefficients_warehouses(self,
                                              coefficient: float,
                                              warehouse_name: str = '') -> list["SortingCenter"]:
        warehouses: list["SortingCenter"] = self.get_coefficients_warehouses()

        filtered_warehouses: list["SortingCenter"] = []

        for warehouse in warehouses:
            if not warehouse.allow_unload \
               or warehouse.coefficient != coefficient:
                continue

            if warehouse_name.lower() != warehouse.warehouse_name.lower():
                continue

            filtered_warehouses.append(warehouse)

        return filtered_warehouses



# Дата классы для удобного описания каждого объекта возвращаемого API
@dataclass
class Supply:
    id: str
    done: bool
    created_at: str
    closed_at: str
    scan_dt: str
    name: str
    cargo_type: int


@dataclass
class SortingCenter:
    date: str
    coefficient: Optional[float]
    warehouse_id: int
    warehouse_name: str
    allow_unload: bool
    box_type_name: str
    box_type_id: int
    is_sorting_center: bool


@dataclass
class Warehouse:
    id: int
    name: str
    address: str
    work_time: str
    accepts_qr: bool
    is_active: bool
    is_transit_active: bool


### ПРОВЕРКА!
supplies_api = WBMarketPlaceAPI(WB_API)
warehouses_api = WBSuppliesAPI(WB_API)

# # Получить все поставки
# supplies = supplies_api.get_supplies(limit=4)
# print(supplies)

print('================')

# Получить конкретную поставку
supply = supplies_api.get_supply(supplyId="WB-GI-166688565") # Поставка Test supply_1
print(supply)

print('======== ДРУГОЙ КЛАСС ========')

# Поиск сортировочных центров по имени
centers = warehouses_api.get_warehouses_by_name("Брянск")
print(centers)

print('================')

# Получить все склады
warehouses = warehouses_api.get_warehouses()
print(warehouses)

print('================')

# Получить все склады и их коэф. приёмки
coef = warehouses_api.get_coefficients_warehouses()
print(coef)

print('================')

# Получить опред склады и их коэф по warehousesIDS
coef_filtered = warehouses_api.get_coefficients_warehouses(warehouseIDs='302988,215020,301760')
print(coef_filtered)

# Склады уд. коэф приёмки
available_warehouses = warehouses_api.get_available_coefficients_warehouses(1, 'Коледино')
print(available_warehouses)