<?php

namespace MiningMeter\Connectors\F2Pool;

use App\Connectors\Connector;
use Carbon\Carbon;
use GuzzleHttp\Client;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache;

class API extends Connector
{
    const BASE_URL = 'https://api.f2pool.com';
    public const HASHRATE_SUPPORT = true;

    public function getProfit()
    {
        $hashrates = $this->updateCache('hashrate.daily',
            $this->fetchDailyHashrate()
        );
        sleep(1);
        $payouts = $this->updateCache('payouts',
            $this->fetchPayoutHistory()
        );
        sleep(1);
        $this->updateCache('hashrate',
            $this->fetchHashrate()
        );

//        $hashrates->dump();

        $profits = $payouts->map(function ($payout) use ($hashrates) {
                /** @var Carbon $date */
                $date = $payout['date'];
                $hashrate = $hashrates->filter(function($hashrate) use ($date) {
                    return $date->eq($hashrate['date']);
                })->first();

                if (empty($hashrate['value'])) {
                    return;
                }

                $value = $payout['value'] * 1E3 / $hashrate['value'];
                return [
                    'date' => $date,
                    'value' => $value
                ];
            })
            ->filter(function ($item) {
                return !empty($item);
            });

        return $profits;
    }

    public function updateCache($key, Collection $values)
    {
        $cached = $this->getCache($key);

        $add = $values->filter(function ($item) use ($cached) {
                $found = $cached->where('date', '=', $item['date']);
                $exists = $found->count() !== 0;
                return !$exists;
            })
            ->values();

        $merged = $cached->merge($add);
        $this->setCache($key, $merged);

        return $merged;

    }

    public function getCacheKey($key)
    {
        $user = $this->_credentials->user;
        return "data-instance.f2pool.$user.$key";
    }


    public function getCache($key)
    {
        $cacheKey = $this->getCacheKey($key);

        $cachedValue = Cache::get($cacheKey);
        $cachedValue = $cachedValue ? json_decode($cachedValue, true) : [];

        return collect($cachedValue)
            ->map(function ($item) {
                $timestamp = $item['timestamp'];
                $date = Carbon::createFromTimestamp($timestamp);
                $item['date'] = $date;
                return $item;
            });
    }

    public function setCache($key, Collection $value)
    {
        $cacheKey = $this->getCacheKey($key);
        $data = $value->map(function ($item) {
                /** @var Carbon $date */
                $date = $item['date'];
                $timestamp = $date->timestamp;
                $item['timestamp'] = $timestamp;
                return $item;
            })
            ->values()
            ->toJson();

        Cache::forever($cacheKey, $data);
    }

    public function fetchUserData()
    {
        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $credentials = $this->_credentials;
        $user = $credentials->user;
        $path = "/bitcoin/{$user}";
        $response = $client->request('GET', $path)
            ->getBody();

        return json_decode($response);
    }

    public function fetchPayoutHistory()
    {
        $data = $this->fetchUserData();

        $history = collect($data->payout_history)
            ->map(function ($item) {
                list($timestamp, $hash, $value) = $item;

                $date = Carbon::createFromFormat('Y-m-d\TH:i:s\Z', $timestamp);
                return [
                    'date' => $date,
                    'value' => $value
                ];
            });


        return $history;
    }

    public function fetchHashrate()
    {
        $data = $this->fetchUserData();

        return collect([
           [
               'date' => now(),
               'last_hour' => $data->hashes_last_hour,
               'last_day' => $data->hashes_last_day,
               'current' => $data->hashrate,
           ]
        ]);
    }

    public function fetchDailyHashrate()
    {
        $client = new Client([
            'base_uri' => static::BASE_URL
        ]);

        $credentials = $this->_credentials;
        $user = $credentials->user;
        $worker = $credentials->worker;
        $path = "/bitcoin/{$user}/{$worker}";

        $response = $client->request('GET', $path)
            ->getBody();

        $data = json_decode($response);

        $hashrates = collect($data->hashrate_history)
            ->map(function($value, $key) {
                $hashrate = $value / 1E12;
                return [
                    'value'	=> $hashrate,
                    'date' => Carbon::createFromFormat('Y-m-d\TH:i:s\Z', $key)
                ];
            })
            ->filter(function ($item) {
                return !empty($item['value']);
            })
            ->values()
            ->sort(function($a, $b) {
                /** @var Carbon $dateA */
                $dateA = $a['date'];
                /** @var Carbon $dateB */
                $dateB = $b['date'];
                return $dateA->lessThan($dateB) ? -1 : 1;
            });

        return $hashrates;
    }
}
