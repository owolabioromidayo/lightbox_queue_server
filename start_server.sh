#!/bin/bash                                                                                                                                                                                                                                     echo "starting flask server" | systemd-cat -p info
export FLASK_APP=/root/lightbox_queue_server/server.py 
flask run --host 0.0.0.0 --cert=/root/lightbox_queue_server/cert.pem --key=/root/lightbox_queue_server/key.pem   