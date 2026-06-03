from abc import ABC, abstractmethod
import requests
from typing import Dict, List, Any


class AbstractAPIClient(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def get_data(self, **kwargs: Any) -> Dict[str, Any]:
        pass


class NominatimAPI(AbstractAPIClient):
    """Класс для работы с Nominatim OpenStreetMap API"""

    def __init__(self) -> None:
        self.base_url: str = 'https://nominatim.openstreetmap.org/search'
        self.headers: Dict[str, str] = {'User-Agent': 'aircraft_tracker/1.0'}
        self._connected: bool = False

    def connect(self) -> bool:
        try:
            response = requests.head(self.base_url, headers=self.headers, timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected

    def get_data(self, country: str = "", **kwargs: Any) -> Dict[str, Any]:
        """Получение географических координат страны"""
        if not self._connected:
            self.connect()

        params: Dict[str, Any] = {'country': country, 'format': 'json', 'limit': 1}
        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        if not data:
            return {}

        bounding_box = data[0].get('boundingbox', [])
        return {
            'country': country,
            'south': float(bounding_box[0]),
            'north': float(bounding_box[1]),
            'west': float(bounding_box[2]),
            'east': float(bounding_box[3]),
        }


class OpenSkyAPI(AbstractAPIClient):
    """Класс для работы с OpenSky Network API"""

    def __init__(self) -> None:
        self.base_url: str = 'https://opensky-network.org/api/states/all'
        self._connected: bool = False

    def connect(self) -> bool:
        try:
            response = requests.head('https://opensky-network.org', timeout=5)
            self._connected = response.status_code == 200
            return self._connected
        except requests.RequestException:
            self._connected = False
            return self._connected

    def get_data(self, lamin: float = 0, lamax: float = 0,
                 lomin: float = 0, lomax: float = 0, **kwargs: Any) -> Dict[str, Any]:
        """Получение информации о самолетах в заданном регионе"""
        if not self._connected:
            self.connect()

        params: Dict[str, float] = {'lamin': lamin, 'lamax': lamax,
                                     'lomin': lomin, 'lomax': lomax}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()

        return response.json()


class AeroplanesAPI:
    """Основной класс для работы с API самолетов"""

    def __init__(self) -> None:
        self.nominatim_api = NominatimAPI()
        self.opensky_api = OpenSkyAPI()
        self._aeroplanes: List[List[Any]] = []

    def get_country_coordinates(self, country: str) -> Dict[str, Any]:
        """Получение координат страны"""
        return self.nominatim_api.get_data(country=country)

    def get_aeroplanes(self, south: float, north: float,
                       west: float, east: float) -> List[List[Any]]:
        """Получение самолетов в заданном регионе"""
        aircraft_data = self.opensky_api.get_data(
            lamin=south, lamax=north, lomin=west, lomax=east
        )
        self._aeroplanes = aircraft_data.get('states', [])
        return self._aeroplanes