from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session
)
from models.db import get_db_connection
from models.price import Price

bp = Blueprint('price', __name__)



@bp.route('/price_manage')
def price_manage():
    if 'username' in session:
        return render_template('price_manage.html', active_link='price_manage')
    return redirect(url_for('login'))


@bp.route('/get_price_by_train_id', methods=['POST'])
def get_price_by_train_id():
    if 'username' in session:
        train_id = request.form.get('train_id')
        print(train_id)
        db_connection = get_db_connection()
        prices = Price.get_price_by_train_id(db_connection, train_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@bp.route('/get_all_price', methods=['POST'])
def get_all_price():
    if 'username' in session:
        db_connection = get_db_connection()
        prices = Price.get_all_price(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@bp.route('/get_price_by_station', methods=['POST'])
def get_price_by_station():
    if 'username' in session:
        station1 = request.form.get('station1')
        station2 = request.form.get('station2')
        # 如果station2为空，令station2=None
        if not station2 or station2 == '':
            station2 = None
        db_connection = get_db_connection()
        prices = Price.search_price_by_station(db_connection, station1, station2)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@bp.route('/get_price_by_train_id_and_station', methods=['POST'])
def get_price_by_train_id_and_station():
    if 'username' in session:
        train_id = request.form.get('train_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        if not end_station or end_station == '':
            end_station = None
        db_connection = get_db_connection()
        prices = Price.search_price_by_train_id_and_station(db_connection, train_id, start_station, end_station)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@bp.route('/get_price_by_train_id_and_station_strict', methods=['POST'])
def get_price_by_train_id_and_station_strict():
    if 'username' in session:
        train_id = request.form.get('train_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        db_connection = get_db_connection()
        prices = Price.get_price_by_train_id_and_station_strict(db_connection, train_id, start_station, end_station)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@bp.route('/update_price', methods=['POST'])
def update_price():
    if 'username' in session:
        train_id = request.form.get('train_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        business_seat_price = request.form.get('business_seat_price')
        first_class_seat_price = request.form.get('first_class_seat_price')
        second_class_seat_price = request.form.get('second_class_seat_price')
        if train_id and start_station and end_station and business_seat_price and first_class_seat_price and second_class_seat_price:
            db_connection = get_db_connection()
            x = Price.update_price(db_connection, train_id, start_station, end_station, business_seat_price, first_class_seat_price, second_class_seat_price)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '修改成功'})
            else:
                return jsonify({'status': 'error', 'message': '修改失败'}), 500
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    else:
        return redirect(url_for('login'))