from db import get_connection

def get_expeditions_by_region(region_name):
    """Получить экспедиции по конкретному региону"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    Номер_экспедиции,
                    Название,
                    Район,
                    Дата_начала,
                    Дата_окончания
                FROM экспедиция
                WHERE Район = %s
                ORDER BY Дата_начала DESC
            """, (region_name,))
            return cursor.fetchall()
    finally:
        connection.close()

def get_unique_expeditions():
    """Получить уникальные экспедиции без дублирования"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    Номер_экспедиции,
                    Название,
                    Район,
                    Дата_начала,
                    Дата_окончания
                FROM экспедиция
                ORDER BY Район, Дата_начала
            """)
            return cursor.fetchall()
    finally:
        connection.close()

def get_coordinates_for_region(region_name):
    """Получить координаты для конкретного региона"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Широта, Долгота
                FROM координаты_районов
                WHERE Район LIKE %s
            """, (f"%{region_name}%",))
            return cursor.fetchall()
    finally:
        connection.close()