# Byron key format

- **Deprecated**: yes
- **Summary**: used by old versions of Daedalus to generate addresses starting with `Ddz`.

## Code

```js
function generateMasterKey(seed) {
    return hashRepeatedly(seed, 1);
}

function hashRepeatedly(key, i) {
    (iL, iR) = HMAC
        ( hash=SHA512
        , key=key
        , message="Root Seed Chain " + UTF8NFKD(i)
        );

    let prv = tweakBits(SHA512(iL));

    if (prv[31] & 0b0010_0000) {
        return hashRepeatedly(key, i+1);
    }

    return (prv + iR);
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
  <summary>Requires no iteration</summary>

  recovery phrase
  ```
  roast crime bounce convince core happy pitch safe brush exit basic among
  ```

  master key
  ```
  60f6e2b12f4c51ed2a42163935fd95a6c39126e88571fe5ffd0332a4924e5e5e9ceda72e3e526a625ea86d16151957d45747fff0f8fcd00e394b132155dfdfc2918019cda35f1df96dd5a798da4c40a2f382358496e6468e4e276db5ec35235f
  ```
</details>

---

<details>
  <summary>Requires 4 iterations</summary>

  recovery phrase
  ```
  legend dismiss verify kit faint hurdle orange wine panther question knife lion
  ```

  master key
  ```
  c89fe21ec722ee174be77d7f91683dcfd307055b04613f064835bf37c58f6a5f362a4ce30a325527ff66b6fbaa43e57c1bf14edac749be3d75819e7759e9e6c82b264afa7c1fd5b3cd51be3053ccbdb0224f82f7d1c7023a96ce97cb4efca945
  ```
</details>
