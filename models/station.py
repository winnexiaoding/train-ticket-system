import pymysql


class Station:
    @staticmethod
    def get_all_stations(connection):
        """
            获取所有站点名称
            :param connection: 数据库连接
            :return: 所有站点名称
        """
        try:
            with connection.cursor() as cursor:
                station_sql = "SELECT station_name FROM station"
                cursor.execute(station_sql)
                result = cursor.fetchall()
                # 转换成列表
                result = [item[0] for item in result]
                return result
        except pymysql.MySQLError as e:
            return []

    @staticmethod
    def add_station(connection, station_name):
        """
            添加站点
            :param connection: 数据库连接
            :param station_name: 站点名称
            :return: True/False
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO station (station_name) VALUES ('{station_name}')")
                connection.commit()
                return True
        except pymysql.MySQLError as e:
            print(e)
            return False

    @staticmethod
    def delete_station(connection, station_name):
        """
            删除站点
        :param connection: 数据库连接
        :param station_name: 站点名称
        :return:
        """
        try:
            with connection.cursor() as cursor:
                delete_station_sql = f"DELETE FROM station WHERE station_name = '{station_name}'"
                cursor.execute(delete_station_sql)
                connection.commit()
                return True
        except pymysql.MySQLError as e:
            return False

    @staticmethod
    def search_station(connection, station_name):
        """
        :param connection: 数据库连接
        :param station_name: 站点名称
        :return: 站点列表
        """
        try:
            with connection.cursor() as cursor:
                search_station_sql = f"SELECT * FROM station WHERE station_name LIKE '%{station_name}%'"
                cursor.execute(search_station_sql)
                result = cursor.fetchall()
                # 转换成列表
                result = [item[0] for item in result]
                return result
        except pymysql.MySQLError as e:
            return []

    @staticmethod
    def get_station_by_name(connection, station_name):
        """
        :param connection: 数据库连接
        :param station_name: 站点名称
        :return: 站点列表
        """
        try:
            with connection.cursor() as cursor:
                search_station_sql = f"SELECT * FROM station WHERE station_name = '{station_name}'"
                cursor.execute(search_station_sql)
                result = cursor.fetchall()
                if len(result) == 0:
                    return None
                return result[0]
        except pymysql.MySQLError as e:
            return None
