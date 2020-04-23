#!/usr/bin/env python3
###############################################
# Pool: pool.btc.com
# API request for worker hashrate:
# * https://pool.api.btc.com/v1/worker/
# Result:
# {
#     "err_no":0,
#     "data": {
#         "page": 1,
#         "page_size": 10,
#         "page_count": 1,
#         "total_count": 1,
#         "data": [
#             {
#                 "gid": "-1",
#                 "group_name": "DEFAULT",
#                 "worker_id": "40",
#                 "worker_name": "km",
#                 "shares_1m": "439.8",
#                 "shares_5m": "674.3",
#                 "shares_15m": "733.0",
#                 "shares_unit": "G", --- unit of force
#                 "accept_count": "36395008",
#                 "last_share_time": "1468393691",
#                 "last_share_ip": "192.168.1.254",
#                 "reject_percent": "3.05",
#                 "shares_1d": "23.32" --- 24-Hour Force
#                 "shares_1d_unit": "T" --- 24-hour force unit
#                 "status": "ACTIVE"
#             }
#         ]
#     }
# }
#
# API request for user earnings:
# * https://pool.api.btc.com/v1/account/earn-stats
# Result:
# {
#     "err_no":0,
#     "data":{
#         "total_paid":"2072586",
#         "pending_payouts":"206017",
#         "earnings_yesterday":"22624",
#         "last_payment_time":1583633860,
#         "earnings_today":"8160",
#         "unpaid":"214177",
#         "relative_pps_rate":100,
#         "amount_100t":"151824",
#         "amount_standard_earn":"151824",
#         "amount_standard_unit":"100T",
#         "hashrate_yesterday":{
#             "size":"14.4500",
#             "unit":"T"
#         },
#         "shares_1d":{
#             "size":"14.1400",
#             "unit":"T"
#         }
#     }
# }
#
# API request for daily profit:
# * https://pool.btc.com/v1/coins-income?lang=en
# Result:
# {
#     "err_no": 0,
#     "data": {
#         "btc": {
#             "hashrate": 9.537086085181465e+19,
#             "diff": 16552923967337,
#             "income_hashrate_unit": "T",
#             "income_coin": 1.5191098300358e-5,
#             "income_usd": 0.10369701948496,
#             "income_cny": 0.7383227787329,
#             "income_optimize_coin": 1.60046601357788e-5,
#             "income_optimize_usd": 0.1092505308790547,
#             "income_optimize_cny": 0.7778637798588531,
#             "diff_adjust_time": 1585197939,
#             "next_diff": 15160595712909,
#             "next_income_coin": 1.6570127516603e-5,
#             "next_income_usd": 0.11311050735001,
#             "next_income_cny": 0.80534681233207,
#             "payment_mode": "FPPS"
#         }
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

import json
import requests
import sys
import threading

unit = {
    'K': 10 ** 3,
    'M': 10 ** 6,
    'G': 10 ** 9,
    'T': 10 ** 12,
    'P': 10 ** 15
}

def get_worker_speed(worker, puid, access_token):
    name = worker.split(".")[1]
    response = requests.get(f"https://pool.api.btc.com/v1/worker/?puid={puid}&access_key={access_token}")
    if response:
        j = json.loads(response.text)["data"]["data"]
        for w in j:
            if w["worker_name"] == name:
                speed = int(float(w["shares_1m"]) * unit[w["shares_unit"]])
                accepted = int(w['accept_count'])
                print(f"proxy_api_worker speed={speed}i,accepted={accepted}i")

def get_worker_earnings(puid, access_token):
    response = requests.get(f"https://pool.api.btc.com/v1/account/earn-stats?puid={puid}&access_key={access_token}")
    if response:
        j = json.loads(response.text)["data"]
        earnings = float(j["earnings_today"]) / 10 ** 8
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.get(f"https://pool.btc.com/v1/coins-income?lang=en")
    if response:
        j = json.loads(response.text)["data"]["btc"]
        profit = float(j["income_optimize_coin"]) / (unit[j["income_hashrate_unit"]] / unit["T"])
        print(f"proxy_api_pool profit={profit:.18f}")

def main():
    try:
        worker = sys.argv[1]
        puid = sys.argv[2]
        access_token = sys.argv[3]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker> <puid> <access_key>")

    threads = []
    threads.append(threading.Thread(target=get_worker_speed, args=(worker, puid, access_token,)))
    threads.append(threading.Thread(target=get_worker_earnings, args=(puid, access_token,)))
    threads.append(threading.Thread(target=get_pool_profit))

    for thread in threads:
        thread.start()

    print("proxy_api_pool enabled=1i")

main()
