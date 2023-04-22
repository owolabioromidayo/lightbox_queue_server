export FLASK_APP="server.py"
flask db init
flask db migrate
flask db upgrade