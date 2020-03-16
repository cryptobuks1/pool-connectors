<?php

namespace MiningMeter\Connectors\F2Pool;

use App\Connectors\Connector;
use Carbon\Carbon;
use GuzzleHttp\Client;
use GuzzleHttp\Cookie\SetCookie as CookieParser;

class WebParser extends Connector
{
    const ERROR_COOKIE_EXPIRED = 1;
    const ERROR_NO_COOKIE= 2;
    const ERROR_NO_USER = 2;
    const HASHRATE_SUPPORT = true;

    protected $_data;

    public function getData($options = [])
    {
        $cache = $options['cache'] ?? true;

        if ($cache && $this->_data) {
            return $this->_data;
        }

        $credentials = $this->_credentials;
        $cookie = $credentials->cookie;
        $user = $credentials->user;

        if (empty($cookie)) {
            throw new \Exception(
                "F2Pool cookie required",
                static::ERROR_NO_COOKIE
            );
        }

        if (empty($user)) {
            throw new \Exception(
                "F2Pool user required",
                static::ERROR_NO_USER
            );
        }

        $url = 'https://www.f2pool.com/user/history?action=load_payout_history&currency=bitcoin&account='.$user;
        $client = new Client;
        $response = $client->request('GET', $url, [
            'headers' => [
                'Accept' => 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With' => 'XMLHttpRequest',
                'Cookie' => $cookie
            ]
        ]);
        $data = $response->getBody()->getContents();
        $headers = $response->getHeaders();

        if (!empty($headers['Set-Cookie'])) {
            $cookies = implode(';', $headers['Set-Cookie']);
            $this->updateCookie($cookies);
        }

        $parsed = json_decode($data);
        $success = $data && is_object($parsed) && $parsed->status === 'ok';

        if (!$success) {
            throw new \Exception(
                "F2Pool cookie expired",
                static::ERROR_COOKIE_EXPIRED
            );
        }

        $rows = collect(
            $parsed->data
        );

        $rows = $rows->groupBy(function($row) {
            return (int) $row->created_at;
        })
            ->map(function ($items) {
                $item = $items->first();

                $items->each(function($row) use ($item) {
                    if ($row->salary) {
                        $item->salary_amount = $row->amount;
                    }

                    if ($row->tx_fee) {
                        $item->fee_amount = $row->amount;
                    }
                });

                $date = Carbon::createFromTimestamp($item->created_at);
                $date = $date->subDay();
                $earnings = $item->salary_amount + $item->fee_amount;
                $earnings = $earnings * 10e7;
                $hashrate = str_replace(' Thash/s', '', $item->hash_rate);
                if (!$hashrate) {
                    return;
                }
                $profit = $earnings / $hashrate;

                return [
                    'hashrate' => $hashrate,
                    'earnings' => $earnings,
                    'profit' => $profit,
                    'date' => $date
                ];
            })
            ->filter(function($item) {
                return !empty($item);
            });

        return $this->_data = $rows;
    }

    protected function updateCookie($newCookiesData)
    {
        $credentials = $this->_credentials;
        $oldCookieData = $credentials->cookie;
        $fromPairs = function ($data, $entry) {
            $entry = trim($entry);
            $row = explode('=',$entry);
            if (count($row) < 2) {
                return $data;
            }
            list($key, $value) = $row;
            $data[$key] = $value;
            return $data;
        };

        $oldCookies = array_reduce(
            explode(';', $oldCookieData),
            $fromPairs,
            []
        );
        $newCookies = array_reduce(
            explode(';', $newCookiesData),
            $fromPairs,
            []
        );

        $cookie = array_replace_recursive($oldCookies, $newCookies);
        $toPairs = function ($key, $value) {
            return "$key=$value";
        };
        $cookieData = implode('; ', array_map(
                $toPairs, array_keys($cookie), $cookie
            )
        );

        $credentialsValue = $credentials->getCredentialsValue('cookie');
        if (!$credentialsValue->exists) {
            return;
        }
        $credentialsValue->value = $cookieData;
        $credentialsValue->save();
    }

    public function getPaymentHistory()
    {
        $rows = $this->getData()
            ->map(function ($item) {
                return [
                    'value' => $item['earnings'],
                    'date' => $item['date'],
                    'item' => $item
                ];
            });

        return $rows;
    }
    public function getProfit()
    {
        $rows = $this->getData()->map(function ($item) {
            return [
                'value' => $item['profit'],
                'hashrate' => $item['hashrate'],
                'earnings' => $item['earnings'],
                'date' => $item['date']
            ];
        });

        return $rows;
    }
}
