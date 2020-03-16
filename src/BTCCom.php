<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use GuzzleHttp\Client;
use Illuminate\Support\Collection;

class BTCCom extends Connector
{
    const BASE_URL = 'https://pool.api.btc.com/v1';
    const HASHRATE_SUPPORT = true;

    public function getAuthParams()
    {
        $credentials = $this->_credentials;
        return [
            'access_key' => $credentials->access_key,
            'puid' => $credentials->puid,
        ];
    }

    public function getUrl($path, $params = [])
    {
        $params = http_build_query(
            array_merge_recursive(
                $params,
                $this->getAuthParams()
            )
        );
        $url = static::BASE_URL . $path . '?' . $params;
        return $url;
    }

    public function getHashrates($options = []): Collection
    {
        $client = new Client;
        $startDate = Carbon::now()->subYear();

        $path = '/worker/share-history';
        $url = $this->getUrl($path, [
            'dimension' => '1d',
            'start_ts' => $startDate->timestamp,
            'count' => 720
        ]);

        $response = $client->request('GET', $url)
            ->getBody();

        $response = json_decode($response);

        $data = collect($response->data->tickers)
            ->map(function ($item) {
                $timestamp = $item[0];
                $date = Carbon::createFromTimestamp($timestamp)->startOfDay();

                return [
                    'date' => $date,
                    'value' => $item[1],
                    'reject_percent' => $item[2],
                ];
            });

        return $data;
    }

    public function getProfit($options = []): Collection
    {
        $earnHistoryOptions = $options['earnHistory'] ?? [];
        $hashratesOptions = $options['hashrates'] ?? [];
        $earnHistory = $this->getPaymentHistory($earnHistoryOptions);
        $hashrates = $this->getHashrates($hashratesOptions);

        $profit = $earnHistory
            ->map(function($item) use ($hashrates) {
                $date = $item['date'];
                $hashrate = $hashrates
                    ->filter(function($item) use ($date) {
                        return $date->equalTo($item['date']);
                    })
                    ->first();

                if (!$hashrate) {
                    return null;
                }
                $hashrate = $hashrate['value'];
                $earnings = $item['earnings'];
                $value = $earnings * 1e-6 / $hashrate;

                return [
                    'earnings' => $earnings,
                    'hashrate' => $hashrate,
                    'date' => $date,
                    'value' => $value
                ];
            })
            ->filter();

        return $profit;
    }

    public function getPaymentHistory($options = [])
    {
        $page = $options['page'] ?? 1;
        $pageSize = $options['page_size'] ?? 10;
        $client = new Client;
        $url = static::getUrl('/account/earn-history', [
            'page' => $page,
            'page_size' => $pageSize
        ]);

        $response = $client->request('GET', $url)
            ->getBody();

        $response = json_decode($response);
        $data = $response->data;
        $data = collect($data->list)
            ->map(function($item) {
                /** @var Carbon $date */
                $date = Carbon::createFromFormat('Ymd', $item->date);
                return [
                    'value' => $item->earnings,
                    'date' => $date,
                    'item' => $item
                ];
            });

        return $data;
    }
}
