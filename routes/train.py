from flask import (
    Blueprint, redirect, render_template, request, session, url_for, jsonify
)
from models.db import get_db_connection
from models.train import Train
from models.train_stopover import TrainStopover
import json


bp = Blueprint('train', __name__)


@bp.route('/train_manage')
def train_manage():
    if 'username' in session:
        return render_template('train_manage.html', active_link='train_manage')
    return redirect(url_for('login'))


@bp.route('/show_all_trains', methods=['POST'])
def show_all_trains():
    if 'username' in session:
        db_connection = get_db_connection()
        trains = Train.get_all_trains(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': trains})
    else:
        return redirect(url_for('login'))


@bp.route('/train_search', methods=['POST'])
def train_search():
    if 'username' in session:
        search_query = request.form.get('search_query')
        db_connection = get_db_connection()
        trains = Train.search_trains(db_connection, search_query)
        db_connection.close()
        return jsonify({'status': 'success', 'data': trains})
    else:
        return redirect(url_for('login'))


@bp.route('/delete_train', methods=['POST'])
def delete_train():
    if 'username' in session:
        train_id = request.form.get('train_id')
        db_connection = get_db_connection()
        x = Train.delete_train(db_connection, train_id)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '删除失败, 检查是否有车次在使用'})
    else:
        return redirect(url_for('login'))


@bp.route('/edit_train', methods=['POST'])
def edit_train():
    if 'username' in session:
        train_id = request.form.get('train_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        train_type = request.form.get('train_type')
        num_carriages = request.form.get('num_carriages')
        num_business_seats = request.form.get('num_business_seats')
        num_first_class_seats = request.form.get('num_first_class_seats')
        num_second_class_seats = request.form.get('num_second_class_seats')
        if train_id and start_station and end_station and train_type and num_carriages \
                and num_business_seats and num_first_class_seats and num_second_class_seats:
            db_connection = get_db_connection()
            x = Train.update_train(db_connection, train_id, start_station, end_station, train_type,
                                  num_carriages, num_business_seats, num_first_class_seats, num_second_class_seats)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '修改成功'})
            else:
                return jsonify({'status': 'error', 'message': '修改失败'}), 500
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    else:
        return redirect(url_for('login'))


@bp.route('/train_add', methods=['POST'])
def train_add():
    if 'username' in session:
        train_id = request.form.get('train_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        train_type = request.form.get('train_type')
        num_carriages = request.form.get('num_carriages')
        num_business_seats = request.form.get('num_business_seats')
        num_first_class_seats = request.form.get('num_first_class_seats')
        num_second_class_seats = request.form.get('num_second_class_seats')
        print(train_id, start_station, end_station, train_type, num_carriages, num_business_seats, num_first_class_seats, num_second_class_seats)
        if train_id and start_station and end_station and train_type and num_carriages \
                and num_business_seats and num_first_class_seats and num_second_class_seats:
            db_connection = get_db_connection()
            x = Train.add_train(db_connection, train_id, start_station, end_station, train_type,
                               num_carriages, num_business_seats, num_first_class_seats, num_second_class_seats)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '添加成功'})
            else:
                return jsonify({'status': 'error', 'message': '添加失败'})
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'})
    else:
        return redirect(url_for('login'))


@bp.route('/get_train_stopovers', methods=['POST'])
def get_train_stopovers():
    if 'username' in session:
        train_id = request.form.get('train_id')
        db_connection = get_db_connection()
        stopovers = TrainStopover.get_train_stopovers_by_train_id(db_connection, train_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': stopovers})
    else:
        return redirect(url_for('login'))


@bp.route('/update_train_stopovers', methods=['POST'])
def update_train_stopovers():
    if 'username' in session:
        train_id = request.form.get('train_id')
        stopovers_json = request.form.get('stopovers')
        stopovers = json.loads(stopovers_json)  # 使用 json.loads 解析 JSON 字符串
        new_stopovers = []

        for stopover_data in stopovers:
            new_stopovers.append({
                'station_name': stopover_data['station_name'],
                'stop_duration': int(stopover_data['stop_duration']),
                'time_to_next_stopover': int(stopover_data['time_to_next_stopover'])
            })

        db_connection = get_db_connection()
        train = Train.get_train_by_id(db_connection, train_id)
        start_station = train[0]['start_station']
        end_station = train[0]['end_station']

        # 确保始发站和终点站在途径站点列表中
        if len(new_stopovers) < 2 or new_stopovers[0]['station_name'] != start_station or new_stopovers[-1]['station_name'] != end_station:
            return jsonify({'status': 'error', 'message': '修改失败，请检查始发站和终点站'})

        if TrainStopover.update_train_stopovers(db_connection, train_id, new_stopovers):
            db_connection.close()
            return jsonify({'status': 'success', 'message': '修改成功'})
        else:
            db_connection.close()
            return jsonify({'status': 'error', 'message': '修改失败'})
    else:
        return redirect(url_for('login'))