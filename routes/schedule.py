from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from models.schedule import Schedule
from models.db import get_db_connection

bp = Blueprint('schedule', __name__)


@bp.route('/get_schedule_by_train_id', methods=['POST'])
def get_schedule_by_train_id():
    if 'username' in session:
        train_id = request.form.get('train_id')
        db_connection = get_db_connection()
        schedules = Schedule.get_schedule_by_train_id(db_connection, train_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': schedules})
    else:
        return redirect(url_for('login'))


@bp.route('/get_schedule_by_schedule_id', methods=['POST'])
def get_schedule_by_schedule_id():
    if 'username' in session:
        schedule_id = request.form.get('schedule_id')
        db_connection = get_db_connection()
        schedule = Schedule.get_schedule_by_schedule_id(db_connection, schedule_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': schedule})
    else:
        return redirect(url_for('login'))


@bp.route('/add_schedule', methods=['POST'])
def add_schedule():
    if 'username' in session:
        train_id = request.form.get('train_id')
        departure_time = request.form.get('departure_time')
        if train_id and departure_time:
            db_connection = get_db_connection()

            x = Schedule.add_schedule(db_connection, train_id, departure_time)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '添加成功'})
            else:
                return jsonify({'status': 'error', 'message': '添加失败'}), 500
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    else:
        return redirect(url_for('login'))


@bp.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    if 'username' in session:
        schedule_id = request.form.get('schedule_id')
        db_connection = get_db_connection()
        x = Schedule.delete_schedule_by_schedule_id(db_connection, schedule_id)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '删除失败'})