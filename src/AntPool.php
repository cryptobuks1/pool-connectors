<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;

class AntPool extends Connector
{
    const BASE_URL = 'https://antpool.com';
    const HASHRATE_SUPPORT = true;

    public function getAuthParams()
    {
        $credentials = $this->_credentials;
        $nonce = time();
        $key = $credentials->api_key;
        $secret = $credentials->api_secret;
        $username = $credentials->username;

        $data = [
            'key' => $key,
            'nonce' => time(),
        ];

        $dataString = $username.$key.$nonce;

        $signature = strtoupper(
            hash_hmac('sha256', $dataString, $secret, false)
        );

        $data['signature'] = $signature;
        return $data;
    }

    public function request($path, $params = [])
    {
        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $formParams = array_merge_recursive(
            $params,
            $this->getAuthParams()
        );

        $response = $client->post($path, [
            'form_params' => $formParams
        ]);

        return $response;
    }

    public function getPaymentHistory()
    {
        $data = $this->request('/api/account.htm', [
            'type' => 'pps',
        ]);

        $contents = $data->getBody()->getContents();
        $data = json_decode($contents)->data;

        $date = Carbon::now()->startOfDay();

        $value = $data->earn24Hours * 10e7;
        return collect([
            [
                'date' => $date,
                'value' => $value
            ]
        ]);
    }

    public function getHashrates()
    {
        $credentials = $this->_credentials;
        $worker = $credentials->worker;

        $data = $this->request('/api/workers.htm');
        $data = json_decode($data->getBody())->data->rows;

        $workerData = collect($data)->firstWhere('workers.htm', $worker);
        $hashrate = $workerData->last1d / 10E5;

        return collect([
           [
               'date' => Carbon::now(),
               'value' => $hashrate
           ]
        ]);
    }
}
