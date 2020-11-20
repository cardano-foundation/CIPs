# Icarus key format

- **Deprecated**: no
- **Summary**: Used by Yoroi during the Byron-era (with Byron-style addresses starting with Ae2). Currently used for all Shelley-era wallets.

*Note*: Also supports setting an extra passphrase as an arbitrary byte array of any size (sometimes called a *mnemonic password*). This passphrase acts as a second factor applied to cryptographic key retrieval. When the seed comes from an encoded recovery phrase, the password can therefore be used to add extra protection in case where the recovery phrase were to be exposed.

## Code

```js
function generateMasterKey(seed, password) {
    let data = PBKDF2
        ( kdf=HMAC-SHA512
        , iter=4096
        , salt=seed
        , password=password
        , outputLen=96
        );

    return tweakBits(data);
}

function tweakBits(data) {
    // on the ed25519 scalar leftmost 32 bytes:
    // * clear the lowest 3 bits
    // * clear the highest bit
    // * clear the 3rd highest bit
    // * set the highest 2nd bit
    data[0]  &= 0b1111_1000;
    data[31] &= 0b0001_1111;
    data[31] |= 0b0100_0000;

    return data;
}
```
## Test vectors

<details>
  <summary>No passphrase</summary>

  recovery phrase
  ```
  eight country switch draw meat scout mystery blade tip drift useless good keep usage title
  ```

  master key
  ```
  c065afd2832cd8b087c4d9ab7011f481ee1e0721e78ea5dd609f3ab3f156d245d176bd8fd4ec60b4731c3918a2a72a0226c0cd119ec35b47e4d55884667f552a23f7fdcd4a10c6cd2c7393ac61d877873e248f417634aa3d812af327ffe9d620
  ```
</details>

---

<details>
  <summary>With passphrase</summary>

  recovery phrase
  ```
  eight country switch draw meat scout mystery blade tip drift useless good keep usage title
  ```

  passphrase
  ```
  foo (as utf8 bytes)
  ```

  master key
  ```
  70531039904019351e1afb361cd1b312a4d0565d4ff9f8062d38acf4b15cce41d7b5738d9c893feea55512a3004acb0d222c35d3e3d5cde943a15a9824cbac59443cf67e589614076ba01e354b1a432e0e6db3b59e37fc56b5fb0222970a010e
  ```
</details>

## Trezor

When used < 24 words, the algorithm is the same as **Icarus**

When using 24 words, **TODO**

*Note*: Trezor also allows users to set an additional [passphrase](https://wiki.trezor.io/Passphrase) that works exactly the same as Icarus passphrase
