#!/usr/bin/env python3
###############################################
# Pool: f2pool.com
# API request for user info:
# * https://api.f2pool.com/bitcoin/<user>
# Result:
# {
#     "balance": 0.004012548053641662,
#     "fixed_balance": 0.004012548053641662,
#     "fixed_value": 0.024133828053641664,
#     "hashes_last_day": 0,
#     "hashes_last_hour": 0,
#     "hashrate": 0,
#     "hashrate_history": {
#         "2020-04-01T10:00:00Z": 0
#     },
#     "hashrate_history_local": {
#         "2020-04-01T10:00:00Z": 0
#     },
#     "last": {},
#     "local_hash": 0,
#     "ori_hashes_last_day": 0,
#     "ori_hashrate": 0,
#     "ori_value_last_day": 0,
#     "paid": 0.02012128,
#     "payout_history": [
#         [
#             "2020-03-28T00:00:00Z",
#             null,
#             0.0000744
#         ]
#     ],
#     "payout_history_fee": [
#         [
#             "2020-03-28T00:00:00Z",
#             null,
#             0.00000147
#         ]
#     ],
#     "stale_hashes_rejected_last_day": 0,
#     "stale_hashes_rejected_last_hour": 0,
#     "value": 0.024133828053641664,
#     "value_change": 0,
#     "value_last_day": 0,
#     "value_today": 0,
#     "worker_length": 0,
#     "worker_length_online": 0,
#     "workers": [
#         [
#             "minerx01",                       // Name
#             12650560751040,                   // Hashrate
#             0,                                // Last 1 hour's hashrate
#             0,                                // Rejected shares of past 1 hour
#             1084452716521979904,              // Hashrate of last 24 hours
#             2533274790395904,                 // Stale rejected hashes of last 24 hours
#             "2018-06-19T10:02:19.810789Z",    // Recently submitted shares
#             false                             // Extra Fields
#         ]
#     ]
# }
#
# API request for daily profit:
# * POST https://www.f2pool.com/coins-chart?currency_code=btc
# Result:
# {
#     "status": "ok",
#     "data": {
#         "id": 73,
#         "code": "btc",
#         "name": "Bitcoin",
#         "algorithm": "SHA256d",
#         "prooftype": "PoW",
#         "total_supply": 21000000,
#         "blocktime": 600,
#         "diff_adj": 2016,
#         "reduction_reward": 210000,
#         "profit_per_hash": "T",
#         "miners": "106,172",
#         "extra": {},
#         "icon64_origin": "btc-64x64.png",
#         "icon64": "/assets/currencies/logo/btc-64x64.png",
#         "icon128_origin": "btc-128x128.png",
#         "icon128": "/assets/currencies/logo/btc-128x128.png",
#         "marketcap": 116430971921.11002,
#         "price": 6362.80019461,
#         "volume24h": 33382482911.7742,
#         "circulating_supply": 18298700,
#         "rank": 1,
#         "percent_change_24h": -1.25467,
#         "blocknumber": 623898,
#         "blockreward": 12.5,
#         "network_hashrate_double_last24h": 103329072868491380000,
#         "network_hashrate_double_last72h": 102091278036509670000,
#         "network_hashrate_double_last168h": 97669556798125900000,
#         "timestamp": 1585765935000,
#         "network_hashrate_split": 1000000000,
#         "network_hashrate_split2": 1000000000,
#         "network_hashrate_double": 105.319737670057,
#         "difficulty_split": 1000000000,
#         "difficulty_double": 13912.524048945908,
#         "difficulty24_split": 1000000000,
#         "difficulty24_double": 13912.524048945908,
#         "blockreward_reward": 0,
#         "blocktime_real": 0,
#         "remain_minable": 2701300,
#         "remain_minable_pro": 0.12863333333333332,
#         "output24h_coin": 1800,
#         "output24h": 11453040.350298,
#         "network_hashrate": 105319737670056980000,
#         "difficulty": 13912524048945.908,
#         "profit_per_t": 0.00001788,
#         "profit24h": 0.11376686747962682,
#         "profit_by_day": 1.788e-17,
#         "estimated_profit": 0.00001788,
#         "estimated_profit_usd": 0.11376686747962682,
#         "estimated_profit_scales": 1000000000000,
#         "currency_scales": 1000000000000,
#         "halving_remain_hours": 1017,
#         "halving_countdown": "42 days 9 hours",
#         "chart_data": [
#             {
#                 "hashrate": 121692458824909860000,
#                 "price": 8611.78682537,
#                 "timestamp": 1583121600000
#             }
#         ]
#     }
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

def get_worker_speed_and_earnings(worker):
    user, name = worker.split(".")
    response = requests.get(f"https://api.f2pool.com/bitcoin/{user}")
    if response:
        j = json.loads(response.text)
        for w in j["workers"]:
            if w[0] == name:
                speed = int(w[1])
                print(f"proxy_api_worker speed={speed}i")
        earnings = float(j["value"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit():
    response = requests.post(f"https://www.f2pool.com/coins-chart?currency_code=btc")
    if response:
        j = json.loads(response.text)["data"]
        profit = float(j["profit_per_t"])
        print(f"proxy_api_pool profit={profit:.18f}")

def main():
    try:
        worker = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker>")

    threads = []
    threads.append(threading.Thread(target=get_worker_speed_and_earnings, args=(worker,)))
    threads.append(threading.Thread(target=get_pool_profit))

    for thread in threads:
        thread.start()

    print("proxy_api_pool enabled=1i")

main()
