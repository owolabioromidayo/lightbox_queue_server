import  json, random, base64, time, copy, requests, datetime 
from flask import Flask, send_file, request, render_template
from flask_socketio import SocketIO, send, emit 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


import heapq


from main.models.user import User
from main.models.worker import Worker

from main import app, db

from views.routes import bp as views_bp
from  auth.routes import bp as auth_bp



class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

    def __len__(self):
        return len(self._queue)

app.register_blueprint(views_bp)
app.register_blueprint(auth_bp)


# r = redis.Redis(port=6379)
AGREED_FEDERATED_TOKEN = "something_more_secret"
TRUST_SCORE_UPDATE = 40
TRUST_SCORE_RESET_PVE_HRS = 24
TRUST_SCORE_RESET_NVE_HRS = 48

workers = dict()
work_queue = dict()
work_returns = dict()

worker_id_map  = dict() #to prevent token stealing, maps generated id to token


limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"],
    storage_uri="memory://",
    strategy="fixed-window", # or "moving-window"
)


socketio = SocketIO(app, logger=True, max_http_buffer_size=100*10e6, cors_allowed_origins="*")





@socketio.on('broadcast information')
def handle_broadcast_information(_json):
    # print(_json)
    api_id, models = _json["data"]["api_id"], _json["data"]["models"]

    #reconnects could be handled here

    try:
        worker_id = Worker.decode_auth_token(api_id)
        print("worker id found", worker_id)

        # worker= Worker.query.filter_by(id=worker_id).first() #check if this fails
        worker = db.session.query(Worker).filter_by(id=worker_id).first() 
        if not worker:
            raise ValueError
        

        #update worker broadcast
        worker.last_broadcast = json.dumps(models, indent=1)
        db.session.commit()

        #configure worker queue
        _id = worker.username + "_" + str(worker.id)
        workers[_id] = {"models" : models, "in_use": False}
        work_queue[_id] = PriorityQueue()

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

    # worker = workers[_id]

    #dispatch work to worker
    timestamp = time.time()
    work_queue[_id].push({ "model": _json["model"], "args": _json, "timestamp": timestamp}, 400 ) #queue servers have lower priority
    work_returns[timestamp] = None

    while work_returns[timestamp] == None:
        socketio.sleep(5)
        continue

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

        except:
            return "Invalid Token", 401
    else:
        return  "Content-Type not supported", 400

    user = db.session.query(User).filter_by(id=user_id).first() 
    if not user:
        raise ValueError
    
    # print("this works ")
    # user = User.query.filter_by(id=user_id).first() #check if this fails

    #check trust score and last update time
    time_delta = datetime.datetime.utcnow() - user.last_update_time 
    hours_delta = time_delta / datetime.timedelta(hours=1)

    if user.trust_score > 0 and hours_delta >= TRUST_SCORE_RESET_PVE_HRS:
        user.trust_score = 1000
        db.session.commit()

    if user.trust_score <= 0 and hours_delta >= TRUST_SCORE_RESET_NVE_HRS:
        user.trust_score = 1000
        db.session.commit()

    print("we got here")            
    if user.trust_score <= 0:
        return "Request rejected, trust score too low", 403

    worker = workers[_id]

    #dispatch work to worker
    timestamp = time.time()
    #get worker priority
    work_queue[_id].push({ "model": _json["model"], "args": _json, "timestamp": timestamp}, user.trust_score)
    work_returns[timestamp] = None

    while work_returns[timestamp] == None:
        socketio.sleep(5)
        continue

    if work_returns[timestamp] == "Failed":
        return "Task was aborted by GPU client", 500
    
    user.trust_score -= TRUST_SCORE_UPDATE #trust score update
    db.session.commit()

    _response = copy.deepcopy(work_returns[timestamp])
    print("Finished task with return obj")
    del work_returns[timestamp]
    return  {"data" : _response}


if __name__ == "__main__":
    socketio.run(app, debug=False, port=3009) 









    
