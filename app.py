import json

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from models.user import User
from models.station import Station
from models.train import Train
from models.price import Price
from models.ticket import Ticket
from models.schedule import Schedule
from models.statistics import Statistics
from models.train_stopover import TrainStopover
from models.schedule_stopover_time import  Schedule_stopover_time
from config import Config
from passlib.hash import sha256_crypt
from models.db import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)
Session(app)


@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/get_user', methods=['POST'])
def get_user():
    db_connection = get_db_connection()
    if 'username' in session:
        uid = session['username']
        name = User.get_user_by_username(db_connection, uid)[2]
        db_connection.close()
        return jsonify({'status': 'success', 'name': name})
    else:
        return jsonify({'status': 'error', 'message': '请先登录'}), 401


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def handle_login():
    uid = request.form['username']
    password = request.form['password']
    db_connection = get_db_connection()
    user = User.get_user_by_username(db_connection, uid)
    db_connection.close()
    if user and not user[1]:
        if sha256_crypt.verify(password, user[0]):  # 验证用户密码
            session['username'] = uid
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': '密码错误'}), 401
    else:
        return jsonify({'status': 'error', 'message': '用户名不存在'}), 404


@app.route('/register', methods=['POST'])
def handle_register():
    uid = request.form['username']
    password = request.form['password']
    uname = request.form['name']
    db_connection = get_db_connection()
    if User.get_user_by_username(db_connection, uid):
        db_connection.close()
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 409

    if User.create_user(db_connection, uid, password, uname):
        db_connection.close()
        return jsonify({'status': 'success', 'message': '注册成功'})
    else:
        db_connection.close()
        return jsonify({'status': 'error', 'message': '注册失败'}), 500


@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', active_link='home')
    return redirect(url_for('login'))


@app.route('/station_manage')
def station_manage():
    if 'username' in session:
        return render_template('station_manage.html', active_link='station_manage')
    return redirect(url_for('login'))


@app.route('/station_add', methods=['POST'])
def station_add():
    if 'username' in session:
        db_connection = get_db_connection()
        name = request.form['name']
        # 判断name是否为空

        if name is None or name.strip() == '' or ' ' in name:
            return jsonify({'status': 'error', 'message': '站点名不能为空或包含空格'})
        x = Station.add_station(db_connection, name)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '添加成功'})
        else:
            return jsonify({'status': 'error', 'message': '添加失败'}), 500
    else:
        return redirect(url_for('login'))


@app.route('/station_delete', methods=['POST'])
def station_delete():
    if 'username' in session:
        name = request.form['name']
        db_connection = get_db_connection()
        # 首先寻找有没有这个站点
        if not Station.get_station_by_name(db_connection, name):
            db_connection.close()
            return jsonify({'status': 'error', 'message': '站点不存在'}), 400
        x = Station.delete_station(db_connection, name)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '删除失败，请检查站点是否被使用'})
    else:
        return redirect(url_for('login'))


@app.route('/station_search', methods=['POST'])
def station_search():
    if 'username' in session:
        name = request.form['name']
        db_connection = get_db_connection()
        stations = Station.search_station(db_connection, name)
        db_connection.close()
        print(stations)
        return jsonify({'status': 'success', 'data': stations})
    else:
        return redirect(url_for('login'))


