from flask import Blueprint, render_template

from main.models.user import User
from main.models.worker import Worker

bp = Blueprint('views', __name__, url_prefix="/views")

@bp.route('/users')
def users():
    users = User.query.all()
    return render_template('views/table_users.html', users=users)

@bp.route('/workers')
def workers():
    workers = Worker.query.all()
    return render_template('views/table_workers.html', workers=workers)

# @app.route('/transactions')
# def transactions():
#     transactions = Transaction.query.all()
#     return render_template('transactions.html', transactions=transactions)