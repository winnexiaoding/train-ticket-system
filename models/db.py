import pymysql
from config import Config


def get_db_connection():
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,

    )
    return connection


if __name__ == '__main__':
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM schedule")
        result = cursor.fetchall()
        print(result)
    connection.close()