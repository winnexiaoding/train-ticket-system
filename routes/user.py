from flask import (Blueprint, render_template, request, redirect, url_for, session, jsonify )
from models.user import User
from models.db import get_db_connection


bp = Blueprint('user', __name__)


@bp.route('/user_manage')
def user_manage():
    if 'username' in session:
        return render_template('user_manage.html', active_link='user_manage')
    return redirect(url_for('login'))


@bp.route('/show_all_users', methods=['POST'])
def show_all_users():
    if 'username' in session:
        db_connection = get_db_connection()
        users = User.get_all_users(db_connection)
        db_connection.close()
        return jsonify({'status': 'success', 'data': users})
    else:
        return redirect(url_for('login'))


@bp.route('/user_search', methods=['POST'])
def user_search():
    if 'username' in session:
        name = request.form.get('name')
        db_connection = get_db_connection()
        users = User.search_user(db_connection, name)
        db_connection.close()
        return jsonify({'status': 'success', 'data': users})
    else:
        return redirect(url_for('login'))


@bp.route('/delete_user', methods=['POST'])
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


@bp.route('/edit_user', methods=['POST'])
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


@bp.route('/change_password', methods=['POST'])
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