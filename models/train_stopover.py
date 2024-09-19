import pymysql
from models.schedule_stopover_time import Schedule_stopover_time
from models.price import Price


class TrainStopover:
    @staticmethod
    def update_train_stopovers(connection, train_id, stopovers: list):
        try:
            with connection.cursor() as cursor:
                # 首先获取原来的列车停靠信息
                cursor.execute(
                    "SELECT station_name, stop_duration, time_to_next_stopover FROM train_stopover WHERE train_id=%s "
                    "ORDER BY stopover_number",
                    train_id)
                old_stopovers = cursor.fetchall()
                old_stopovers = [
                    {'station_name': stopover[0], 'stop_duration': stopover[1], 'time_to_next_stopover': stopover[2]}
                    for stopover in old_stopovers]
                for i in range(len(old_stopovers)):
                    old_stopover = old_stopovers[i]
                    if old_stopover['station_name'] not in [stopover['station_name'] for stopover in stopovers]:
                        # 如果原来有该站，但现在没有，则删除该站
                        cursor.execute("DELETE FROM train_stopover WHERE train_id=%s AND station_name=%s",
                                       (train_id, old_stopover['station_name']))

                for i, stopover in enumerate(stopovers, start=1):
                    if stopover['station_name'] in [old_stopover['station_name'] for old_stopover in old_stopovers]:
                        # 如果原来有该站，则更新站点编号、停靠时间和到达下一站时间
                        cursor.execute(
                            "UPDATE train_stopover SET stopover_number=%s, stop_duration=%s, time_to_next_stopover=%s "
                            "WHERE train_id=%s AND station_name=%s",
                            (i, stopover['stop_duration'], stopover['time_to_next_stopover'], train_id,
                             stopover['station_name']))
                for i, stopover in enumerate(stopovers, start=1):
                    # 如果原来没有该站，则插入该站
                    if stopover['station_name'] not in [old_stopover['station_name'] for old_stopover in old_stopovers]:
                        cursor.execute(
                        "INSERT INTO train_stopover (train_id, station_name, stopover_number, stop_duration, "
                        "time_to_next_stopover) VALUES (%s, %s, %s, %s, %s)",
                        (train_id, stopover['station_name'], i, stopover['stop_duration'],
                         stopover['time_to_next_stopover']))
            connection.commit()

            # 更新价格表
            Price.add_price_when_update_stopover(connection, train_id,
                                                 [stopover['station_name'] for stopover in old_stopovers],
                                                 [stopover['station_name'] for stopover in stopovers])

            if len(stopovers) != len(old_stopovers):
                Schedule_stopover_time.copy_from_train_stopover(connection, train_id=train_id)

            # 修改发车途径时间表
            return True
        except pymysql.Error as e:
            print(e)
            connection.rollback()
            return False
        except Exception as e:
            connection.rollback()
            print(e)
            return False

    @staticmethod
    def get_train_stopovers_by_train_id(connection, train_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT station_name, stop_duration, time_to_next_stopover FROM train_stopover WHERE "
                           "train_id=%s ORDER BY stopover_number", (train_id))
            stopovers = cursor.fetchall()
            stopovers = [{'station_name': stopover[0], 'stop_duration': stopover[1],
                          'time_to_next_stopover': stopover[2]} for stopover in stopovers]
            return stopovers