@app.route('/station_all', methods=['POST'])
def station_all():
    if 'username' in session:
        db_connection = get_db_connection()
        stations = Station.get_all_stations(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': stations})
    else:
        return redirect(url_for('login'))


@app.route('/user_manage')
def user_manage():
    if 'username' in session:
        return render_template('user_manage.html', active_link='user_manage')
    return redirect(url_for('login'))


@app.route('/show_all_users', methods=['POST'])
def show_all_users():
    if 'username' in session:
        db_connection = get_db_connection()
        users = User.get_all_users(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': users})
    else:
        return redirect(url_for('login'))


@app.route('/user_search', methods=['POST'])
def user_search():
    if 'username' in session:
        name = request.form.get('name')
        db_connection = get_db_connection()
        users = User.search_user(db_connection, name)
        db_connection.close()
        return jsonify({'status': 'success', 'data': users})
    else:
        return redirect(url_for('login'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' in session:
        uid = request.form['uid']
        db_connection = get_db_connection()

        x = User.delete_user(db_connection, uid)
        db_connection.close()
        if x:
            return jsonify({'status': 'success', 'message': '删除成功'})
        else:
            return jsonify({'status': 'error', 'message': '删除失败'}), 500
    else:
        return redirect(url_for('login'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    if 'username' in session:
        uid = request.form.get('uid')
        uname = request.form.get('newname')
        password = request.form.get('password')

        if uid and uname and password:
            db_connection = get_db_connection()
            x = User.edit_user(db_connection, uid, password, uname)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '修改成功'})
            else:
                return jsonify({'status': 'error', 'message': '密码错误'}), 400
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    else:
        return redirect(url_for('login'))


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' in session:
        uid = request.form.get('uid')
        old_password = request.form.get('oldpassword')
        new_password = request.form.get('newpassword')
        if uid and old_password and new_password:
            db_connection = get_db_connection()

            x = User.update_password(db_connection, uid, old_password, new_password)
            db_connection.close()
            if x:
                return jsonify({'status': 'success', 'message': '修改成功'})
            else:
                return jsonify({'status': 'error', 'message': '旧密码错误'}), 400
        else:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
    else:
        return redirect(url_for('login'))


@app.route('/train_manage')
def train_manage():
    if 'username' in session:
        return render_template('train_manage.html', active_link='train_manage')
    return redirect(url_for('login'))


@app.route('/show_all_trains', methods=['POST'])
def show_all_trains():
    if 'username' in session:
        db_connection = get_db_connection()
        trains = Train.get_all_trains(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': trains})
    else:
        return redirect(url_for('login'))


@app.route('/train_search', methods=['POST'])
def train_search():
    if 'username' in session:
        search_query = request.form.get('search_query')
        db_connection = get_db_connection()
        trains = Train.search_trains(db_connection, search_query)
        db_connection.close()
        return jsonify({'status': 'success', 'data': trains})
    else:
        return redirect(url_for('login'))


@app.route('/delete_train', methods=['POST'])
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


@app.route('/edit_train', methods=['POST'])
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


@app.route('/train_add', methods=['POST'])
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


@app.route('/get_train_stopovers', methods=['POST'])
def get_train_stopovers():
    if 'username' in session:
        train_id = request.form.get('train_id')
        db_connection = get_db_connection()
        stopovers = TrainStopover.get_train_stopovers_by_train_id(db_connection, train_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': stopovers})
    else:
        return redirect(url_for('login'))


@app.route('/update_train_stopovers', methods=['POST'])
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


@app.route('/price_manage')
def price_manage():
    if 'username' in session:
        return render_template('price_manage.html', active_link='price_manage')
    return redirect(url_for('login'))


@app.route('/get_price_by_train_id', methods=['POST'])
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


@app.route('/get_all_price', methods=['POST'])
def get_all_price():
    if 'username' in session:
        db_connection = get_db_connection()
        prices = Price.get_all_price(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': prices})
    else:
        return redirect(url_for('login'))


@app.route('/get_price_by_station', methods=['POST'])
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


@app.route('/get_price_by_train_id_and_station', methods=['POST'])
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


@app.route('/get_price_by_train_id_and_station_strict', methods=['POST'])
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


@app.route('/update_price', methods=['POST'])
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


@app.route('/get_schedule_by_train_id', methods=['POST'])
def get_schedule_by_train_id():
    if 'username' in session:
        train_id = request.form.get('train_id')
        db_connection = get_db_connection()
        schedules = Schedule.get_schedule_by_train_id(db_connection, train_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': schedules})
    else:
        return redirect(url_for('login'))


@app.route('/get_schedule_by_schedule_id', methods=['POST'])
def get_schedule_by_schedule_id():
    if 'username' in session:
        schedule_id = request.form.get('schedule_id')
        db_connection = get_db_connection()
        schedule = Schedule.get_schedule_by_schedule_id(db_connection, schedule_id)
        db_connection.close()
        return jsonify({'status': 'success', 'data': schedule})
    else:
        return redirect(url_for('login'))


@app.route('/add_schedule', methods=['POST'])
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


@app.route('/delete_schedule', methods=['POST'])
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


@app.route('/get_stopover_times_by_schedule_id', methods=['POST'])
def get_stopover_times_by_schedule_id():
    if 'username' in session:
        schedule_id = request.form.get('schedule_id')
        db_connection = get_db_connection()
        stopover_times = Schedule_stopover_time.get_stopover_times_by_schedule_id(db_connection, schedule_id)
        db_connection.close()
        print(stopover_times)
        if stopover_times:
            return jsonify({'status': 'success', 'data': stopover_times})
        else:
            return jsonify({'status': 'error', 'message': '获取站点时间数据失败'})
    else:
        return redirect(url_for('login'))


@app.route('/edit_schedule_stopover_time', methods=['POST'])
def edit_schedule_stopover_time():
    if 'username' in session:
        schedule_id = request.form.get('schedule_id')
        stopovers_json = request.form.get('stopovers')
        stopovers = json.loads(stopovers_json)
        new_stopovers = []

        for stopover_data in stopovers:
            new_stopovers.append({
                'stop_duration': int(stopover_data['stop_duration']),
                'time_to_next_stopover': int(stopover_data['time_to_next_stopover'])
            })

        db_connection = get_db_connection()
        if Schedule_stopover_time.update_stopover_time(db_connection, schedule_id, new_stopovers):
            db_connection.close()
            return jsonify({'status': 'success', 'message': '修改成功'})
        else:
            db_connection.close()
            return jsonify({'status': 'error', 'message': '修改失败'})
    else:
        return redirect(url_for('login'))


@app.route('/sale_manage')
def sale_manage():
    if 'username' in session:
        return render_template('sale_manage.html', active_link='sale_manage')
    return redirect(url_for('login'))


@app.route('/search_tickets_by_station_and_time', methods=['POST'])
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


@app.route('/buy_ticket', methods=['POST'])
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


@app.route('/refund_manage')
def refund_manage():
    if 'username' in session:
        return render_template('refund_manage.html', active_link='refund_manage')
    return redirect(url_for('login'))


@app.route('/refund_ticket', methods=['POST'])
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


@app.route('/show_all_tickets', methods=['POST'])
def show_all_tickets():
    if 'username' in session:
        db_connection = get_db_connection()
        tickets = Ticket.show_all_tickets(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': tickets})
    else:
        return redirect(url_for('login'))


@app.route('/search_tickets', methods=['POST'])
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


@app.route('/statistics_train')
def statistics_train():
    if 'username' in session:
        return render_template('statistics_train.html', active_link='statistics_train')
    return redirect(url_for('login'))


@app.route('/get_all_statistics_of_train', methods=['POST'])
def get_all_statistics_of_train():
    if 'username' in session:
        db_connection = get_db_connection()
        statistics = Statistics.get_all_statistics_of_train(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': statistics})
    else:
        return redirect(url_for('login'))


@app.route('/get_statistics_by_train_id_and_date', methods=['POST'])
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


@app.route('/statistics_staff')
def statistics_staff():
    if 'username' in session:
        return render_template('statistics_staff.html', active_link='statistics_staff')
    return redirect(url_for('login'))


@app.route('/get_statistics_by_date', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
