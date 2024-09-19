from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models.user import User
from models.db import get_db_connection
from passlib.hash import sha256_crypt

bp = Blueprint('auth', __name__)


@bp.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')


@bp.route('/get_user', methods=['POST'])
def get_user():
    db_connection = get_db_connection()
    if 'username' in session:
        uid = session['username']
        name = User.get_user_by_username(db_connection, uid)[2]
        db_connection.close()
        return jsonify({'status': 'success', 'name': name})
    else:
        return jsonify({'status': 'error', 'message': '请先登录'}), 401


@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/login', methods=['POST'])
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


@bp.route('/register', methods=['POST'])
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