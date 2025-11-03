import pymysql
import pymysql.cursors
from db import get_connection

def get_expeditions():
    """
    Получает список всех экспедиций с координатами.
    Используется для команды /list и /map
    """
    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                e.Номер_экспедиции,
                e.Название,
                e.Район,
                e.Дата_начала,
                e.Дата_окончания,
                s.Название AS Статус,
                k.Широта,
                k.Долгота
            FROM экспедиция e
            JOIN статус_экспедиции s ON e.Код_статуса = s.Код_статуса
            JOIN координаты_районов k ON e.Код_района = k.Номер
            ORDER BY e.Номер_экспедиции
        """)
        result = cur.fetchall()
    conn.close()
    return result


def get_expedition_by_id(expedition_id):
    """
    Получает данные по одной экспедиции для отображения на карте.
    """
    conn = get_connection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("""
            SELECT 
                e.Номер_экспедиции,
                e.Название,
                e.Район,
                e.Дата_начала,
                e.Дата_окончания,
                s.Название AS Статус,
                k.Широта,
                k.Долгота
            FROM экспедиция e
            JOIN статус_экспедиции s ON e.Код_статуса = s.Код_статуса
            JOIN координаты_районов k ON e.Код_района = k.Номер
            WHERE e.Номер_экспедиции = %s
        """, (expedition_id,))
        expedition = cur.fetchone()
    conn.close()
    return expedition


def get_expeditions_by_region(region_name):
    """
    Возвращает список экспедиций по названию океана/региона.
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT *
        FROM экспедиция
        WHERE Район LIKE %s
    """, (f"%{region_name}%",))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_unique_expeditions():
    """
    Возвращает все экспедиции с уникальными названиями и их основными данными.
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT *
        FROM экспедиция
    """)

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def get_coordinates_for_region(region_name):
    """
    Возвращает координаты района по названию океана.
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT широта AS Широта, долгота AS Долгота
        FROM координаты_районов
        WHERE район LIKE %s
    """, (f"%{region_name}%",))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
