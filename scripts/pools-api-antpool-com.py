#!/usr/bin/env python3
###############################################
# Pool: antpool.com
# API request for worker hashrate:
# * POST https://antpool.com/api/workers.htm
# Result:
# {
#     "code": 0,
#     "message": "ok",
#     "data": {
#         "rows": [
#             {
#                 "worker": "mmme.001",
#                 "last10m": "12075276.49807545",
#                 "last30m": "0",
#                 "last1h": "0",
#                 "last1d": "0",
#                 "prev10m": "12075276.49807545",
#                 "prev30m": "0",
#                 "prev1h": "0",
#                 "prev1d": "0",
#                 "accepted": "0",
#                 "stale": "0",
#                 "dupelicate": "0",
#                 "other": "0"
#             }
#         ],
#         "page": 1,
#         "totalPage": 1,
#         "pageSize": 10,
#         "totalRecord": 1
#     }
# }
#
# API request for user earnings:
# * POST https://antpool.com/api/account.htm
# Result:
# {
#     "code": 0,
#     "message": "ok",
#     "data": {
#         "earn24Hours": "0.00000000",
#         "earnTotal": "0.00578638",
#         "paidOut": "0.00512436",
#         "balance": "0.00066202",
#         "settleTime": "2020-03-27"
#     }
# }
#
# API request for daily profit:
# * https://v3.antpool.com/auth/v3/index/ppsplusReward?coinType=BTC
# Result:
# {
#     "code": "000000",
#     "msg": "",
#     "data": {
#         "avgBlockReward": "12.67918414",
#         "ppsPercent": "97.25 %",
#         "ppsReward": "0.00001807",
#         "ppsPlusReward": "0.00003565"
#     }
# }
#
# Output:
# Pool API status
# proxy_api_pool enabled=1i
# Speed in H/s
# proxy_api_worker speed=0i,accepted=0i
# Earnings - changes of balance in BTC
# proxy_api_worker earnings=0.0
# Profit in BTC/TH/s/day
# proxy_api_pool profit=0.0
###############################################

import hashlib
import hmac
import json
import requests
import sys
import threading
import time

def get_signature(user, api_key, api_secret, nonce):
    message = user + api_key + str(nonce)
    return hmac.new(api_secret.encode(), msg=message.encode(), digestmod=hashlib.sha256).hexdigest().upper()

def get_worker_speed(worker, api_key, api_secret):
    user = worker.split(".")[0]
    nonce = int(time.time())
    response = requests.post(
        "https://antpool.com/api/workers.htm",
        params={
            "key": api_key,
            "nonce": nonce,
            "signature": get_signature(user, api_key, api_secret, nonce),
            "coin": "BTC",
            "pageEnable": 0,
        }
    )
    if response:
        j = json.loads(response.text)["data"]["rows"]
        for w in j:
            if w["worker"] == worker:
                speed = int(float(w["last10m"]) * 10 ** 6)
                print(f"proxy_api_worker speed={speed}i")

def get_worker_earnings(worker, api_key, api_secret):
    user = worker.split(".")[0]
    nonce = int(time.time())
    response = requests.post(
        "https://antpool.com/api/account.htm",
        params={
            "key": api_key,
            "nonce": nonce,
            "signature": get_signature(user, api_key, api_secret, nonce),
            "coin": "BTC",
        }
    )
    if response:
        j = json.loads(response.text)["data"]
        earnings = float(j["earnTotal"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.get("https://v3.antpool.com/auth/v3/index/ppsplusReward?coinType=BTC")
    if response:
        j = json.loads(response.text)["data"]
        profit = float(j["ppsReward"])
        print(f"proxy_api_pool profit={profit:.18f}")

def main():
    try:
        worker = sys.argv[1]
        api_key = sys.argv[2]
        api_secret = sys.argv[3]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker> <api_key> <api_secret>")

    threads = []
    threads.append(threading.Thread(target=get_worker_speed, args=(worker, api_key, api_secret,)))
    threads.append(threading.Thread(target=get_worker_earnings, args=(worker, api_key, api_secret,)))
    threads.append(threading.Thread(target=get_pool_profit))

    for thread in threads:
        thread.start()

    print("proxy_api_pool enabled=1i")

main()
