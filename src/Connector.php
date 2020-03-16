<?php

namespace MiningMeter\Connectors;

use Carbon\Carbon;
use Illuminate\Support\Collection;

abstract class Connector
{
    const HASHRATE_SUPPORT = false;
    const PAYMENT_HISTORY_SUPPORT = true;
    const CALCULATION_TIMEZONE_OFFSET = 0;

    protected $_credentials;

    public function __construct($credentials)
    {
        $this->_credentials = $credentials;
    }

    public static function groupByDate(Collection $data)
    {
        return $data
            ->groupBy(function($item) {
                /** @var Carbon $date */
                $date = $item['date'];
                return $date->clone()->startOfDay()->timestamp;
            })
            ->map(function (Collection $group, $timestamp) {
                $date = Carbon::createFromTimestamp($timestamp);
                $value = $group->sum('value');

                return [
                    'date' => $date,
                    'value' => $value,
                    'items' => $group
                ];
            });
    }

    public function getPaymentHistory()
    {
        return collect([]);
    }

    public function getHashrates()
    {
        return collect([]);
    }

    public function getBalance()
    {
        return 0;
    }

    public function getProfit()
    {
        $paymentHistory = static::groupByDate(
            $this->getPaymentHistory()
        );
        $hashrates = static::groupByDate(
            $this->getHashrates()
        );

        $profit = $paymentHistory
            ->map(function($item) use ($hashrates) {
                $date = $item->date;
                $hashrate = $hashrates
                    ->filter(function($item) use ($date) {
                        return $date->equalTo($item->date);
                    })
                    ->first();

                if (!$hashrate) {
                    return null;
                }
                $hashrate = $hashrate->value;
                $earnings = $item->value;
                $value = $earnings / ($hashrate * 100000);
                return [
                    'revenue' => $earnings,
                    'hashrate' => $hashrate,
                    'date' => $date,
                    'value' => $value
                ];
            })
            ->filter();

        return $profit;
    }
}
