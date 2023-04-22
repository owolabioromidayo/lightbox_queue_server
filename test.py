import requests, threading, time

# def func(i):
#     _id = (i % 2) + 1
#     response = requests.post("http://localhost:3003/hey", json={"worker_id": _id})
#     print(response.__dict__)

# for i in range(5):
#     thread = threading.Thread(target=func, args=(i,)) 
#     thread.start()


# while True:

# response = requests.get("http://localhost:3003/user/register", json={"username":"bigmike", "password" : "hellothere", "email": "Thisplacesucks@mail.com"})
# print(response.__dict__)

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NzkyMzM1MzMsImlhdCI6MTY3ODM2OTUzMywiaWQiOjR9.YC_P9HMCRcmvX0lhMnVb_tr9hTrvGF5I2fdpkAh-2G8"

# response = requests.get("http://localhost:3003/auth/api/login", json={"username":"owolabioromidayo1", "password" : "frock"})
# print(response.__dict__)
# token = response.content.decode("utf-8")
# print(token, type(token))


response = requests.get("http://localhost:3003/workers")
broadcast = response.json()
print(len(broadcast))

chosen_worker_key = list(broadcast.keys())[0]
chosen_worker = broadcast[chosen_worker_key]

# print(chosen_worker)

args = {
    "model": "wavymulder/Analog-Diffusion",
    "prompt": "emma stone",
    "iters" : 5,
    "token" : token
}

# #eventually i should be able to just tell it what model im interested in and thats all 
response = requests.get(f"http://localhost:3003/execute_task/{chosen_worker_key}", json=args)
print(response.__dict__) #get this to the level where it prints the b64
    # time.sleep(5)