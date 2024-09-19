from flask import (
    Blueprint, redirect, render_template, session, url_for
)


bp = Blueprint('home', __name__)


@bp.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', active_link='home')
    return redirect(url_for('login'))
