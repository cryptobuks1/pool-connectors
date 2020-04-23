#!/usr/bin/env python3
###############################################
# Pool: emcd.io
# API request for worker hashrate:
# * https://api.emcd.io/v1/btc/workers/<api_key>
# Result:
# {
#     "total_count":{
#         "all":1,
#         "active":1,
#         "inactive":0
#     },
#     "total_hashrate":{
#         "hashrate":10789874107242,
#         "hashrate1h":12822748939041,
#         "hashrate24h":12570268491181
#     },
#     "details":[
#         {
#             "worker":"worker",
#             "hashrate":10789874107242,
#             "hashrate1h":12822748939041,
#             "hashrate24h":12570268491181,
#             "active":1
#         }
#     ]
# }
#
# API request for user earnings:
# * https://api.emcd.io/v1/info/<api_key>
# Result:
# {
#     "username":"mmeter",
#     "bitcoin":{
#         "balance":0.00129399,
#         "total_paid":0.01894419,
#         "address":"39EiX6AzigNUPmtXCV8D4GieNUeBY8M4Tn",
#         "min_payout":0.002
#     },
#     "litecoin":{ . . . },
#     "bitcoin_cash":{ . . . },
#     "bitcoin_sv":{ . . . },
#     "notifications":{
#         "email":0,
#         "telegram":0
#     }
# }
#
# API request for daily profit:
# * https://common.emcd.io/get_calc?emcd=1
# Result:
# {
#     "coins":{
#         "btc":"0.00001582",
#         "ltc":"50.40836000",
#         "bsv":"0.00067075",
#         "bch":"0.00046294"
#     },
#     "code":200
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
    response = requests.get(f"https://api.emcd.io/v1/btc/workers/{api_key}")
    if response:
        j = json.loads(response.text)["details"]
        for w in j:
            if w["worker"] == name:
                speed = int(j[0]["hashrate"])
                print(f"proxy_api_worker speed={speed}i")

def get_worker_earnings(api_key):
    response = requests.get(f"https://api.emcd.io/v1/info/{api_key}")
    if response:
        j = json.loads(response.text)["bitcoin"]
        earnings = float(j["balance"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.get(f"https://common.emcd.io/get_calc?emcd=1")
    if response:
        j = json.loads(response.text)["coins"]
        profit = float(j["btc"])
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
