import sys

from src.database import DatabaseSetup
from src.db_manager import DBManager


def setup_database():
    """Настройка базы данных"""
    print("\n" + "=" * 60)
    print("  НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 60)

    db_setup = DatabaseSetup()
    db_setup.setup_all()


def show_statistics():
    """Показать статистику"""
    db = DBManager()

    db.print_countries_and_counts()
    db.print_avg_speed()


def search_aircraft():
    """Поиск самолетов по ключевому слову"""
    db = DBManager()

    print("\n" + "=" * 60)
    print("  ПОИСК САМОЛЕТОВ ПО ПОЗЫВНОМУ")
    print("=" * 60)
    print("\nПримеры запросов:")
    print("  'ACA' — Air Canada")
    print("  'AFL' — Аэрофлот")
    print("  'DLH' — Lufthansa")
    print("  'BAW' — British Airways")
    print("  'UAL' — United Airlines")

    keyword = input("\nВведите часть позывного для поиска: ").strip()
    if keyword:
        db.search_by_keyword(keyword)
    else:
        print("Поиск отменен")


def user_interaction():
    """Основное меню"""
    while True:
        print("\n" + "=" * 60)
        print("  СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
        print("=" * 60)
        print("1. Настроить базу данных (создать таблицы и загрузить данные)")
        print("2. Показать статистику (страны, количество самолетов, ср. скорость)")
        print("3. Показать все самолеты")
        print("4. Показать самолеты со скоростью выше средней")
        print("5. Поиск самолетов по позывному")
        print("6. Выход")
        print("-" * 60)

        choice = input("Выберите действие (1-6): ").strip()

        if choice == "1":
            setup_database()

        elif choice == "2":
            show_statistics()

        elif choice == "3":
            db = DBManager()
            db.print_all_aeroplanes()

        elif choice == "4":
            db = DBManager()
            db.print_faster_aircraft()

        elif choice == "5":
            search_aircraft()

        elif choice == "6":
            print("\nДо свидания!")
            break

        else:
            print("\nНеверный выбор! Введите число от 1 до 6.")


def main() -> int:
    """Главная функция"""
    print("=" * 60)
    print("  СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ С БАЗОЙ ДАННЫХ")
    print("=" * 60)
    print("\nИспользуемые API:")
    print("  - nominatim.openstreetmap.org (геоданные)")
    print("  - opensky-network.org (данные о самолетах)")
    print("\nБаза данных: PostgreSQL")

    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\n[ОШИБКА] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
