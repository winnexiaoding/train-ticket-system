import pymysql


class Ticket:
    @staticmethod
    def get_remaining_tickets(connection, schedule_id, start_station, end_station):
        """
        :param connection: 数据库连接
        :param schedule_id: 时刻表ID
        :param start_station: 出发站
        :param end_station: 到达站
        :return: 返回剩余票数
        """
        try:
            with connection.cursor() as cursor:
                # 找start_station和end_station的编号
                sql = "SELECT stopover_number FROM train_stopover, schedule " \
                      "WHERE train_stopover.train_id = schedule.train_id " \
                      "AND station_name=%s AND schedule_id=%s"
                cursor.execute(sql, (start_station, schedule_id))
                start_station_number = cursor.fetchone()[0]
                cursor.execute(sql, (end_station, schedule_id))
                end_station_number = cursor.fetchone()[0]
                # 找到他们之间的站点
                sql = "SELECT station_name FROM train_stopover WHERE train_id=(SELECT train_id FROM schedule WHERE schedule_id=%s) " \
                      "AND stopover_number>=%s AND stopover_number<=%s ORDER BY stopover_number"
                cursor.execute(sql, (schedule_id, start_station_number, end_station_number))
                stations = cursor.fetchall()
                stations = [x[0] for x in stations]


                business_seats = []
                first_class_seats = []
                second_class_seats = []
                for i in range(len(stations) - 1):
                    sql = "SELECT remaining_business_seats, remaining_first_class_seats, remaining_second_class_seats " \
                          "FROM remaining_seats WHERE schedule_id =%s AND start_station=%s AND end_station=%s"
                    cursor.execute(sql, (schedule_id, stations[i], stations[i + 1]))
                    temp = cursor.fetchone()
                    business_seats.append(temp[0])
                    first_class_seats.append(temp[1])
                    second_class_seats.append(temp[2])
                # 查找票价
                sql = "SELECT business_seat_price, first_class_seat_price, second_class_seat_price " \
                      "FROM price, schedule WHERE price.train_id = schedule.train_id AND schedule_id=%s"
                cursor.execute(sql, schedule_id)
                temp = cursor.fetchone()
                result = {'remaining_business_seats': min(business_seats), 'remaining_first_class_seats': min(first_class_seats),
                          'remaining_second_class_seats': min(second_class_seats),
                          'business_seat_price': temp[0], 'first_class_seat_price': temp[1], 'second_class_seat_price': temp[2]}
                # 查找出发时间
                sql = """SELECT departure_time FROM schedule_stopover_times_view 
                WHERE schedule_id=%s AND station_name = %s"""
                cursor.execute(sql, (schedule_id, start_station))
                result['departure_time'] = cursor.fetchone()[0]
                # 查找到达时间
                sql = """
                    SELECT arrival_time FROM schedule_stopover_times_view 
                    WHERE schedule_id=%s AND station_name = %s"""
                cursor.execute(sql, (schedule_id, end_station))
                result['arrival_time'] = cursor.fetchone()[0]
                # 查找train_id
                sql = "SELECT train_id FROM schedule WHERE schedule_id=%s"
                cursor.execute(sql, schedule_id)
                result['train_id'] = cursor.fetchone()[0]
                result['start_station'] = start_station
                result['end_station'] = end_station
                result['schedule_id'] = schedule_id
                return result
        except pymysql.Error as e:
            print("Error getting remaining tickets: ", e)
            return None
        except Exception as e:
            print('Exception', e)
            return None

    @staticmethod
    def search_tickets_by_station_and_time(connection, datetime, start_station, end_station):
        """
        :param connection: 数据库连接
        :param datetime: 出发时间
        :param start_station: 出发站
        :param end_station: 到达站
        :return: 返回符合条件的车次信息
        """
        try:
            with connection.cursor() as cursor:
                # 通过车次途径表,找到包含出发站和到达站的车次
                sql = """
                        SELECT DISTINCT train_id
                        FROM train_stopover
                        WHERE station_name IN (%s, %s)
                        GROUP BY train_id
                        HAVING COUNT(DISTINCT station_name) = 2
                           AND SUM(CASE WHEN station_name = %s THEN stopover_number ELSE NULL END) <
                               SUM(CASE WHEN station_name = %s THEN stopover_number ELSE NULL END);
                    """
                cursor.execute(sql, (start_station, end_station, start_station, end_station))
                train_ids = cursor.fetchall()
                train_ids = [x[0] for x in train_ids]
                train_ids = tuple(train_ids)
                schedule_ids = []
                # 从发车表中，找到上面车次的发车时间符合条件的schedule_id
                for train_id in train_ids:
                    sql = """SELECT schedule_id FROM schedule_stopover_times_view schedule 
                    WHERE train_id = %s AND station_name = %s AND departure_time > %s
                    """
                    cursor.execute(sql, (train_id, start_station, datetime))
                    temp = cursor.fetchall()
                    temp = [x[0] for x in temp]
                    schedule_ids.extend(temp)
                results = []
                # 通过发车id找到剩余票数
                for schedule_id in schedule_ids:
                    x = Ticket.get_remaining_tickets(connection, schedule_id, start_station, end_station)
                    if x:
                        results.append(x)
                return results
        except Exception as e:
            print(f"Error searching tickets: {e}")
            return None

    @staticmethod
    def buy_ticket(connection, passenger_id, staff_id, schedule_id, start_station, end_station, seat_class, price):
        """
        :param connection: 数据库连接
        :param passenger_id: 乘客ID
        :param staff_id: 售票员ID
        :param schedule_id: 时刻表ID
        :param start_station: 出发站
        :param end_station: 到达站
        :param seat_class: 座位类型
        :param price: 价格
        :return: 返回是否购票成功
        """
        try:
            with connection.cursor() as cursor:
                # 直接插入到ticket表中
                sql = "INSERT INTO ticket (passenger_id, staff_id, schedule_id, start_station, end_station, seat_class, ticket_price) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (passenger_id, staff_id, schedule_id, start_station, end_station, seat_class, price))
                connection.commit()
                return True
        except Exception as e:
            print(f"Error buying ticket: {e}")
            return False

    @staticmethod
    def refund_ticket(connection, ticket_id):
        """
        :param connection: 数据库连接
        :param ticket_id: 票ID
        :return: 返回是否退票成功
        """
        try:
            with connection.cursor() as cursor:
                # 直接删除ticket表中的记录
                sql = "UPDATE ticket SET is_refunded = 1 WHERE ticket_id = %s"
                cursor.execute(sql, ticket_id)
                connection.commit()
                return True
        except Exception as e:
            print(f"Error refunding ticket: {e}")
            return False

    @staticmethod
    def show_all_tickets(connection):
        """
        :param connection: 数据库连接
        :return: 返回所有车票信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM ticket where is_refunded = 0"
                cursor.execute(sql)
                tickets = cursor.fetchall()
                results = []
                for tickets in tickets:
                    results.append({'ticket_id': tickets[0], 'passenger_id': tickets[1], 'staff_id': tickets[2],
                                    'schedule_id': tickets[3], 'start_station': tickets[4], 'end_station': tickets[5],
                                    'seat_class': tickets[6], 'ticket_price': tickets[8], 'operation_time': tickets[9]})
                return results
        except Exception as e:
            print(f"Error showing all tickets: {e}")
            return None

    @staticmethod
    def search_tickets(connection, passenger_id=None, staff_id=None, schedule_id=None, start_station=None,
                       end_station=None, seat_class=None, operation_time=None):
        """
        :param connection: 数据库连接
        :param passenger_id: 乘客ID
        :param staff_id: 售票员ID
        :param schedule_id: 时刻表ID
        :param start_station: 出发站
        :param end_station: 到达站
        :param seat_class: 座位类型
        :param operation_time: 操作时间
        :return: 返回符合条件的车票信息
        """
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM ticket WHERE 1=1"
                args = []
                if passenger_id:
                    sql += " AND passenger_id LIKE %s"
                    args.append(f"%{passenger_id}%")
                if staff_id:
                    sql += " AND staff_id LIKE %s"
                    args.append(f"%{staff_id}%")
                if schedule_id:
                    sql += " AND schedule_id LIKE %s"
                    args.append(f"%{schedule_id}%")
                if start_station:
                    sql += " AND start_station LIKE %s"
                    args.append(f"%{start_station}%")
                if end_station:
                    sql += " AND end_station LIKE %s"
                    args.append(f"%{end_station}%")
                if seat_class:
                    sql += " AND seat_class LIKE %s"
                    args.append(f"%{seat_class}%")
                # operation_time是为年月日，数据库中是年月日时分秒，所以只取前10位
                if operation_time:
                    sql += " AND operation_time LIKE %s"
                    args.append(f"%{operation_time[:10]}%")
                args = tuple(args)
                cursor.execute(sql, args)
                tickets = cursor.fetchall()
                results = []
                for tickets in tickets:
                    results.append({'ticket_id': tickets[0], 'passenger_id': tickets[1], 'staff_id': tickets[2],
                                    'schedule_id': tickets[3], 'start_station': tickets[4], 'end_station': tickets[5],
                                    'seat_class': tickets[6], 'ticket_price': tickets[8], 'operation_time': tickets[9]})
                return results
        except Exception as e:
            print(f"Error searching tickets: {e}")
            return None
