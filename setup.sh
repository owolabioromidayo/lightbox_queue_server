export FLASK_APP=server.py
flask db init
flask db migrate
flask db upgrade
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365