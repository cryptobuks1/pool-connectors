#!/usr/bin/env python3
###############################################
# Pool: sigmapool.com
# API request for worker hashrate:
# * https://sigmapool.com/api/v1/btc/workers?search=<worker_name>&key=<api_key>
# Result:
# [
#     {
#         "workername": "worker001",
#         "created": "2020-04-09T13:21:30Z",
#         "hashrate": 11728124029610.666,
#         "avg1Hashrate": 5551312040682.382,
#         "avg24Hashrate": 0,
#         "nShares1h": 4653056,
#         "nShares24h": 0,
#         "lastShareTimeRaw": "2020-04-09T13:21:17.000Z",
#         "status": "ONLINE",
#         "lastShareTime": "2020-04-09T13:21:17.000+00:00",
#         "online": true
#     }
# ]
#
# API request for user earnings:
# * https://sigmapool.com/api/v1/btc/stats?key=<api_key>
# Result:
# {
#     "hashrate": "0 H/s",
#     "avgHashrate1h": "0 H/s",
#     "avgHashrate24h": "0 H/s",
#     "balance": "0.004883396826",
#     "rewards": 0.0048834,
#     "rewards24": 0,
#     "paid": 0,
#     "scheme": "FPPS",
#     "address": "39EiX6AzigNUPmtXCV8D4GieNUeBY8M4Tn",
#     "threshold": 0.005,
#     "profit": {
#         "hour": 0,
#         "day": 0,
#         "week": 0,
#         "month": 0,
#         "halfyear": 0,
#         "year": 0
#     }
# }
#
# API request for daily profit:
# * https://sigmapool.com/api/v1/btc/stats/index
# Result:
# {
#     "hashRateList": [
#         {
#             "x": 1585483200000,
#             "y": 482.76
#         },
#         . . .
#     ],
#     "poolHashrate": "479.14PH/s",
#     "usdRate": 7095.96,
#     "blockHeight": 624677,
#     "minPayout": 0.002,
#     "difficulty": 13912524048945,
#     "difficultyIncrease": 1586349996,
#     "payoutScheme": "FPPS",
#     "payoutTime": "9:00 - 12:00",
#     "profitability24h": 0.000017451238420224,
#     "workerNumber": 5233,
#     "stratum": {
#         "Russia": [
#             "stratum+tcp://ru1.btc.sigmapool.com:3333",
#             "stratum+tcp://ru2.btc.sigmapool.com:3333",
#             "stratum+tcp://ru3.btc.sigmapool.com:3333"
#         ],
#         "Europe": [
#             "stratum+tcp://eu1.btc.sigmapool.com:3333",
#             "stratum+tcp://eu2.btc.sigmapool.com:3333",
#             "stratum+tcp://eu3.btc.sigmapool.com:3333"
#         ],
#         "USA": [
#             "stratum+tcp://us1.btc.sigmapool.com:3333",
#             "stratum+tcp://us2.btc.sigmapool.com:3333"
#         ],
#         "China": [
#             "stratum+tcp://cn1.btc.sigmapool.com:3333"
#         ]
#     },
#     "networkHashrate": "105.68 EH/s"
# }
#
# Output:
# Pool API status
# proxy_api_pool enabled=1i
# Speed in H/s
# proxy_api_worker speed=0i
# Earnings - changes of balance in BTC
# proxy_api_worker earnings=0.0
# Profit in BTC/TH/s/day
# proxy_api_pool profit=0.0
###############################################

import json
import requests
import sys
import threading

def get_worker_speed(worker, api_key):
    name = worker.split(".")[1]
    response = requests.get(f"https://sigmapool.com/api/v1/btc/workers?search={name}&key={api_key}")
    if response:
        j = json.loads(response.text)
        for w in j:
            if w["workername"] == name:
                speed = int(w["hashrate"])
                print(f"proxy_api_worker speed={speed}i")

def get_worker_earnings(api_key):
    response = requests.get(f"https://sigmapool.com/api/v1/btc/stats?key={api_key}")
    if response:
        j = json.loads(response.text)
        earnings = float(j["rewards"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.get("https://sigmapool.com/api/v1/btc/stats/index")
    if response:
        j = json.loads(response.text)
        profit = float(j["profitability24h"])
        print(f"proxy_api_pool profit={profit:.18f}")

def main():
    try:
        worker = sys.argv[1]
        api_key = sys.argv[2]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker> <api_key>")

    threads = []
    threads.append(threading.Thread(target=get_worker_speed, args=(worker, api_key,)))
    threads.append(threading.Thread(target=get_worker_earnings, args=(api_key,)))
    threads.append(threading.Thread(target=get_pool_profit))

    for thread in threads:
        thread.start()

    print("proxy_api_pool enabled=1i")

main()
