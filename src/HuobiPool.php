<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;
use Illuminate\Support\Collection;

class HuobiPool extends Connector
{
    const BASE_URL = 'https://openapi.hpt.com';
    const HASHRATE_SUPPORT = true;

    public function request($path, $params = [])
    {
        $credentials = $this->_credentials;
        $subCode = $credentials->sub_code;
        $secretKey = $credentials->secret_key;
        $timestamp = (int)(microtime(true) * 1000);

        $query = array_merge_recursive(
            $params,
            [
                'sub_code_list' => $subCode,
                'secret_key' => $secretKey,
                'timestamp' => $timestamp
            ]
        );

        $queryData = http_build_query($query);
        $sign = hash('sha256', $queryData);

        $query['sign'] = $sign;

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $response = $client->get($path, [
            'query' => $query
        ]);

        return $response;
    }

    public function getYesterdayProfit(): Collection
    {
        $response = $this->request('/open/api/user/v1/list-hourly', [
            'coin_name' => 'btc'
        ])
            ->getBody();

        $data = collect(
            json_decode($response)->data
        );

        return $data->filter(function ($item) {
                return strtolower($item->currency) === 'btc';
            })
            ->map(function ($item) {
                $item->date = Carbon::yesterday()->startOfDay();
                return $item;
            });
    }

    public function getTodayProfit(): Collection
    {
        $response = $this->request('/open/api/user/v1/list-hourly', [
            'coin_name' => 'btc'
        ])
            ->getBody();

        $data = json_decode($response)->data;

        if (!is_array($data)) {
            $data = [$data];
        }

        $data = collect($data);

        return $data->filter(function ($item) {
            return strtolower($item->currency) === 'btc';
        })
            ->map(function ($item) {
                $item->date = Carbon::today()->startOfDay();
                return $item;
            });
    }

    public function getPaymentHistory()
    {
        $yesterday = $this->getYesterdayProfit();
        $today = $this->getTodayProfit();
        $data = $yesterday->concat($today);

        return $data->map(function ($item) {
            return (object)[
                'date' => $item->date,
                'value' => $item->amount
            ];
        });
    }

    public function getHashrates()
    {
        $response = $this->request('/open/api/user/v1/list-hourly', [
                'coin_name' => 'btc'
            ])
            ->getBody();

        $data = collect(
            json_decode($response)->data
        );

        return $data->map(function($item) {
            $date = Carbon::createFromTimestamp($item->date);
            return (object) [
                'value' => $item->speed,
                'date' => $date
            ];
        });
    }
}
