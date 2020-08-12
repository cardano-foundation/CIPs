<?php

$argc = count($argv);

if ($argc == 1) {
  // The n-root curve exponent. 1 = linear, 2 = square root, 3 = cube root, 4 = fourth root, etc.
  $curve_roots = array(2, 3, 4);

  // Divisor of saturation that calculates the pledge where the curve crosses the line
  $crossover_factors = array(10, 20, 50);
} else if ($argc == 3) {
  $curve_roots = array($argv[1]);
  $crossover_factors = array($argv[2]);
} else {
  echo "Usage: php -f " . $argv[0] . " <curve_root> <crossover_factor>" . PHP_EOL;
  echo "  curve_root:  The n-root curve exponent. 1 = linear, 2 = square root, 3 = cube root, etc." . PHP_EOL;
  echo "               An integer greater than 0." . PHP_EOL;
  echo "  crossover_factor: Divisor of saturation that calculates the pledge where the curve crosses the line." . PHP_EOL;
  echo "                    A real number greater than or equal to 1." . PHP_EOL;
  exit;
}

// Assumptions
$reserve = 14000000000;
$total_stake = 31700000000;
$fees = 0;

echo "Assumptions" . PHP_EOL;
echo "Reserve: " . round($reserve / 1000000000, 1) . "b" . PHP_EOL;
echo "Total stake: " . round($total_stake / 1000000000, 1) . "b" . PHP_EOL;
echo "Tx fees: " . $fees . PHP_EOL;
echo "Fully Saturated Pool" . PHP_EOL;

// Protocol parameters
$k = 150;
$rho = 0.0022;
$a0 = 0.3;
$tau = .05;

// Calculated values
$R = (($reserve * $rho) + $fees) * (1 - $tau);
$z0 = 1 / $k;
$o = $z0; // for fully saturated pool
$saturation = round($total_stake / $k);

echo "Rewards available in epoch: " . round($R / 1000000, 1) . "m" . PHP_EOL;
echo "Pool saturation: " . round($saturation / 1000000, 1) . "m" . PHP_EOL;
echo PHP_EOL;

// Pool pledge
$pledges = array(0, 10000, 50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 20000000, 50000000, 100000000, $saturation);

// Compare to zero pledge
$comparison_pledge = 0;
$comparison_s = $comparison_pledge / $total_stake;
$comparison_rewards = round(($R / (1 + $a0)) * ($o + ($comparison_s * $a0 * (($o - ($comparison_s * (($z0 - $o) / $z0))) / $z0))));

foreach ($curve_roots as $curve_root) {
  foreach ($crossover_factors as $crossover_factor) {
    $crossover = $total_stake / ($k * $crossover_factor);
    echo "Curve root: " . $curve_root . PHP_EOL;
    echo "Crossover factor: " . $crossover_factor . PHP_EOL;
    echo "Crossover: " . round($crossover / 1000000, 1) . "m" . PHP_EOL;
    echo PHP_EOL;

    echo "Pledge\tRewards\tBenefit\tAlt Rwd\tAlt Bnft" . PHP_EOL;

    foreach ($pledges as $pledge) {
      if ($pledge < 1000000) {
        $pledge_str = round($pledge / 1000, 1) . "k";
      } else {
        $pledge_str = round($pledge / 1000000, 1) . "m";
      }

      // Current Formula (same as alternate formula with curve_root = 1)
      $s = $pledge / $total_stake;
      $rewards = round(($R / (1 + $a0)) * ($o + ($s * $a0 * (($o - ($s * (($z0 - $o) / $z0))) / $z0))));
      $benefit = round(((($rewards / $comparison_rewards) - 1) * 100), 2);

      $alt_numerator = pow($pledge, (1 / $curve_root)) * pow($crossover, (($curve_root - 1) / $curve_root));
      $alt_s = $alt_numerator / $total_stake;
      $alt_rewards = round(($R / (1 + $a0)) * ($o + ($alt_s * $a0 * (($o - ($alt_s * (($z0 - $o) / $z0))) / $z0))));
      $alt_benefit = round(((($alt_rewards / $comparison_rewards) - 1) * 100), 2);

      echo $pledge_str . "\t" . $rewards . "\t" . $benefit . "%\t" . $alt_rewards . "\t" . $alt_benefit . "%" . PHP_EOL;
    }

    echo PHP_EOL;
  }
}

