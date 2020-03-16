<?php

namespace MiningMeter\Connectors;

use GuzzleHttp\Client;
use MiningMeter\Connectors\Connector;
use Carbon\Carbon;

class ViaBTC extends Connector
{
    const BASE_URL = "https://www.viabtc.com";
    const HASHRATE_SUPPORT = true;
    public const CALCULATION_TIMEZONE_OFFSET = 8 * 60;

    public function request($path, $params = [])
    {
        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);
        $credentials = $this->_credentials;
        $key = $credentials->api_key;

        $response = $client->get($path, [
            'query' => $params,
            'headers' => [
                'X-API-KEY' => $key,
            ]
        ]);

        return $response;
    }

    public function getPaymentHistory()
    {
        $response = $this->request('/res/openapi/v1/profit/history', [
            'coin' => 'btc',
            'utc' => 'true'
        ])
            ->getBody()
            ->getContents();

        $response = json_decode($response);
        $data = $response->data;

        if (!property_exists($data, 'data')) {
            throw new \Exception($response->message);
        }

        $data = collect(
            $data->data
        );

        $data = $data->map(function ($item) {
            $date = Carbon::parse($item->date)->startOfDay();
            $value = $item->pps_profit * 10e7;
            return [
                'date' => $date,
                'value' => $value,
                'item' => $item
            ];
        });

        return $data;
    }

    public function getHashrates()
    {
        $credentials = $this->_credentials;
        $worker_id = $credentials->worker_id;

        $url = "/res/openapi/v1/hashrate/worker/{$worker_id}/history";
        $response = $this->request($url, [
            'coin' => 'btc',
            'utc' => 'true'
        ])
            ->getBody()
            ->getContents();

        $response = json_decode($response);
        $data = $response->data;

        if (!property_exists($data, 'data')) {
            throw new \Exception($response->message);
        }
        $data = collect(
            $data->data
        );

        return $data->map(function ($item) {
            $date = Carbon::parse($item->date);
            $hashrate = $item->hashrate / 10E11;
            return [
                'date' => $date,
                'value' => $hashrate,
                'item' => $item,
            ];
        });
    }
}
