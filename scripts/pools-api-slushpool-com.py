#!/usr/bin/env python3
###############################################
# Pool: slushpool.com
# API request for worker hashrate:
# * https://slushpool.com/accounts/workers/json/btc/
# Result:
# {
#     "btc": {
#         "workers": {
#             "mmeter.worker_mmeter_eu": {
#                 "state": "off",
#                 "last_share": 1585300160,
#                 "hash_rate_unit": "Gh/s",
#                 "hash_rate_scoring": 0.0,
#                 "hash_rate_5m": 0.0,
#                 "hash_rate_60m": 0.0,
#                 "hash_rate_24h": 0.0
#             }
#         }
#     }
# }
#
# API request for user earnings:
# * https://slushpool.com/accounts/profile/json/btc/
# Result:
# {
#     "username": "mmeter",
#     "btc": {
#         "confirmed_reward": "0.00134148",
#         "unconfirmed_reward": "0.00000000",
#         "estimated_reward": "0.00002172",
#         "send_threshold": "0.02000000",
#         "hash_rate_unit": "Gh/s",
#         "hash_rate_5m": 13753.1725,
#         "hash_rate_60m": 7248.1701,
#         "hash_rate_24h": 302.0071,
#         "hash_rate_scoring": 10956.5588,
#         "hash_rate_yesterday": 0.0,
#         "low_workers": 0,
#         "off_workers": 0,
#         "ok_workers": 1,
#         "dis_workers": 0
#     }
# }
#
# API request for daily profit:
# * https://slushpool.com/stats/json/btc/
# Result:
# {
#     "btc": {
#         "luck_b10": "1.14",
#         "luck_b50": "0.84",
#         "luck_b250": "0.93",
#         "hash_rate_unit": "Gh/s",
#         "pool_scoring_hash_rate": 5983167367.9262,
#         "pool_active_workers": 184928,
#         "round_probability": "0.23",
#         "round_started": 1585897675,
#         "round_duration": 2585.0,
#         "blocks": {
#             "624183": {
#                 "date_found": 1585897675,
#                 "mining_duration": 4212,
#                 "total_shares": 5855725579832,
#                 "state": "new",
#                 "confirmations_left": 97,
#                 "value": "12.67207426",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5979094050.713095
#             },
#             "624172": {
#                 "date_found": 1585893463,
#                 "mining_duration": 4231,
#                 "total_shares": 5872392984029,
#                 "state": "new",
#                 "confirmations_left": 86,
#                 "value": "12.53951458",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5972633348.775941
#             },
#             "624162": {
#                 "date_found": 1585889232,
#                 "mining_duration": 1581,
#                 "total_shares": 2194023278494,
#                 "state": "new",
#                 "confirmations_left": 76,
#                 "value": "12.66297685",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5932719861.515021
#             },
#             "624159": {
#                 "date_found": 1585887651,
#                 "mining_duration": 1411,
#                 "total_shares": 1940241452231,
#                 "state": "new",
#                 "confirmations_left": 73,
#                 "value": "12.74580317",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5830703678.49654
#             },
#             "624158": {
#                 "date_found": 1585886240,
#                 "mining_duration": 3207,
#                 "total_shares": 4166349660792,
#                 "state": "new",
#                 "confirmations_left": 72,
#                 "value": "12.77200709",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5600600896.865254
#             },
#             "624156": {
#                 "date_found": 1585883033,
#                 "mining_duration": 6946,
#                 "total_shares": 9215297803844,
#                 "state": "new",
#                 "confirmations_left": 70,
#                 "value": "12.76457022",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5614442070.039768
#             },
#             "624146": {
#                 "date_found": 1585876087,
#                 "mining_duration": 11596,
#                 "total_shares": 15131524891483,
#                 "state": "new",
#                 "confirmations_left": 60,
#                 "value": "12.76365451",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5846763177.255441
#             },
#             "624130": {
#                 "date_found": 1585864491,
#                 "mining_duration": 21463,
#                 "total_shares": 27784383991900,
#                 "state": "new",
#                 "confirmations_left": 44,
#                 "value": "12.60059135",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5789087378.796348
#             },
#             "624093": {
#                 "date_found": 1585843028,
#                 "mining_duration": 17717,
#                 "total_shares": 23553924288279,
#                 "state": "new",
#                 "confirmations_left": 7,
#                 "value": "13.00228874",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5424457120.101567
#             },
#             "624058": {
#                 "date_found": 1585825311,
#                 "mining_duration": 19022,
#                 "total_shares": 26169006118941,
#                 "state": "confirmed",
#                 "confirmations_left": 0,
#                 "value": "12.70714747",
#                 "user_reward": "0.00000000",
#                 "pool_scoring_hash_rate": 5971794713.785212
#             }
#         }
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
import time

unit = {
    'Kh/s': 10 ** 3,
    'Mh/s': 10 ** 6,
    'Gh/s': 10 ** 9,
    'Th/s': 10 ** 12,
    'Ph/s': 10 ** 15
}

def get_worker_speed(worker, access_token):
    response = requests.get(
        "https://slushpool.com/accounts/workers/json/btc/",
        headers={'X-SlushPool-Auth-Token': access_token}
    )
    if response:
        user, name = list(worker.split("."))
        j = json.loads(response.text)["btc"]["workers"][worker]
        speed = int(float(j["hash_rate_5m"]) * unit[j["hash_rate_unit"]])
        print(f"proxy_api_worker speed={speed}i")

def get_worker_earnings(access_token):
    response = requests.get(
        "https://slushpool.com/accounts/profile/json/btc/",
        headers={'X-SlushPool-Auth-Token': access_token}
    )
    if response:
        j = json.loads(response.text)["btc"]
        earnings = float(j["confirmed_reward"]) + float(j["unconfirmed_reward"]) + float(j["estimated_reward"])
        print(f"proxy_api_worker earnings={earnings:.18f}")

def get_pool_profit(access_token):
    response = requests.get(
        "https://slushpool.com/stats/json/btc/",
        headers={'X-SlushPool-Auth-Token': access_token}
    )
    if response:
        j = json.loads(response.text)["btc"]
        d = int(time.time()) - 86400
        profit = 0.0
        for v in j["blocks"].values():
            if int(v["date_found"]) > d and float(v["pool_scoring_hash_rate"]) > 0:
                profit += float(v["value"]) / (float(v["pool_scoring_hash_rate"]) * unit[j["hash_rate_unit"]] / unit["Th/s"])
        print(f"proxy_api_pool profit={profit:.18f}")

def main():
    try:
        worker = sys.argv[1]
        access_token = sys.argv[2]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker> <access_key>")

    threads = []
    threads.append(threading.Thread(target=get_worker_speed, args=(worker, access_token,)))
    threads.append(threading.Thread(target=get_worker_earnings, args=(access_token,)))
    threads.append(threading.Thread(target=get_pool_profit, args=(access_token,)))

    for thread in threads:
        thread.start()

    print("proxy_api_pool enabled=1i")

main()
