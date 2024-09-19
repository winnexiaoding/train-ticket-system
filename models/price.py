import pymysql


class Price:
    @staticmethod
    def get_all_price(connection):
        """
            获取所有价格
        :param connection:  数据库连接
        :return:    价格
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM price"
                cursor.execute(sql)
                temp = cursor.fetchall()
                result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                           'business_seat_price': x[3], 'first_class_seat_price': x[4],
                           'sceond_class_seat_price': x[5]} for x in temp]
                return result

        except pymysql.Error as e:
            print("Error getting price by train id: ", e)
            return None
        except Exception as e:
            return None

    @staticmethod
    def get_price_by_train_id(connection, train_id):
        """
            通过train_id获取票价
        :param connection:  数据库连接
        :param train_id:  车次ID
        :return:  返回价格信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM price WHERE train_id LIKE %s"
                cursor.execute(sql, f"%{train_id}%")
                temp = cursor.fetchall()
                result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                           'business_seat_price': x[3], 'first_class_seat_price': x[4],
                           'sceond_class_seat_price': x[5]} for x in temp]
                return result

        except pymysql.Error as e:
            print("Error getting price by train id: ", e)
            return None
        except Exception as e:
            return None

    @staticmethod
    def update_price(connection, train_id, start_station, end_station, business_seat_price, first_class_seat_price,
                     second_class_seat_price):
        """
            更新票价
        :param connection: 数据库连接
        :param train_id:  车次ID
        :param start_station:  出发站
        :param end_station:  到达站
        :param business_seat_price: 商务座价格
        :param first_class_seat_price:  一等座价格
        :param second_class_seat_price:  二等座价格
        :return:
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE price SET business_seat_price=%s, first_class_seat_price=%s, "
                               "second_class_seat_price=%s WHERE train_id=%s AND start_station=%s AND end_station=%s",
                               (business_seat_price, first_class_seat_price, second_class_seat_price, train_id,
                                start_station, end_station))
                connection.commit()
                return True
        except pymysql.Error as e:
            print("Error updating price: ", e)
            connection.rollback()
            return False
        except Exception as e:
            return False

    @staticmethod
    def search_price_by_station(connection, station1, station2=None):
        """

        :param connection: 数据库连接
        :param station1:  站点1
        :param station2:  站点2
        :return:  返回价格信息
        """
        # 如果只有一个站点，则搜索所有和该站点有关的价格信息
        if station2 is None:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM price WHERE  start_station LIKE %s OR end_station LIKE %s"
                    cursor.execute(sql, (f"%{station1}%", f"%{station1}%"))
                    temp = cursor.fetchall()
                    result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                               'business_seat_price': x[3], 'first_class_seat_price': x[4],
                               'sceond_class_seat_price': x[5]} for x in temp]
                    return result
            except pymysql.Error as e:
                print("Error searching price by station: ", e)
                return None
            except Exception as e:
                return None
        # 如果有两个站点，则搜索两个站点之间的价格信息
        else:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM price WHERE (start_station LIKE %s AND end_station LIKE %s) OR " \
                          "(start_station LIKE %s AND end_station LIKE %s)"
                    cursor.execute(sql, (f"%{station1}%", f"%{station2}%", f"%{station2}%", f"%{station1}%"))
                    temp = cursor.fetchall()
                    result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                               'business_seat_price': x[3], 'first_class_seat_price': x[4],
                               'sceond_class_seat_price': x[5]} for x in temp]
                    return result
            except pymysql.Error as e:
                print("Error searching price by station: ", e)
                return None
            except Exception as e:
                return None


    @staticmethod
    def get_price_by_train_id_and_station_strict(connection, train_id, start_station, end_station):
        """
        :param connection:  数据库连接
        :param train_id:  车次ID
        :param start_station:  出发站
        :param end_station:  到达站
        :return:  返回价格信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM price WHERE train_id=%s AND start_station=%s AND end_station=%s"
                cursor.execute(sql, (train_id, start_station, end_station))
                temp = cursor.fetchone()
                result = {'train_id': temp[0], 'start_station': temp[1], 'end_station': temp[2],
                          'business_seat_price': temp[3], 'first_class_seat_price': temp[4],
                          'sceond_class_seat_price': temp[5]}
                return result
        except pymysql.Error as e:
            print("Error getting price by train id and station: ", e)
            return None
        except Exception as e:
            return None

    @staticmethod
    def search_price_by_train_id_and_station(connection, train_id, station1, station2=None):
        """

        :param connection: 数据库连接
        :param train_id:  车次ID
        :param station1:  站点1
        :param station2:  站点2
        :return:  返回价格信息
        """
        # 如果只有一个站点，则搜索所有和该站点有关的价格信息
        if station2 is None:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM price WHERE train_id LIKE %s AND (start_station LIKE %s OR end_station LIKE %s)"
                    cursor.execute(sql, (f"%{train_id}%", f"%{station1}%", f"%{station1}%"))
                    temp = cursor.fetchall()
                    result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                               'business_seat_price': x[3], 'first_class_seat_price': x[4],
                               'sceond_class_seat_price': x[5]} for x in temp]
                    return result
            except pymysql.Error as e:
                print("Error searching price by station: ", e)
                return None
            except Exception as e:
                return None
        # 如果有两个站点，则搜索两个站点之间的价格信息
        else:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM price WHERE train_id=%s AND ((start_station LIKE %s AND end_station LIKE %s) " \
                          "OR (start_station LIKE %s AND end_station LIKE %s))"
                    cursor.execute(sql, (train_id, f"%{station1}%", f"%{station2}%", f"%{station2}%", f"%{station1}%"))
                    temp = cursor.fetchall()
                    result = [{'train_id': x[0], 'start_station': x[1], 'end_station': x[2],
                               'business_seat_price': x[3], 'first_class_seat_price': x[4],
                               'sceond_class_seat_price': x[5]} for x in temp]
                    return result
            except pymysql.Error as e:
                print("Error searching price by station: ", e)
                return None
            except Exception as e:
                return None

    @staticmethod
    def add_price(connection, train_id, start_station, end_station, business_seat_price, first_class_seat_price,
                  second_class_seat_price):
        """
        :param connection: 数据库连接
        :param train_id:  车次ID
        :param start_station:  出发站
        :param end_station:  到达站
        :param business_seat_price: 商务座价格
        :param first_class_seat_price:  一等座价格
        :param second_class_seat_price:  二等座价格
        :return:
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO price (train_id, start_station, end_station, business_seat_price, "
                               "first_class_seat_price, second_class_seat_price) VALUES (%s, %s, %s, %s, %s, %s)",
                               (train_id, start_station, end_station, business_seat_price, first_class_seat_price,
                                second_class_seat_price))
                connection.commit()
                return True
        except pymysql.Error as e:
            print("Error adding price: ", e)
            connection.rollback()
            return False
        except Exception as e:
            return False

    @staticmethod
    def add_price_when_update_stopover(connection, train_id, old_stopovers, new_stopovers):
        """
        当修改途径站点的时候，更新价格表
        :param connection:  数据库连接
        :param train_id:    车次ID
        :param old_stopovers:    旧的途径站点
        :param new_stopovers:   新的途径站点
        :return:      True/False
        """

        print(old_stopovers, new_stopovers)
        # 获取已经被删除的站点
        deleted_stations = list(set(old_stopovers) - set(new_stopovers))
        # 获取新增的站点
        added_stations = []
        for station in new_stopovers:
            if station not in old_stopovers:
                added_stations.append(station)
        # 获取已有未删除的站点
        stayed_stations = []
        for station in old_stopovers:
            if station not in deleted_stations:
                stayed_stations.append(station)
        try:
            with connection.cursor() as cursor:
                for station in deleted_stations:
                    cursor.execute("DELETE FROM price WHERE train_id=%s AND (start_station=%s OR end_station=%s)",
                                   (train_id, station, station))
                for i in range(len(new_stopovers)):
                    for j in range(i+1, len(new_stopovers)):
                        if new_stopovers[i] in added_stations or new_stopovers[j] in added_stations:
                            cursor.execute("INSERT INTO price (train_id, start_station, end_station, "
                                           "business_seat_price, first_class_seat_price, second_class_seat_price) "
                                           "VALUES (%s, %s, %s, %s, %s, %s)",
                                           (train_id, new_stopovers[i], new_stopovers[j], 0, 0, 0))
                        else:
                            continue
                    connection.commit()
                return True
        except pymysql.Error as e:
            print("Error adding price when update stopover: ", e)
            connection.rollback()
            return False
        except Exception as e:
            return False