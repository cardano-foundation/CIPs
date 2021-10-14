# Ledger key format

- **Deprecated**: no
- **Summary**: Used by Ledger hardware wallets

*Note*: Ledger also allows users to set an additional [passphrase](https://support.ledger.com/hc/en-us/articles/115005214529-Advanced-passphrase-security)

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
        , message=UTF8NFKD(1) + seed
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
  1091f9fd9d2febbb74f08798490d5a5727eacb9aa0316c9eeecf1ff2cb5d8e55bc21db1a20a1d2df9260b49090c35476d25ecefa391baf3231e56699974bdd46652f8e7dd4f2a66032ed48bfdffa4327d371432917ad13909af5c47d0d356beb
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
