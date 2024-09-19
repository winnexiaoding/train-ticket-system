from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from models.ticket import Ticket
from models.user import User
from models.db import get_db_connection
import json

bp = Blueprint('ticket', __name__)


@bp.route('/sale_manage')
def sale_manage():
    if 'username' in session:
        return render_template('sale_manage.html', active_link='sale_manage')
    return redirect(url_for('login'))


@bp.route('/search_tickets_by_station_and_time', methods=['POST'])
def search_tickets_by_station_and_time():
    if 'username' in session:
        datetime = request.form.get('datetime')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        db_connection = get_db_connection()
        results = Ticket.search_tickets_by_station_and_time(db_connection, datetime, start_station, end_station)
        db_connection.close()
        return jsonify({'status': 'success', 'data': results})
    else:
        return redirect(url_for('login'))


@bp.route('/buy_ticket', methods=['POST'])
def buy_ticket():
    if 'username' in session:
        passenger_id = request.form.get('passenger_id')
        # 判断乘客ID是否为空
        if passenger_id is None or passenger_id.strip() == '':
            return jsonify({'status': 'error', 'message': '乘客ID为空'})
        # staff_id 从当前登录的业务员中获取
        staff_id = session['username']
        schedule_id = request.form.get('schedule_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        seat_class = request.form.get('seat_class')
        price = request.form.get('price')
        print(passenger_id, staff_id, schedule_id, start_station, end_station, seat_class, price)
        db_connection = get_db_connection()
        x = Ticket.buy_ticket(db_connection, passenger_id, staff_id, schedule_id, start_station, end_station, seat_class, price)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '购票成功'})
        else:
            return jsonify({'status': 'error', 'message': '购票失败'})
    else:
        return redirect(url_for('login'))


@bp.route('/refund_manage')
def refund_manage():
    if 'username' in session:
        return render_template('refund_manage.html', active_link='refund_manage')
    return redirect(url_for('login'))


@bp.route('/refund_ticket', methods=['POST'])
def refund_ticket():
    if 'username' in session:
        ticket_id = request.form.get('ticket_id')
        db_connection = get_db_connection()
        x = Ticket.refund_ticket(db_connection, ticket_id)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '退票成功'})
        else:
            return jsonify({'status': 'error', 'message': '退票失败'})
    else:
        return redirect(url_for('login'))


@bp.route('/show_all_tickets', methods=['POST'])
def show_all_tickets():
    if 'username' in session:
        db_connection = get_db_connection()
        tickets = Ticket.show_all_tickets(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': tickets})
    else:
        return redirect(url_for('login'))


@bp.route('/search_tickets', methods=['POST'])
def search_tickets():
    if 'username' in session:
        passenger_id = request.form.get('passenger_id')
        staff_id = request.form.get('staff_id')
        schedule_id = request.form.get('schedule_id')
        start_station = request.form.get('start_station')
        end_station = request.form.get('end_station')
        set_class = request.form.get('seat_class')
        operation_time = request.form.get('operation_time')
        db_connection = get_db_connection()
        tickets = Ticket.search_tickets(db_connection, passenger_id, staff_id, schedule_id, start_station, end_station, set_class, operation_time)
        db_connection.close()
        return jsonify({'status': 'success', 'data': tickets})
    else:
        return redirect(url_for('login'))
