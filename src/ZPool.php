<?php

namespace MiningMeter\Connectors;

use GuzzleHttp\Client;
use MiningMeter\Connectors\Connector;
use Carbon\Carbon;

class ZPool extends Connector
{
    const BASE_URL = "https://www.zpool.ca";
    const PAYMENT_HISTORY_SUPPORT = false;

    public function getBalance()
    {
        $address = $this->_credentials->wallet_address;
        $url = "/api/walletEX?address={$address}";

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $response = $client->get($url)
            ->getBody()
            ->getContents();

        $data = json_decode($response);

        return $data->total;
    }

    public function getPaymentHistory()
    {
        $address = $this->_credentials->wallet_address;
        $url = "/api/walletEX?address={$address}";

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $response = $client->get($url)
            ->getBody()
            ->getContents();

        $data = json_decode($response);

        $date = Carbon::now()->startOfDay();

        return collect([
            [
                'date' => $date,
                'value' => $data->paid24h
            ]
        ]);
    }


}
