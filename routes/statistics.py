from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint
from models.db import get_db_connection
from models.statistics import Statistics


bp = Blueprint('statistics', __name__)


@bp.route('/statistics_train')
def statistics_train():
    if 'username' in session:
        return render_template('statistics_train.html', active_link='statistics_train')
    return redirect(url_for('login'))


@bp.route('/get_all_statistics_of_train', methods=['POST'])
def get_all_statistics_of_train():
    if 'username' in session:
        db_connection = get_db_connection()
        statistics = Statistics.get_all_statistics_of_train(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': statistics})
    else:
        return redirect(url_for('login'))


@bp.route('/get_statistics_by_train_id_and_date', methods=['POST'])
def get_statistics_by_train_id_and_date():
    if 'username' in session:
        train_id = request.form.get('train_id')
        date = request.form.get('date')
        print(train_id, date)
        db_connection = get_db_connection()
        statistics = Statistics.get_statistics_by_train_id_and_date(db_connection, train_id, date)
        db_connection.close()
        return jsonify({'status': 'success', 'data': statistics})
    else:
        return redirect(url_for('login'))


@bp.route('/statistics_staff')
def statistics_staff():
    if 'username' in session:
        return render_template('statistics_staff.html', active_link='statistics_staff')
    return redirect(url_for('login'))


@bp.route('/get_statistics_by_date', methods=['POST'])
def get_statistics_by_date():
    if 'username' in session:
        # 获取两个时间
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        connection = get_db_connection()
        # 获取统计数据
        statistics = Statistics.get_statistics_of_staff_by_date(connection, start_date, end_date)
        connection.close()
        return jsonify({'status': 'success', 'data': statistics})