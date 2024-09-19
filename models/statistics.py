import pymysql


class Statistics:
    @staticmethod
    def get_all_statistics_of_train(connection):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT 
                    `schedule`.train_id, 
                        `schedule`.departure_time,
                    business_class_sales_view.*
                FROM business_class_sales_view
                JOIN `schedule` ON `schedule`.schedule_id = business_class_sales_view.schedule_id
                
                UNION ALL
                
                SELECT 
                    `schedule`.train_id, 
                        `schedule`.departure_time,
                    first_class_sales_view.*
                FROM first_class_sales_view
                JOIN `schedule` ON `schedule`.schedule_id = first_class_sales_view.schedule_id
                
                UNION ALL
                
                SELECT 
                    `schedule`.train_id, 
                        `schedule`.departure_time,
                    second_class_sales_view.*
                FROM second_class_sales_view
                JOIN `schedule` ON `schedule`.schedule_id = second_class_sales_view.schedule_id;

                """)
                result = []
                for row in cursor.fetchall():
                    result.append({
                        'train_id': row[0],
                        'date': row[1],
                        'Current_station': row[2],      # 当前站
                        'Next_station': row[3], # 下一站
                        'Seat_class': row[4],   # 座位等级
                        'Total_seats': row[5],  # 总座位数
                        'Sold_seats': row[6],   # 已售座位数
                        'Remain_seats': row[7], # 剩余座位数
                    })
            return result
        except pymysql.MySQLError as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_statistics_by_train_id_and_date(connection, train_id, date):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'CALL `ticket_sales_statistics`("{train_id}","{date}");')
                result = []
                for row in cursor.fetchall():
                    result.append({
                        'train_id': train_id,
                        'date': date,
                        'Current_station': row[0],      # 当前站
                        'Next_station': row[1], # 下一站
                        'Seat_class': row[2],   # 座位等级
                        'Total_seats': row[3],  # 总座位数
                        'Sold_seats': row[4],   # 已售座位数
                        'Remain_seats': row[5], # 剩余座位数
                    })
            return result
        except pymysql.MySQLError as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_statistics_of_staff_by_date(connetcion, start_date, end_date=None):
        try:
            with connetcion.cursor() as cursor:
                if end_date is None or end_date.strip() == '':
                    cursor.execute(f'CALL `sales_income_by_date_range`("{start_date}", NULL);')
                else:
                    cursor.execute(f'CALL `sales_income_by_date_range`("{start_date}", "{end_date}");')
                result = []
                for row in cursor.fetchall():
                    result.append({
                        'Staff_id': row[0],     # 员工ID
                        'Total_sales': row[1],  # 总销售额
                    })
            return result
        except pymysql.MySQLError as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None