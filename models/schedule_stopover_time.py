import pymysql


class Schedule_stopover_time:
    @staticmethod
    def get_stopover_times_by_schedule_id(connection, schedule_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT s.station_name, sst.stop_duration, sst.time_to_next_stopover
                    FROM schedule_stopover_time sst, train_stopover s, schedule
                    WHERE sst.schedule_id = schedule.schedule_id and schedule.train_id = s.train_id 
                    and sst.stopover_number = s.stopover_number and sst.schedule_id = %s
                    ORDER BY sst.stopover_number
                """, schedule_id)
                stopover_times = cursor.fetchall()
                result = []
                for stopover_time in stopover_times:
                    result.append({
                        'station_name': stopover_time[0],
                        'stop_duration': stopover_time[1],
                        'time_to_next_stopover': stopover_time[2]
                    })
                print(result)
                return result
        except pymysql.Error as e:
            print("pymysql.Error", e)
            return None
        except Exception as e:
            print("Exception", e)
            return None

    @staticmethod
    def copy_from_train_stopover(connection, train_id):
        try:
            with connection.cursor() as cursor:
                # 找出train_id对应的所有shedule_id，然后删除所有的schedule_stopover_time，再重新插入
                cursor.execute("""
                    DELETE FROM schedule_stopover_time WHERE schedule_id 
                    IN (SELECT schedule_id FROM schedule WHERE train_id=%s)
                """, train_id)

                cursor.execute("""
                    INSERT INTO schedule_stopover_time (schedule_id, stopover_number, stop_duration, time_to_next_stopover) 
                    SELECT schedule_id, stopover_number, stop_duration, time_to_next_stopover 
                    FROM train_stopover
                    JOIN schedule ON train_stopover.train_id = schedule.train_id
                    WHERE train_stopover.train_id=%s
                """, train_id)
            connection.commit()
            return True
        except pymysql.Error as e:
            print(e)
            connection.rollback()
            return False
        except Exception as e:
            print(e)
            connection.rollback()
            return False

    @staticmethod
    def update_stopover_time(connection, schedule_id, stopovers: list):
        try:
            with connection.cursor() as cursor:
                # 先删除原有的schedule_stopover_time
                cursor.execute("""
                    DELETE FROM schedule_stopover_time WHERE schedule_id=%s
                """, schedule_id)

                # 再插入新的schedule_stopover_time

                for i, stopover in enumerate(stopovers, start=1):
                    cursor.execute("""
                        INSERT INTO schedule_stopover_time (schedule_id, stopover_number, stop_duration, time_to_next_stopover) 
                        VALUES (%s, %s, %s, %s)
                    """, (schedule_id, i, stopover['stop_duration'], stopover['time_to_next_stopover']))
            connection.commit()

            return True
        except pymysql.Error as e:
            print(e)
            connection.rollback()
            return False
        except Exception as e:
            print(e)
            connection.rollback()
            return False


if __name__ == '__main__':
    from models.db import get_db_connection

    connection = get_db_connection()
    Schedule_stopover_time.copy_from_train_stopover(connection, "G105")
