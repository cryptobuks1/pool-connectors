#!/usr/bin/env python3
###############################################
# Pool: nicehash.com
# API request for worker hashrate and user earnings:
# * https://api2.nicehash.com/main/api/v2/mining/rigs2/
# Result:
# {
#     "minerStatuses": {
#         "MINING": 1
#     },
#     "rigTypes": {
#         "UNMANAGED": 1
#     },
#     "totalRigs": 1,
#     "totalProfitability": 0.0,
#     "totalDevices": 1,
#     "devicesStatuses": {
#         "MINING": 1
#     },
#     "unpaidAmount": "0",
#     "path": "",
#     "btcAddress": "3MkeTtwhKXAn4P5gGgV3wvzze2PvR9XoZD",
#     "nextPayoutTimestamp": "2020-04-08T12:00:00Z",
#     "miningRigGroups": [],
#     "miningRigs": [
#         {
#             "rigId": "worker0001",
#             "type": "UNMANAGED",
#             "name": "worker0001",
#             "statusTime": 1586333411000,
#             "minerStatus": "MINING",
#             "unpaidAmount": "0",
#             "notifications": [],
#             "stats": [
#                 {
#                     "statsTime": 1586333411000,
#                     "market": "EU",
#                     "algorithm": {
#                         "enumName": "SHA256",
#                         "description": "SHA256"
#                     },
#                     "unpaidAmount": "0",
#                     "difficulty": 500000.0,
#                     "proxyId": 0,
#                     "timeConnected": 1586332956700,
#                     "xnsub": false,
#                     "speedAccepted": 0.0,
#                     "speedRejectedR1Target": 0.0,
#                     "speedRejectedR2Stale": 0.0,
#                     "speedRejectedR3Duplicate": 0.0,
#                     "speedRejectedR4NTime": 0.0,
#                     "speedRejectedR5Other": 0.0,
#                     "speedRejectedTotal": 0.0,
#                     "profitability": 0.0
#                 }
#             ],
#             "profitability": 0.0
#         }
#     ],
#     "rigNhmVersions": [],
#     "externalAddress": false,
#     "pagination": {
#         "size": 25,
#         "page": 0,
#         "totalPageCount": 1
#     }
# }
#
# * https://api2.nicehash.com/main/api/v2/mining/rig/stats/algo?rigId=<worker_name>&afterTimestamp=<time_ms - 24h>&algorithm=1
# Result:
# {
#     "columns": [
#         "time",
#         "unpaid_total_amount",
#         "speed_accepted",
#         "speed_rejected_target",
#         "speed_rejected_stale",
#         "speed_rejected_duplicate",
#         "speed_rejected_ntime",
#         "speed_rejected_other",
#         "profitability"
#     ],
#     "data": [
#         [
#             1586335500000,
#             0E-8,
#             0.0,
#             0.0,
#             0.0,
#             0.0,
#             0.0,
#             0.0,
#             0.0
#         ],
#         . . .
#     ]
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

import hashlib
import hmac
import json
import requests
import sys
import time
import urllib
import uuid

def api_request(url, api_key, api_secret, org_id, body=None):
    time_ms = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    parts = urllib.parse.urlparse(url)

    input = f"{api_key}\0{time_ms}\0{nonce}\0\0{org_id}\0\0GET\0{parts.path}\0{parts.query}"
    if body != None:
        input += f"\0{body}"
    signature = hmac.new(api_secret.encode(), msg=input.encode(), digestmod=hashlib.sha256).hexdigest()
    auth = f"{api_key}:{signature}"

    return requests.get(
        url,
        headers={
            "X-Time": time_ms,
            "X-Nonce": nonce,
            "X-Request-Id": request_id,
            "X-Organization-Id": org_id,
            "X-Auth": auth,
            "Content-Type": "application/json",
        }
    )

def main():
    try:
        worker = sys.argv[1]
        api_key = sys.argv[2]
        api_secret = sys.argv[3]
        org_id = sys.argv[4]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <worker> <api_key> <api_secret> <org_id>")

    print("proxy_api_pool enabled=1i")
    response = api_request(
        "https://api2.nicehash.com/main/api/v2/mining/rigs2/",
        api_key, api_secret, org_id
    )
    if response:
        name = worker.split(".")[1]
        j = json.loads(response.text)["miningRigs"]
        for w in j:
            if w["name"] == name and "stats" in w:
                earnings = float(w["unpaidAmount"])
                profit = float(w["profitability"])
                speed = int(float(w["stats"][0]["speedAccepted"]) * 10 ** 12)
                print(f"proxy_api_worker speed={speed}i")
                print(f"proxy_api_worker earnings={earnings:.18f}")
                print(f"proxy_api_pool profit={profit:.18f}")

main()
