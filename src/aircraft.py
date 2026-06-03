from functools import total_ordering
from typing import Any, Dict, List, Optional


@total_ordering
class Aircraft:
    """Класс, представляющий информацию о самолете."""

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        baro_altitude: float,
        icao24: str = "",
        on_ground: bool = False,
        last_contact: int = 0,
    ) -> None:
        """Конструктор класса"""
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._baro_altitude = self._validate_altitude(baro_altitude)
        self._icao24 = icao24
        self._on_ground = on_ground
        self._last_contact = last_contact

    @staticmethod
    def _validate_callsign(callsign: str) -> str:
        if not isinstance(callsign, str):
            raise TypeError("Позывной должен быть строкой")
        if not callsign or not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        return callsign.strip()

    @staticmethod
    def _validate_country(country: str) -> str:
        if not isinstance(country, str):
            raise TypeError("Страна должна быть строкой")
        if not country or not country.strip():
            raise ValueError("Страна не может быть пустой")
        return country.strip()

    @staticmethod
    def _validate_velocity(velocity: float) -> float:
        if not isinstance(velocity, (int, float)):
            raise TypeError("Скорость должна быть числом")
        if velocity < 0:
            raise ValueError(f"Скорость не может быть отрицательной: {velocity}")
        return float(velocity)

    @staticmethod
    def _validate_altitude(altitude: float) -> float:
        if not isinstance(altitude, (int, float)):
            raise TypeError("Высота должна быть числом")
        if altitude < 0:
            raise ValueError(f"Высота не может быть отрицательной: {altitude}")
        return float(altitude)

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def baro_altitude(self) -> float:
        return self._baro_altitude

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @property
    def last_contact(self) -> int:
        return self._last_contact

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aircraft):
            return NotImplemented
        return abs(self._velocity - other._velocity) < 0.01 and abs(self._baro_altitude - other._baro_altitude) < 0.01

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Aircraft):
            return NotImplemented
        if abs(self._velocity - other._velocity) >= 0.01:
            return self._velocity < other._velocity
        return self._baro_altitude < other._baro_altitude

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "callsign": self._callsign,
            "origin_country": self._origin_country,
            "velocity": self._velocity,
            "baro_altitude": self._baro_altitude,
            "icao24": self._icao24,
            "on_ground": self._on_ground,
            "last_contact": self._last_contact,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aircraft":
        """Создание из словаря"""
        return cls(
            callsign=data["callsign"],
            origin_country=data.get("origin_country", "Unknown"),
            velocity=data["velocity"],
            baro_altitude=data["baro_altitude"],
            icao24=data.get("icao24", ""),
            on_ground=data.get("on_ground", False),
            last_contact=data.get("last_contact", 0),
        )

    @classmethod
    def from_api_response(cls, state: List[Any]) -> "Aircraft":
        """Создание объекта из ответа OpenSky API"""
        callsign = state[1].strip() if state[1] else "UNKNOWN"
        origin_country = state[2] if state[2] else "Unknown"
        velocity = float(state[9]) if state[9] is not None else 0.0
        baro_altitude = float(state[7]) if state[7] is not None else 0.0
        icao24 = state[0] if state[0] else ""
        on_ground = bool(state[8]) if state[8] is not None else False
        last_contact = state[4] if state[4] else 0

        return cls(
            callsign=callsign,
            origin_country=origin_country,
            velocity=velocity,
            baro_altitude=baro_altitude,
            icao24=icao24,
            on_ground=on_ground,
            last_contact=last_contact,
        )

    @classmethod
    def cast_to_object_list(cls, states: List[List[Any]]) -> List["Aircraft"]:
        """Преобразование данных API в список объектов Aircraft"""
        aircraft_list: List["Aircraft"] = []
        if states:
            for state in states:
                try:
                    aircraft = cls.from_api_response(state)
                    aircraft_list.append(aircraft)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка при создании объекта: {e}")
        return aircraft_list

    def __str__(self) -> str:
        return (
            f"Самолет {self._callsign} ({self._origin_country}): "
            f"скорость {self._velocity} м/с, высота {self._baro_altitude} м"
        )

    def __repr__(self) -> str:
        return (
            f"Aircraft(callsign='{self._callsign}', "
            f"country='{self._origin_country}', "
            f"velocity={self._velocity}, altitude={self._baro_altitude})"
        )
