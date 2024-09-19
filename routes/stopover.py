from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from models.db import get_db_connection
from models.schedule_stopover_time import Schedule_stopover_time
import json

bp = Blueprint('stopover', __name__)


@bp.route('/get_stopover_times_by_schedule_id', methods=['POST'])
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


@bp.route('/edit_schedule_stopover_time', methods=['POST'])
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