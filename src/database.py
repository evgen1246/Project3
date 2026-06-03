from typing import Any, Dict, List

import psycopg2
from psycopg2 import sql

from config import COUNTRIES, DB_CONFIG
from src.aircraft import Aircraft
from src.api_clients import AeroplanesAPI


class DatabaseSetup:
    """Класс для настройки и заполнения базы данных"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Подключение к базе данных"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def disconnect(self) -> None:
        """Закрытие соединения"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_database(self) -> None:
        """Создание базы данных если её нет"""
        try:
            # Подключаемся к postgres для создания БД
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database="postgres",
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Проверяем существование БД
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_CONFIG["database"],))
            if not cursor.fetchone():
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG["database"])))
                print(f"База данных '{DB_CONFIG['database']}' создана")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при создании БД: {e}")

    def create_tables(self) -> None:
        """Создание таблиц"""
        self.connect()

        # Читаем SQL скрипт
        with open("sql/create_tables.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()

        self.cursor.execute(sql_script)
        self.conn.commit()
        print("Таблицы созданы успешно")

        self.disconnect()

    def fill_countries(self, countries: List[str]) -> None:
        """Заполнение таблицы стран"""
        self.connect()
        api = AeroplanesAPI()

        for country in countries:
            print(f"Получение координат для: {country}")
            data = api.get_country_coordinates(country)

            if data:
                self.cursor.execute(
                    """INSERT INTO countries (name, south_lat, north_lat, west_lon, east_lon)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (name) DO UPDATE SET
                           south_lat = EXCLUDED.south_lat,
                           north_lat = EXCLUDED.north_lat,
                           west_lon = EXCLUDED.west_lon,
                           east_lon = EXCLUDED.east_lon""",
                    (country, data["south"], data["north"], data["west"], data["east"]),
                )
                print(f"  Координаты сохранены")
            else:
                print(f"  Страна '{country}' не найдена")

        self.conn.commit()
        self.disconnect()

    def fill_aircraft(self) -> None:
        """Заполнение таблицы самолетов данными из API"""
        self.connect()
        api = AeroplanesAPI()

        # Получаем все страны из БД
        self.cursor.execute("SELECT id, name, south_lat, north_lat, west_lon, east_lon FROM countries")
        countries = self.cursor.fetchall()

        for country_data in countries:
            country_id, country_name, south, north, west, east = country_data

            print(f"Получение самолетов над: {country_name}")

            try:
                states = api.get_aeroplanes(south, north, west, east)
                aircraft_list = Aircraft.cast_to_object_list(states)

                for aircraft in aircraft_list:
                    self.cursor.execute(
                        """INSERT INTO aircraft 
                           (callsign, origin_country, velocity, baro_altitude, 
                            country_id, icao24, on_ground, last_contact)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            aircraft.callsign,
                            aircraft.origin_country,
                            aircraft.velocity,
                            aircraft.baro_altitude,
                            country_id,
                            aircraft.icao24,
                            aircraft.on_ground,
                            aircraft.last_contact,
                        ),
                    )

                print(f"  Добавлено самолетов: {len(aircraft_list)}")

            except Exception as e:
                print(f"  Ошибка для {country_name}: {e}")

        self.conn.commit()
        self.disconnect()

    def setup_all(self) -> None:
        """Полная настройка базы данных"""
        print("=" * 50)
        print("Настройка базы данных")
        print("=" * 50)

        print("\n1. Создание базы данных...")
        self.create_database()

        print("\n2. Создание таблиц...")
        self.create_tables()

        print("\n3. Заполнение таблицы стран...")
        self.fill_countries(COUNTRIES)

        print("\n4. Заполнение таблицы самолетов...")
        self.fill_aircraft()

        print("\n" + "=" * 50)
        print("Настройка завершена!")
        print("=" * 50)
