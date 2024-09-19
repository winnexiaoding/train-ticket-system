import pymysql


class Schedule:
    @staticmethod
    def get_schedule_by_train_id(connection, train_id):
        """
        :param connection:  数据库连接
        :param train_id:  车次ID
        :return:  返回时刻表信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM schedule WHERE train_id=%s"
                cursor.execute(sql, train_id)
                temp = cursor.fetchall()
                result = [{'schedule_id': x[0], 'train_id': x[1], 'departure_time': x[2]} for x in temp]
                print(result)
                return result

        except pymysql.Error as e:
            print("Error getting schedule by train id: ", e)
            return None
        except Exception as e:
            return None

    @staticmethod
    def get_schedule_by_schedule_id(connection, schedule_id):
        """
        :param connection:  数据库连接
        :param schedule_id:  时刻表ID
        :return:  返回时刻表信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM schedule WHERE schedule_id=%s"
                cursor.execute(sql, schedule_id)
                temp = cursor.fetchone()
                result = {'schedule_id': temp[0], 'train_id': temp[1], 'departure_time': temp[2]}
                return result

        except pymysql.Error as e:
            print("Error getting schedule by schedule id: ", e)
            return None
        except Exception as e:
            return None

    @staticmethod
    def add_schedule(connection, train_id, departure_time):
        """
        :param connection: 数据库连接
        :param train_id: 车次ID
        :param departure_time: 出发时间
        :return: 返回是否添加成功
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO schedule (train_id, departure_time) VALUES (%s, %s)",
                               (train_id, departure_time))
                connection.commit()
                return True
        except pymysql.err.IntegrityError:
            return False
        except pymysql.Error as e:
            print("Error adding schedule: ", e)
            return False
        except Exception as e:
            return False


    @staticmethod
    def delete_schedule_by_schedule_id(connection, schedule_id):
        """
        :param connection: 数据库连接
        :param schedule_id: 时刻表ID
        :return: 返回是否删除成功
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM schedule WHERE schedule_id=%s", schedule_id)
                connection.commit()
                return True
        except pymysql.Error as e:
            print("Error deleting schedule by schedule id: ", e)
            return False
        except Exception as e:
            return False