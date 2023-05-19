export FLASK_APP=server.py
flask run --cert=cert.pem --key=key.pem

gunicorn -b 0.0.0.0:8000 