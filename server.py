import os, sys, json, random, base64, time, copy, requests
from flask import Flask, send_file, request, render_template
from flask_socketio import SocketIO, send, emit 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis, pickle, threading, time


from main.models.user import User
from main.models.worker import Worker

from main import app, db

from views.routes import bp as views_bp
from  auth.routes import bp as auth_bp

app.register_blueprint(views_bp)
app.register_blueprint(auth_bp)


# r = redis.Redis(port=6379)
AGREED_FEDERATED_TOKEN = "something_more_secret"

workers = dict()
work_queue = dict()
work_returns = dict()

worker_id_map  = dict() #to prevent token stealing, maps generated id to token

#restore data if crash
# if r.get("workers") and r.get("work_queue") and r.get("work_returns"):
#     workers = pickle.loads(r.get("workers"))
#     work_queue = pickle.loads(r.get("work_queue"))
#     work_returns = pickle.loads(r.get("work_returns"))

#     time.sleep(10) #to allow everyone to reconnect

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"],
    storage_uri="memory://",
    strategy="fixed-window", # or "moving-window"
)


socketio = SocketIO(app, logger=True, max_http_buffer_size=5*10e6)




# def periodic_save_redis():
#     while True: 
        
#         r.set('workers', pickle.dumps(workers))
#         r.set('work_queue', pickle.dumps(work_queue))
#         value = pickle.loads(r.get('foo'))
#         print(value[1]['1'])

#         time.sleep(2*60)

# thread = threading.Thread(target=periodic_save_redis)
# thread.start()






@socketio.on('broadcast information')
def handle_broadcast_information(_json):
    #need to have something here for adding new worker, etc, having a worker poll
    # print(_json)
    api_id, models = _json["data"]["api_id"], _json["data"]["models"]

    try:
        worker_id = Worker.decode_auth_token(api_id)

        worker= Worker.query.filter_by(id=worker_id).first() #check if this fails
        if worker:
            _id = worker.username + "_" + str(worker.id)
            workers[_id] = {"models" : models, "in_use": False}
            work_queue[_id] = []

            worker_id_map[api_id]= _id

            print(_id)
            emit('broadcast information', 'Authenticated')
    except:
        emit('broadcast information', 'Worker object could not be loaded')


@socketio.on('done task')
def handle_done_task(_json):
    _response, timestamp =  _json["_response"], _json["timestamp"]

    print("Handling done task with data ", _json)
    work_returns[timestamp] = _response

    # print(work_returns)
    return 

@socketio.on('aborted task')
def handle_aborted_task(_json):
    error, timestamp =  _json["error"], _json["timestamp"]
    print("Task failed with reason ", error)

    work_returns[timestamp] = "Failed"

    # print(work_returns)
    return 

@socketio.on('get work')
def get_work_for_id(_json):
    api_id = _json["_id"]
    _id = worker_id_map[api_id]

    if len(work_queue[_id]) > 0:
        new_task = work_queue[_id].pop()

        print(f" Sending new task", new_task)
        emit('execute task', new_task)

    else:
        emit("no task")



@app.route("/workers", methods=["GET"])
def get_workers():
    return workers



@app.route("/federated/execute_task/<_id>", methods=["GET","POST"])
def exec_federated_task(_id):
    _json = None #only cares about 

    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        _json = request.json

    #token verification
        token = _json["token"]
        if token != AGREED_FEDERATED_TOKEN:
            return "Invalid Token", 401

    else:
        return  "Content-Type not supported", 400

    worker = workers[_id]

    while worker["in_use"] == True:
        socketio.sleep(5)
        continue

    worker["in_use"] = True

    #dispatch work to worker
    timestamp = time.time()
    work_queue[_id].insert(0, { "model": _json["model"], "args": _json, "timestamp": timestamp})
    work_returns[timestamp] = None

    while work_returns[timestamp] == None:
        socketio.sleep(5)
        continue

    worker["in_use"] = False 

    if work_returns[timestamp] == "Failed":
        return "Task was aborted by GPU client", 500
    
    _response = copy.deepcopy(work_returns[timestamp])
    print("Finished task with return obj")
    del work_returns[timestamp]
    return  {"data" : _response}


@app.route("/make_federated_request/<_id>", methods=["GET","POST"])
def query_federated_server(_id):
    _json = None
    user = None

    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        _json = request.json

    #token verification
        token = _json["token"]
        try:
            user_id = User.decode_auth_token(token)

            if isinstance(user_id, str):
                return user_id, 401
            
            print(user_id, token)

        except:
            return "Invalid Token", 401

    else:
        return  "Content-Type not supported", 400
    
    _json["token"] = AGREED_FEDERATED_TOKEN
    _url = _json["url"]

    #make federated request to server
    response = requests.get(f"{_url}/federated/execute_task/{_id}", json=_json)
    if response.status_code == 200:
        return response.json()
    else:
        return "Request failed", response.status_code


@app.route("/execute_task/<_id>", methods=["GET","POST"])
def exec_task(_id):
    _json = None
    user = None

    content_type = request.headers.get("Content-Type")
    if (content_type == "application/json"):
        _json = request.json

    #token verification
        token = _json["token"]
        try:
            user_id = User.decode_auth_token(token)

            if isinstance(user_id, str):
                return user_id, 401
            
            print(user_id, token)
            # user = User.query.filter_by(id=user_id).first() #check if this fails
            # if not user:
            #     raise ValueError

        except:
            return "Invalid Token", 401

    else:
        return  "Content-Type not supported", 400

    worker = workers[_id]


    while worker["in_use"] == True:
        socketio.sleep(5)
        continue

    worker["in_use"] = True

    #dispatch work to worker
    timestamp = time.time()
    work_queue[_id].insert(0, { "model": _json["model"], "args": _json, "timestamp": timestamp})
    work_returns[timestamp] = None

    while work_returns[timestamp] == None:
        socketio.sleep(5)
        continue

    worker["in_use"] = False 

    if work_returns[timestamp] == "Failed":
        return "Task was aborted by GPU client", 500
    
    _response = copy.deepcopy(work_returns[timestamp])
    print("Finished task with return obj")
    del work_returns[timestamp]
    return  {"data" : _response}


if __name__ == "__main__":
    socketio.run(app, debug=True, port=3003) 









    
