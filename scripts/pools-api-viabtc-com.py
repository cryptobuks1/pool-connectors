#!/usr/bin/env python3
###############################################
# Pool: viabtc.com
# API request for worker hashrate:
# * https://www.viabtc.com/res/openapi/v1/hashrate/worker?coin=BTC
# Result:
# {
#     "code": 0,
#     "data": {
#         "count": 2,
#         "curr_page": 1,
#         "data": [
#             {
#                 "coin": "BTC",
#                 "group_id": 14,
#                 "group_name": "group1",
#                 "hashrate_10min": "278542945703",
#                 "hashrate_1hour": "46423824283",
#                 "hashrate_24hour": "0",
#                 "last_active": 1545811200,          # last active time
#                 "reject_rate": "0",
#                 "worker_id": 369,                   # miner id
#                 "worker_name": "1x1",               # miner name
#                 "worker_status": "active"           # miner status
#             },
#             {
#                 "coin": "BTC",
#                 "group_id": null,
#                 "group_name": null,
#                 "hashrate_10min": "0",
#                 "hashrate_1hour": "0",
#                 "hashrate_24hour": "0",
#                 "last_active": 1545808266,
#                 "reject_rate": "0",
#                 "worker_id": 370,
#                 "worker_name": "1x1",
#                 "worker_status": "unactive"
#             }
#         ],
#         "has_next": false,
#         "total": 2,
#         "total_page": 1
#     },
#     "message": "OK"
# }
#
# API request for user earnings:
# * https://www.viabtc.com/res/openapi/v1/profit?coin=BTC
# Result:
# {
#   "code": 0,
#   "data": {
#     "coin": "BTC",
#     "pplns_profit": "0.00010927",
#     "pps_profit": "0.00507849",
#     "solo_profit": "0",
#     "total_profit": "0.00518776"
#   },
#   "message": "OK"
# }
#
# API request for daily profit:
# * https://www.viabtc.com/res/tools/calculator?coin=BTC
# Result:
# {
#     "code": 0,
#     "data": [
#         {
#             "coin": "BTC",
#             "coin_price": {
#                 "CNY": "50281.14",
#                 "USD": "7091.14"
#             },
#             "diff": "13912524048945.91",
#             "hash_unit": [
#                 "TH/s",
#                 "PH/s"
#             ],
#             "hashrate": "1",
#             "pps_fee_rate": "0.04",
#             "profit": {
#                 "BTC": "0.00001756",
#                 "CNY": "0.8829",
#                 "USD": "0.1245"
#             }
#         }
#     ],
#     "message": "OK"
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
    response = requests.get(
        "https://www.viabtc.com/res/openapi/v1/hashrate/worker?coin=BTC",
        headers={"X-API-KEY": api_key}
    )
    if response:
        j = json.loads(response.text)["data"]["data"]
        for w in j:
            if w["worker_name"] == name:
                speed = int(w["hashrate_10min"])
                print(f"proxy_api_worker speed={speed}i")

def get_worker_earnings(api_key):
    response = requests.get(
        "https://www.viabtc.com/res/openapi/v1/profit?coin=BTC",
        headers={"X-API-KEY": api_key}
    )
    if response:
        j = json.loads(response.text)["data"]
        earnings = float(j["total_profit"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.get("https://www.viabtc.com/res/tools/calculator?coin=BTC")
    if response:
        j = json.loads(response.text)["data"][0]["profit"]
        profit = float(j["BTC"])
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
