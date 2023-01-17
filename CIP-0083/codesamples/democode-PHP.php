// ------------------------------------------------------------------------------------------
// Demonstration implementation of CIP-0020 Transaction Messages Encryption/Decryption via PHP
// ------------------------------------------------------------------------------------------

<?php

const debug = true;

function elapsedTime($start) {
    $elapsed = microtime(true) - $start;
    if ($elapsed < 1) {
        return ($elapsed * 1000) . " milliseconds";
    } else if ($elapsed > 60) {
        return ($elapsed / 60) . " minutes";
    } else {
        return $elapsed . " seconds";
    }
}

function getPbkdf2($password, $salt, $iterations) {
    return openssl_pbkdf2($password, $salt, 48, $iterations, 'sha256');
}

function encryptCardanoMessage($msg, $password = 'cardano', $iterations = 10000) {
    if (debug) {
        $start = microtime(true);
    }
    $salt          = openssl_random_pseudo_bytes(8);
    $encryptedText = "Salted__" . $salt;

    $keyIV = getPbkdf2($password, $salt, $iterations);
    $key   = substr($keyIV, 0, 32);
    $iv    = substr($keyIV, 32);

    $encryptedText       .= openssl_encrypt($msg, 'aes-256-cbc', $key, OPENSSL_RAW_DATA, $iv);
    $hashedEncryptedText = base64_encode($encryptedText);

    if (debug) {
        echo "Done encrypting message in " . elapsedTime($start) . "\r\n";
    }

    return $hashedEncryptedText;
}

function decryptCardanoMessage($msg, $password = 'cardano', $iterations = 10000) {
    if (debug) {
        $start = microtime(true);
    }

    $encryptedText = base64_decode($msg);
    $salt          = substr($encryptedText, 8, 8);
    $cyphertext    = substr($encryptedText, 16);

    $keyIV = getPbkdf2($password, $salt, $iterations);
    $key   = substr($keyIV, 0, 32);
    $iv    = substr($keyIV, 32);

    $decrypted = openssl_decrypt($cyphertext, 'aes-256-cbc', $key, OPENSSL_RAW_DATA, $iv);

    if (debug) {
        echo "Done decrypting message in " . elapsedTime($start) . "\r\n";
    }

    return $decrypted;
}

$payload = "Testing message signing...";

// Basic signed/encrypted message w/ default password of "cardano"
$signed = encryptCardanoMessage($payload);

// Basic signed/encrypted message w/ custom password
$passwordSigned = encryptCardanoMessage($payload, "You'll never guess it!");

// Basic signed/encrypted message w/ custom password and fewer iterations
$shortPasswordSigned = encryptCardanoMessage($payload, "Please", 20);

// Basic decoding w/ default password of "cardano"
$unsigned = decryptCardanoMessage($signed);
echo "\$signed is: {$unsigned}\r\n";

// Basic decoding w/ custom password
$unsignedPassword = decryptCardanoMessage($passwordSigned, "You'll never guess it!");
echo "\$passwordSigned is: {$unsignedPassword}\r\n";

// Basic decoding w/ custom password and fewer iterations
$shortUnsigned = decryptCardanoMessage($shortPasswordSigned, "Please", 20);
echo "\$shortPasswordSigned is: {$shortUnsigned}\r\n";
