# Mining Pool connectors
## Connectors
The connectors that are in the `scripts` folder are designed to work with the [`Telegraf`](https://github.com/influxdata/telegraf) monitoring agent and are used to extract data from the `API` pools. To run the connectors, `Python 3` is required with a basic set of libraries. All connectors retrieve 3 groups of data.
* `hashrate` - the current hashrate. Since all pools approximate the hashrate at different intervals and with different latencies, it was decided not to bother with rationing, but simply to collect as is. Hash rate normalized to `H/s`.
* `earnings` - earnings for mining. Charges are normalized to `BTC`. Their current value is taken. Calculation of the delta for the period monitoring system is making.
* `profit` - the value of `Th/s/day` profitability by the pool. Normalized to `BTC`. It is taken from the public `API` of the pool - if one is provided, usually from a calculator or statistics.
The output is transmitted in `InfluxDB` format. If any data cannot be received, it is not returned. To increase the speed of operation, requests to the `API` are parallelized. Request speed is controlled by `Telegraf`.

## Connecting connectors to Telegraf
Connectors are connected to `Telegraf` using the [`exec`](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec) plugin and the configuration file in `telegraf.d`.
```ini
[[inputs.exec]]
commands = [
	"/etc/telegraf/scripts/pools-api-antpool-com.py {{ worker_antpool_com_worker }} {{ worker_antpool_com_api_key }} {{ worker_antpool_com_api_secret }}"
]
timeout = "20s"
data_format = "influx"
```
It is not recommended to request data from pools more than once every 30 seconds, because you can get access to the `API` for a certain time.

Known problems:
* Nicehash parser return pool profitability as zero.
* Earnings return in BTC. In the future, the result will be returned in satoshi.
