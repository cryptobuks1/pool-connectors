<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use Illuminate\Support\Collection;

class Poolin extends Connector
{
    const BASE_URL = 'https://api-prod.poolin.com/api/public';
    const HASHRATE_SUPPORT = true;

    public function request($method, $path, $params = [])
    {
        $credentials = $this->_credentials;
        $puid = $credentials->puid;
        $read_token = $credentials->read_token;
        if (empty($puid)) {
            throw new \Error('PUID cannot be empty!');
        }
        if (empty($read_token)) {
            throw new \Error('Read token cannot be empty!');
        }
        $token = "Bearer {$read_token}";
        $curl = curl_init();

        $params = array_merge_recursive($params, [
            'puid' => $puid,
        ]);

        $url = static::BASE_URL . $path . '?' . http_build_query($params);

        curl_setopt_array($curl, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => [
                "Authorization: $token",
            ],
        ]);

        $raw = curl_exec($curl);

        $response = json_decode($raw);

        if (!$response) {
            throw new \Error('Response is null in raw ' .$raw);
        }

        if (!property_exists($response, 'data')) {
            throw new \Error('Response have not data field in raw ' .$raw);
        }

        return $response->data;
    }

    public function getProfit($options = []): Collection
    {
        /** @var Collection $data */
        $data = $this->getPaymentHistory($options)->data;

        return $data->map(function ($item) {
            $hashrate = $item->share_accept;
            $revenue = $item->amount;
            $value = $revenue / ($hashrate * 100000);
            return [
                'hashrate' => $hashrate,
                'revenue' => $revenue,
                'date' => $item->date,
                'value' => $value
            ];
        });
    }

    public function getWorkers($options = [])
    {
        $params = array_merge_recursive(
            [
                'coin_type' => 'btc',
                'status' => 'ALL',
                'pagesize' => 200,
                'page' => 1
            ],
            $options
        );

        $response = $this->request(
            'GET',
            '/v2/worker',
            $params
        );

        return $response;
    }

    public function getPaymentHistory($options = [])
    {
        $params = array_merge_recursive(
            [
                'coin_type' => 'btc',
                'page' => 1
            ],
            $options
        );

        $response = $this->request(
            'GET',
            '/v2/payment/history',
            $params
        );

        $data = collect($response->data)
            ->map(function($item) {
                /* @var Carbon $date */
                $date = Carbon::createFromFormat('Ymd', $item->date);
                $date = $date->startOfDay();
                $item->date = $date;
                $value = $item->amount;
                return [
                    'date' => $date,
                    'value' => $value,
                    'item' => $item
                ];
            });

        return $data;
    }
}
