from typing import List, Tuple

import psycopg2

from config import DB_CONFIG


class DBManager:
    """Класс для работы с данными в PostgresSQL"""

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

    def get_countries_and_aeroplanes_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех стран и количество самолетов
        в их воздушных пространствах.

        Returns:
            Список кортежей (страна, количество самолетов)
        """
        self.connect()
        self.cursor.execute("""
            SELECT c.name, COUNT(a.id) as aircraft_count
            FROM countries c
            LEFT JOIN aircraft a ON c.id = a.country_id
            GROUP BY c.name
            ORDER BY aircraft_count DESC
        """)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def get_all_aeroplanes(self) -> List[Tuple]:
        """Получает список всех воздушных судов."""

        self.connect()
        self.cursor.execute("""
            SELECT a.id, a.callsign, a.origin_country, 
                   a.velocity, a.baro_altitude, a.icao24,
                   a.on_ground, c.name as country_name
            FROM aircraft a
            JOIN countries c ON a.country_id = c.id
            ORDER BY a.callsign
        """)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def get_avg_speed(self) -> float:
        """Получает среднюю скорость по всем самолетам."""

        self.connect()
        self.cursor.execute("""
            SELECT AVG(velocity) 
            FROM aircraft 
            WHERE velocity > 0
        """)
        result = self.cursor.fetchone()
        self.disconnect()
        return float(result[0]) if result and result[0] else 0.0

    def get_aeroplanes_with_higher_speed(self) -> List[Tuple]:
        """Получает список всех самолетов, у которых скорость выше средней."""

        avg_speed = self.get_avg_speed()

        self.connect()
        self.cursor.execute(
            """
            SELECT a.id, a.callsign, a.origin_country, 
                   a.velocity, a.baro_altitude, a.icao24,
                   c.name as country_name
            FROM aircraft a
            JOIN countries c ON a.country_id = c.id
            WHERE a.velocity > %s AND a.velocity > 0
            ORDER BY a.velocity DESC
        """,
            (avg_speed,),
        )
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Tuple]:
        """Получает список всех самолетов, в позывном которых
        содержатся переданные символы."""

        self.connect()
        self.cursor.execute(
            """
            SELECT a.id, a.callsign, a.origin_country, 
                   a.velocity, a.baro_altitude, a.icao24,
                   c.name as country_name
            FROM aircraft a
            JOIN countries c ON a.country_id = c.id
            WHERE UPPER(a.callsign) LIKE UPPER(%s)
            ORDER BY a.callsign
        """,
            (f"%{keyword}%",),
        )
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def print_countries_and_counts(self) -> None:
        """Вывод стран и количества самолетов"""
        data = self.get_countries_and_aeroplanes_count()
        print("\n" + "=" * 60)
        print("СТРАНЫ И КОЛИЧЕСТВО САМОЛЕТОВ")
        print("=" * 60)
        print(f"{'Страна':25s} {'Количество':>10s}")
        print("-" * 40)
        for country, count in data:
            print(f"{country:25s} {count:>10d}")
        print("-" * 40)
        print(f"{'ВСЕГО:':25s} {sum(c for _, c in data):>10d}")

    def print_all_aeroplanes(self) -> None:
        """Вывод всех самолетов"""
        data = self.get_all_aeroplanes()
        print("\n" + "=" * 80)
        print("ВСЕ ВОЗДУШНЫЕ СУДА")
        print("=" * 80)
        print(f"{'№':4s} {'Позывной':12s} {'Страна рег.':20s} " f"{'Скорость':10s} {'Высота':10s} {'Над страной':15s}")
        print("-" * 75)
        for i, row in enumerate(data[:30], 1):
            print(
                f"{i:<4d} {row[1]:12s} {row[2] or 'N/A':20s} "
                f"{row[3] or 0:>8.1f}  {row[4] or 0:>8.1f}  {row[7]:15s}"
            )
        if len(data) > 30:
            print(f"... и еще {len(data) - 30} самолетов")

    def print_avg_speed(self) -> None:
        """Вывод средней скорости"""
        avg = self.get_avg_speed()
        print(f"\nСредняя скорость всех самолетов: {avg:.2f} м/с ({avg * 3.6:.2f} км/ч)")

    def print_faster_aircraft(self) -> None:
        """Вывод самолетов со скоростью выше средней"""
        data = self.get_aeroplanes_with_higher_speed()
        avg = self.get_avg_speed()
        print(f"\nСАМОЛЕТЫ СО СКОРОСТЬЮ ВЫШЕ СРЕДНЕЙ ({avg:.2f} м/с)")
        print("=" * 60)
        for i, row in enumerate(data[:15], 1):
            print(f"{i}. {row[1]} - {row[3]:.1f} м/с ({row[7]})")

    def search_by_keyword(self, keyword: str) -> None:
        """Поиск самолетов по ключевому слову"""
        data = self.get_aeroplanes_with_keyword(keyword)
        print(f"\nСАМОЛЕТЫ С '{keyword}' В ПОЗЫВНОМ")
        print("=" * 60)
        if data:
            for i, row in enumerate(data[:15], 1):
                print(f"{i}. {row[1]} - {row[2]} (над {row[7]})")
        else:
            print("Ничего не найдено")
