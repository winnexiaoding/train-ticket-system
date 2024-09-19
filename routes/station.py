from flask import (
    Blueprint, redirect, render_template, request, session, url_for, jsonify
)
from models.db import get_db_connection
from models.station import Station

bp = Blueprint('station_manage', __name__)


@bp.route('/station_manage')
def station_manage():
    if 'username' in session:
        return render_template('station_manage.html', active_link='station_manage')
    return redirect(url_for('login'))


@bp.route('/station_add', methods=['POST'])
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


@bp.route('/station_delete', methods=['POST'])
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


@bp.route('/station_search', methods=['POST'])
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


@bp.route('/station_all', methods=['POST'])
def station_all():
    if 'username' in session:
        db_connection = get_db_connection()
        stations = Station.get_all_stations(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': stations})
    else:
        return redirect(url_for('login'))