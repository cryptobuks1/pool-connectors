<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;
use Ramsey\Uuid\Uuid;

class Nicehash extends Connector
{
    const BASE_URL = "https://api2.nicehash.com";
    const HASHRATE_SUPPORT = true;

    public function request($method, $path, $query=[], $body=[])
    {
        $method = strtoupper($method);
        $credentials = $this->_credentials;
        $key = $credentials->api_key;
        $secret = $credentials->secret_key;
        $organizationId = $credentials->organization_id;

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $time = (int) microtime(true) * 1000;
        $nonce = Uuid::uuid1()->toString();
        $requestId = Uuid::uuid4()->toString();

        $input = [
            $key,
            $time,
            $nonce,
            '',
            $organizationId,
            '',
            $method,
            $path,
        ];

        if (!empty($query)) {
            $input[] = http_build_query($query);
        }
        if (!empty($body)) {
            $input[] = json_encode($body);
        }

        $input = implode("\x00",$input);
        $sign = hash_hmac('sha256', $input, $secret, false);
        $auth = $key.':'.$sign;

        $requestParams = [
            'headers' => [
                'X-Time' => $time,
                'X-Nonce' => $nonce,
                'X-Request-Id' => $requestId,
                'X-Auth' => $auth,
                'Content-Type' => 'application/json'
            ]
        ];

        if (!empty($organizationId)) {
            $requestParams['headers']['X-Organization-Id'] = $organizationId;
        }

        if (!empty($body)) {
            $requestParams['form_params'] = $query;
        }

        if (!empty($query)) {
            $requestParams['query'] = $query;
        }

        $response = $client->request($method, $path, $requestParams);

        return $response;
    }

    public function getPaymentHistory()
    {
        $path = "/main/api/v2/mining/rigs/payouts/";

        $response = $this->request('GET', $path, [
            'timestamp' => Carbon::now()->timestamp,
            'page' => 0,
            'size' => 100
        ]);

        $data = json_decode(
            $response->getBody()
        );
        $data = collect($data->list);

        $data = $data
            ->map(function ($item) {
                $date = Carbon::createFromTimestampMs($item->created);

                $value = $item->amount * 10e7;
                return [
                    'date' => $date,
                    'value' => $value,
                    'item' => $item
                ];
            });

        return $data;
    }
}
