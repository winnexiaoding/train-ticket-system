import pymysql


class Train:
    @staticmethod
    def get_all_trains(connection):
        """
        :param connection: 数据库连接
        :return: 返回一个Train对象列表
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM train")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({'train_id': row[0], 'start_station': row[1], 'end_station': row[2],
                               'train_type': row[3], 'num_carriages': row[4], 'num_business_seats': row[5],
                               'num_first_class_seats': row[6], 'num_second_class_seats': row[7]})
            return result

    @staticmethod
    def get_train_by_id(connection, train_id):
        """
        :param connection: 数据库连接
        :param train_id: 车次ID
        :return: 返回一个Train对象
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM train WHERE train_id=%s", (train_id,))
            row = cursor.fetchone()
            result = []
            if row:
                result.append({'train_id': row[0], 'start_station': row[1], 'end_station': row[2],
                               'train_type': row[3], 'num_carriages': row[4], 'num_business_seats': row[5],
                               'num_first_class_seats': row[6], 'num_second_class_seats': row[7]})
            return result

    @staticmethod
    def add_train(connection, train_id, start_station, end_station, train_type, num_carriages, num_business_seats,
                  num_first_class_seats, num_second_class_seats):
        """
        :param connection: 数据库连接
        :param start_station: 起始站
        :param end_station: 终点站
        :param train_type: 车次类型
        :param num_carriages: 车厢数
        :param num_business_seats: 商务座
        :param num_first_class_seats: 一等座
        :param num_second_class_seats: 二等座
        :return: 返回是否添加成功
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO train (train_id, start_station, end_station, train_type, num_carriages, "
                               "num_business_seats, num_first_class_seats, num_second_class_seats) "
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                               (train_id, start_station, end_station, train_type, num_carriages,
                                num_business_seats, num_first_class_seats, num_second_class_seats))
                connection.commit()
                return True
            except pymysql.err.IntegrityError:
                return False
            except:
                return False

    @staticmethod
    def delete_train(connection, train_id):
        """
        :param connection: 数据库连接
        :param train_id: 车次ID
        :return: 返回是否删除成功
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM train WHERE train_id=%s", (train_id,))
                connection.commit()
                return True
        except Exception as e:
            return False

    @staticmethod
    def update_train(connection, train_id, start_station, end_station, train_type, num_carriages, num_business_seats,
                     num_first_class_seats, num_second_class_seats):
        """
        :param connection: 数据库连接
        :param train_id: 车次ID
        :param start_station: 起始站
        :param end_station: 终点站
        :param train_type: 车次类型
        :param num_carriages: 车厢数
        :param num_business_seats: 商务座
        :param num_first_class_seats: 一等座
        :param num_second_class_seats: 二等座
        :return: 返回是否更新成功
        """
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.execute("UPDATE train SET start_station=%s, end_station=%s, train_type=%s, num_carriages=%s, "
                                   "num_business_seats=%s, num_first_class_seats=%s, num_second_class_seats=%s WHERE "
                                   "train_id=%s",
                                   (start_station, end_station, train_type, num_carriages, num_business_seats,
                                    num_first_class_seats, num_second_class_seats, train_id))
                    connection.commit()
                    return True
                except:
                    return False
        except:
            return False

    @staticmethod
    def search_trains(connection, s):
        """
        :param connection: 数据库连接
        :param s: 要搜索的关键字 例如：车次，站点，火车类型
        :return: 返回一个Train对象列表
        """
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM train WHERE start_station LIKE %s OR end_station LIKE %s OR train_type LIKE "
                           "%s OR train_id LIKE %s", (f'%{s}%', f'%{s}%', f'%{s}%', f'%{s}%'))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append({'train_id': row[0], 'start_station': row[1], 'end_station': row[2],
                               'train_type': row[3], 'num_carriages': row[4], 'num_business_seats': row[5],
                               'num_first_class_seats': row[6], 'num_second_class_seats': row[7]})
            return result
