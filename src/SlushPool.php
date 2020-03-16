<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;
use Illuminate\Support\Collection;

class SlushPool extends Connector
{
    const BASE_URL = 'https://slushpool.com/';

    public function request($path, $params=[])
    {
        $credentias = $this->_credentials;
        $token = $credentias->access_token;

        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $response = $client->post($path, [
            'headers' => [
                'SlushPool-Auth-Token' => $token,
                'X-SlushPool-Auth-Token' => $token,
            ],
            'query' => $params
        ]);

        $data = $response->getBody()->getContents();
        return json_decode($data);
    }

    public function getPaymentHistory()
    {
        $response = $this->request('stats/json/btc');

        $blocks = collect($response->btc->blocks)->values();

        $data = $blocks
            ->filter(function ($block) {
                return $block->state === 'confirmed';
            })
            ->map(function($block) {
                $date = Carbon::createFromTimestamp($block->date_found);
                $value = $block->user_reward * 10e7;
                return [
                    'date' => $date,
                    'item' => $block,
                    'value' => $value
                ];
            });

        return $data;
    }
}
