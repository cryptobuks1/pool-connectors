<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;

class EMCD extends Connector
{
    const BASE_URL = 'https://api.emcd.io';

    public function request($path, $params=[])
    {
        $credentias = $this->_credentials;
        $key = $credentias->api_key;

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $response = $client->get($path.'/'.$key, [
            'json' => $params
        ]);

        $data = $response->getBody()->getContents();

        return json_decode($data);
    }

    public function getPaymentHistory()
    {
        $response = $this->request('/v1/btc/income');
        $income = collect($response->income);

        $data = $income
            ->map(function($item) {
                $date = Carbon::createFromTimestamp($item->timestamp);
                $value = $item->income * 10e7;
                return [
                    'date' => $date,
                    'value' => $value
                ];
            });

        return $data;
    }
}
