import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymysql.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="ocean_research_v2",
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4"
    )
