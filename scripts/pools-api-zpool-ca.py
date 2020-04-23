#!/usr/bin/env python3
###############################################
# Pool: zpool.ca
# API request for worker hashrate and earnings:
# * https://www.zpool.ca/api/walletEX?address=WALLET_ADDRESS
# Result:
# {
#     "currency": "BTC",
#     "unsold": 1.6319901806703E-6,
#     "balance": 0.00023031,
#     "unpaid": 0.00023194,
#     "paid24h": 0.00000000,
#     "total": 0.00023194,
#     "miners": [
#         {
#             "version": "miningmeter-proxy\/1.0",
#             "password": "c=BTC",
#             "ID": "",
#             "algo": "sha256",
#             "difficulty": 27570,
#             "subscribe": 0,
#             "accepted": 14146316602966,
#             "rejected": 1088178200228.2
#         }
#     ],
#     "payouts": [],
#     "error": ""
# }
#
# Output:
# Pool API status
# proxy_api_pool enabled=1i
# Speed in H/s
# proxy_api_worker speed=0i
# Earnings - changes of balance in BTC
# proxy_api_worker earnings=0.0
###############################################

import json
import requests
import sys
import time

def main():
    try:
        wallet = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <wallet>")

    print("proxy_api_pool enabled=1i")
    response = requests.get(f"https://www.zpool.ca/api/walletEX?address={wallet}")
    if response:
        print(response.text)
        j = json.loads(response.text)
        earnings = float(j["total"])
        print(f"proxy_api_worker earnings={earnings:.18f}")
        if len(j["miners"]) > 0:
            speed = int(j["miners"][0]["accepted"])
            print(f"proxy_api_worker speed={speed}i")

main()
