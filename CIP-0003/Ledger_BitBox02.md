# Ledger/BitBox02 key format

- **Deprecated**: no
- **Summary**: Used by Ledger hardware wallets

Reference implementation by Ledger: [HDEd25519.py](https://github.com/LedgerHQ/orakolo/blob/0b2d5e669ec61df9a824df9fa1a363060116b490/src/python/orakolo/HDEd25519.py)

Implementation by BitBox02: [keystore.c](https://github.com/digitalbitbox/bitbox02-firmware/blob/1e36dbfb3c71c3a9d8ea81fe6fad13b18dd735a4/src/keystore.c#L676-L709)

*Note*: Ledger and BitBox02 also allow users to set an additional [passphrase](https://support.ledger.com/hc/en-us/articles/115005214529-Advanced-passphrase-security)

## Code

```js
function generateMasterKey(seed, password) {
    let data = PBKDF2
        ( kdf=HMAC-SHA512
        , iter=2048
        , salt="mnemonic" + UTF8NFKD(password)
        , password=UTF8NFKD(spaceSeparated(toMnemonic(seed)))
        , outputLen=64
        );

    let cc = HMAC
        ( hash=SHA256
        , key="ed25519 seed"
        , message=UTF8NFKD(1) + data
        );

    let (iL, iR) = hashRepeatedly(data);

    return (tweakBits(iL) + iR + cc);
}

function hashRepeatedly(message) {
    let (iL, iR) = HMAC
        ( hash=SHA512
        , key="ed25519 seed"
        , message=message
        );

    if (iL[31] & 0b0010_0000) {
        return hashRepeatedly(iL + iR);
    }

    return (iL, iR);
}

function tweakBits(data) {
    // * clear the lowest 3 bits
    // * clear the highest bit
    // * set the highest 2nd bit
    data[0]  &= 0b1111_1000;
    data[31] &= 0b0111_1111;
    data[31] |= 0b0100_0000;

    return data;
}
```

## Test vectors

<details>
  <summary>No passphrase no iterations</summary>

  recovery phrase
  ```
  recall grace sport punch exhibit mad harbor stand obey short width stem awkward used stairs wool ugly trap season stove worth toward congress jaguar
  ```

  master key
  ```
  a08cf85b564ecf3b947d8d4321fb96d70ee7bb760877e371899b14e2ccf88658104b884682b57efd97decbb318a45c05a527b9cc5c2f64f7352935a049ceea60680d52308194ccef2a18e6812b452a5815fbd7f5babc083856919aaf668fe7e4
  ```
</details>

---

<details>
  <summary>No passphrase with iterations</summary>

  recovery phrase
  ```
  correct cherry mammal bubble want mandate polar hazard crater better craft exotic choice fun tourist census gap lottery neglect address glow carry old business
  ```

  master key
  ```
  587c6774357ecbf840d4db6404ff7af016dace0400769751ad2abfc77b9a3844cc71702520ef1a4d1b68b91187787a9b8faab0a9bb6b160de541b6ee62469901fc0beda0975fe4763beabd83b7051a5fd5cbce5b88e82c4bbaca265014e524bd
  ```
</details>

---

<details>
  <summary>With passphrase</summary>

  recovery phrase
  ```
  abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art
  ```

  passphrase
  ```
  foo (as utf8 bytes)
  ```

  master key
  ```
  f053a1e752de5c26197b60f032a4809f08bb3e5d90484fe42024be31efcba7578d914d3ff992e21652fee6a4d99f6091006938fac2c0c0f9d2de0ba64b754e92a4f3723f23472077aa4cd4dd8a8a175dba07ea1852dad1cf268c61a2679c3890
  ```
</details>
