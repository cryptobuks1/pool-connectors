<?php

namespace MiningMeter\Connectors;

use GuzzleHttp\Client;
use Carbon\Carbon;

class SigmaPool extends Connector
{
    const BASE_URL = "https://sigmapool.com";
    const HASHRATE_SUPPORT = true;

    public function request($path, $params=[])
    {
        $key = $this->_credentials->api_key;

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $params['key'] = $key;

        $response = $client->get($path, [
            'query' => $params
        ]);

        return $response;
    }

    public function getPaymentHistory()
    {
        $response = $this->request('/api/v1/btc/dailyearnings', [
            'limit' => 25,
            'page' => 1
        ])
            ->getBody()
            ->getContents();

        $data = collect(
            json_decode($response)
        );

        return $data->map(function($item) {
            $date = Carbon::createFromTimestampMs($item->date);
            $value = $item->earnings * 10e7;
            return [
                'date' => $date,
                'value' => $value,
                'item' => $item
            ];
        });
    }

    public function getProfit()
    {
        $response = $this->request('/api/v1/btc/dailyearnings', [
            'limit' => 25,
            'page' => 1
        ])
            ->getBody()
            ->getContents();

        $data = collect(
            json_encode($response)
        );

        return collect([]);
    }
}
