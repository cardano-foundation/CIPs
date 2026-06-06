<?php

$argc = count($argv);

if ($argc == 3) {
  $new_fixed = $argv[1];
  $new_rate = $argv[2];
  $pledge = 100000;
} else if ($argc == 4) {
  $new_fixed = $argv[1];
  $new_rate = $argv[2];
  $pledge = $argv[3];
} else {
  echo "Usage: php " . $argv[0] . " <min_fixed_fee> <min_rate_fee> <pledge>" . PHP_EOL;
  echo "  min_fixed_fee:  Minimum fixed fee in ADA." . PHP_EOL;
  echo "               An integer greater than or equal to 0." . PHP_EOL;
  echo "  min_rate_fee: Minimum rate fee in decimal. Example: 1.5% = .015" . PHP_EOL;
  echo "                    A real number greater than or equal to 0." . PHP_EOL;
  echo "  pledge: Optional pledge amount in ADA. Defaults to 100000" . PHP_EOL;
  echo "                    A real number greater than or equal to 0." . PHP_EOL;
  exit;
}

if ($pledge < 1000000) {
  $pledge_str = round($pledge / 1000, 1) . "k";
} else {
  $pledge_str = round($pledge / 1000000, 1) . "m";
}

// Protocol parameters
$k = 500;
$rho = 0.003;
$a0 = 0.3;
$tau = .2;

// Assumptions
$current_fixed = 170;
$current_rate = 0.0;
$reserve = 1690000000;
$total_stake = 37000000000;
$fees = 32000;
$staker = 100000;

if ($staker < 1000000) {
  $staker_str = round($staker / 1000, 1) . "k";
} else {
  $staker_str = round($staker / 1000000, 1) . "m";
}

// Calculated values
$R = (($reserve * $rho) + $fees) * (1 - $tau);
$z0 = 1 / $k;
$saturation = $total_stake / $k;
$half_saturation = $saturation / 2;
$ds = array(2000000, 5000000, 10000000, 20000000, $half_saturation, $saturation);
$os = array();

foreach ($ds as $d) {
  $os[] = $d / $total_stake;
}

echo "Reserve: " . round($reserve / 1000000000, 1) . "b" . PHP_EOL;
echo "Total stake: " . round($total_stake / 1000000000, 1) . "b" . PHP_EOL;
echo "Tx fees: " . $fees . PHP_EOL;
echo "Rewards available in epoch: " . round($R / 1000000, 1) . "m" . PHP_EOL;
echo "Pool saturation: " . round($saturation / 1000000, 1) . "m" . PHP_EOL;
echo "Pledge: " . $pledge_str . PHP_EOL;
echo "Staker Delegation: " . $staker_str . PHP_EOL;
echo "Current Fixed Fee: " . $current_fixed . PHP_EOL;
echo "Current Rate: " . round($current_rate * 100, 1) . '%' . PHP_EOL;
echo "New Fixed Fee: " . $new_fixed . PHP_EOL;
echo "New Rate: " . round($new_rate * 100, 1) . '%' . PHP_EOL;
echo PHP_EOL;

echo "\t\t/---------- Current ----------\\ /-------- Proposed ---------\\" . PHP_EOL;
echo "Pool\tTotal\tPool\tStaker\tStaker\tCurrent\tPool\tStaker\tStaker\tNew" . PHP_EOL;
echo "Stake\tRewards\tFee\tFee\tRew\tFee %\tFee\tFee\tRew\tFee %" . PHP_EOL;
echo "---------------------------------------------------------------------" . PHP_EOL;

$i = 0;

foreach ($os as $o) {
  // Rewards Formula
  $s = $pledge / $total_stake;
  $rewards = round(($R / (1 + $a0)) * ($o + ($s * $a0 * (($o - ($s * (($z0 - $o) / $z0))) / $z0))));
  $current_rate_basis = $rewards - $current_fixed;
  $current_rate_fee = $current_rate_basis * $current_rate;
  $current_fees = $current_fixed + $current_rate_fee;

  if ($current_fees > $rewards) {
    $current_fees = $rewards;
  }

  $current_fee_per_staker = $current_fees * ($staker / $ds[$i]);
  $current_reward_per_staker = ($rewards - $current_fees) * ($staker / $ds[$i]);
  $current_fee_percent = round(($current_fees / $rewards) * 100, 1);
  $new_rate_basis = $rewards - $new_fixed;
  $new_rate_fee = $new_rate_basis * $new_rate;
  $new_fees = $new_fixed + $new_rate_fee;
  $new_fee_per_staker = $new_fees * ($staker / $ds[$i]);
  $new_reward_per_staker = ($rewards - $new_fees) * ($staker / $ds[$i]);
  $new_fee_percent = round(($new_fees / $rewards) * 100, 1);
  $d_str = round($ds[$i] / 1000000, 1) . 'm';

  echo $d_str . "\t" . $rewards . "\t" . round($current_fees, 1) . "\t" . round($current_fee_per_staker, 1) . "\t" . round($current_reward_per_staker, 1) . "\t" . $current_fee_percent . "%\t" . round($new_fees, 1) . "\t" . round($new_fee_per_staker, 1) . "\t" . round($new_reward_per_staker, 1) . "\t" . $new_fee_percent . '%' . PHP_EOL;
  $i++;
}

echo PHP_EOL;

