---
CIP: 0071
Title: Verified Stake-Pool Identity
Authors: Dennis Mittmann <dennis@iamx.id>
Status: Proposed
Type: Process
Created: 2022-10-18
License: CC-BY-4.0
---

## Abstract

This CIP defines a standard to verify Staking Pools using Decentralized Identifiers (DID)

## Motivation

The verification process of the authenticity of Staking Pools is currently a centralized effort. 

## High-Level Overview

1. Topic: Verification Validators Proof-of-Stake

2. Background: Legal / Compliance

3. Process Summary Pool Verification per identity source

   - a) Pool Owner / Holder: Option to attach verification data points to the pool
   
   - b) How: Connect Stake-Pool metadata to one or more Digital Identifiers (DIDs)
   
   - c) Data Points: Each of these data points stores information about a direct connection between the Stake-Pool operator and some sort of > identity source.
   
   - d) This > identity source could be a
     - d1) social account, examples: Twitter, Facebook, Discord, GitHub, Apple, LinkedIn, Twitch, Google, more;
     - d2) Know-Your-Customer (KYC), Know-Your-Business (KYB); Level: identity checks in up to 20 modules per jurisdiction and industry sector incl. financial transactions,
     - d3) any other source where an identity is directly linked to an account or something similar
     
   - e) Visibility and Audit: The data points connected to the Stake-Pool are publicly visible and can be audited by anyone. Either manually or programmatically.
   
   - f) Operator: The operator (HOLDER) can choose which identity data points he wants to connect to the pool,
   
   - g) Delegator: The delegator (VERIFIER) can then choose if he trusts those data points (verifiable credentials) to stake with the pool or not.
   
   - h) Product: The verified POOL owns a verifiable imprint with sources social media, KYC, KYB, other sources of reusable identity verification
   

### Glossary

Know-Your-Customer (KYC)

Know-Your-Business (KYB)

## Specification

### Structure

There are three different key components to this structure.

| Component                    | Description                                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| DID                          | The actual Decentralized Identity Document, where the information about the connected identity data points is stored. |
| Extended Stake-Pool Metadata | This metadata segment is placed in the Extended Stake-Pool Metadata and defines the connection to the DID.            |

#### 1. DID

This is an example DID taken from the official [W3C specification](https://www.w3.org/TR/did-core/#did-syntaxg).
To keep the scope reasonable, this CIP will not explain the DID specification deeper. Please refer to the W3C speciation as linked above.
The only important thing to note is that inside the DID document, the payload will contain KYC/KYB imprint Data that were linked to the DID document.

```
{
   "payload":{
      "timestamp":"2022.10.13",
      "company":"IAMX AG",
      "jurisdiction":"Switzerland",
      "company_type_national":"Aktiengesellschaft",
      "company_type_international":"public company limited by shares",
      "street":"Dammstr.",
      "street_number":"16",
      "zip":"6300",
      "city":"Zug",
      "country":"Switzerland",
      "VAT_identification_number":"CHE-270.340.034",
      "commercial_register":"CH-170.3.046.506-9",
      "date_of_incorporation":"2021.11.22",
      "pool_ticker":"IAMX"
   },
   "@context":"https://github.com/IAMXID/did-method-iamx",
   "signatures":[
      {
         "signature":"fnAp1inBgV7g5yZx86HaUaw43RZ8qgrjtriLcZ8RbcQhnUNrgLMKA6qxZz3CNGwsqzF3qtcWrKzaFijzgfNtEi98tQBhXHtLcW5dW5ysaPYcbRZAUPMfUVGxeQWMcB7h15mCQaqxYcnqPkpZwDiw3tk971wv3jim5SHtePGC2tpEbV71XF6QuNHFXbLfs82YxxUruEPLPQZi7RW59SUCVmpTdJPwUJbwL7TQdJkGcKJTNtuebowBzuZyPJEDCJQxR3MfyYvxo2mo9HYkvbFbwx5uLhkPQUhmwck6UdbbXhtaAJdZ4nW9EaBgJA2QyNRLAnQSBBRGwG8RApadGVX1hxiqxnc3sFazdcSkh6xVw4Y1aaTwdARZqAnae3mtHMJLDHQLtfhQxoYFpbzuugsdfBP4FtBV6LiCesT5xPCHNT1v71a6GQyEXUQeviwAnCzjvmKF1McvhAVEfdmgdFbpPK1Y9fW7p3Y9ZWudCHCmnQYZjGQsK9cz4uq636APLDfzpdnXHP72J73qUo8XqWvZoig9egmSHgTWKBo9WdvaBUsKBWb7ZpSyYj4wb9iz6xCa6DwgdAmAcWAfC87WomDSXo12t4kkyUS5ixYQRXgCLH11U4eQ9zLcwF9Zq46T4bmNDpFcsujBvg4SFC1JBYeV5f5FLU3NttR1jTdzjYzqWNoVeAQHZXykM6iZ8vqSNnD1BVDgRUZENmGNa1KhMxLriaBTYMmGfRfQydcYj3aNwU6p9JRhYupVPkueXGd1uMarBkj7UsQVsAH5zQybdaHNnagiihn1i9PxV1UrwLEhnTBPYTvvPorELEnFLdCNMtrxEvniK6uNcbubXRvoftoSYMmncDnrKaJu4RPuDAKpvwu8sjM3SfT4ws9cJqu1Zu15U3611K5BDPRFyWuK4pREgMKarKfPxLnWDqLm4g",
         "DID":[
            [
               "did:iamx:cardanozggW2SuC7Phxth3SAjhtz7YuNfrcDhoRTz5WrSZ2xh38BTwf",
               "Xpi6R1vn5PzPFkBb7S9XdNVSV6NGtXpYqF4kVGgytNcsxUvcztzn18V6LzibMzCc",
               "aEyb1RP3nfyNLQ6aZ4MKEKDCeWKReCGpQ7bvGoRZX12kUGqBbTpkskou81ZXpAMv",
               "UKe11tQY3GwK1or73VKhbdBjLxZf98z8hvYBopkwgqoSB9CL2rLSdBvuGc261irj",
               "RdagpY1ViRWqZbfwNHNharsnayv4NdRNfVnJXqUqu1ysfJNaLxaZosTnWMe8HPfs",
               "AbLanSRRWFeaET5xdaak8GP7ekKG961E2kfD6MfSthSS2n72DzqyHfssABhfzKBW",
               "weHDF76BuhyWi6XX8BGFBhk5nLeMFiiU3MKjfC4sqNNQ62iVcayqwLxECroFTHjw",
               "EDYdp61s7HVq43q7uYfJ8jqTts6mZXkZK2VWmbCmVDKYZMzDzqqFgQN6mznAj6Ei",
               "tcDSm2nCoSYSRErms3AKXtxS6NR36135kpxh3LhAEYNiBvjNhW6JVkBh37cFFPDu",
               "c2dSJvQYfhSzAHpHZK4pfHNe5bMiU8jxJC7WUAz8Gj9FAwQrXRJxS9qHD4G5CDfz",
               "WNUxU7ZJy1QmhWDb7Gb2ycMtRDF3dhgcGpYRKewbX4dgkSy8yarGwNindGJVhMTk",
               "t2Nmw2RayVHAiYvm4Y1LjZrVEXtx1oREbxKu885CRtgb1xegCYoy478Yz3bHfegE",
               "jsn52VvDab7NdWvYudkUgGxYG7ACoHfwdNpLY32fEULL9FCAowSTAsrkKLWa94M7",
               "tsh16Q3TSySGFFp48YjDnGsmh1jUAgzYU27Yt1LSedvzcAtjvPLsydXCEgz4LFnZ",
               "WAYYpKbQC8LRELM7HpX2fe4RLD1apPdVCwJkDqkDwD6a7TdVW3FvjpGGwC9puNwh",
               "vomgbeYuBJNz7AsfokCk7Vx5Q3YC4adidwg39X4Auapd3UuQ58BdTJVnZEavopdS"
            ]
         ],
         "description":"Issuer",
         "storageLocation":{
            "uri":"ipfs://QmYtZkfa6Qvjt3mhKJX1on9VGa1YYP9tFfALowcz2tHSeZ",
            "type":"ipfs"
         }
      },
      {
         "signature":"hZSpGWzRAcHfDu9mNdLJ9bWSsbCATE6FnJgG7RDRQFLRHnXZ9Cy2ULeJLnjgUW3N25eBiAmjUCSWqDpme3DWZRPJFbRuwhT5EfXYunC6p1Xi4L3Yw63uqKME5nkHLkQzLD6hVPuqyyZ74EWhh7v74BuouTa1ZytaWxoMRyEij7DXFnFbMCJkNczvxpXnCTMa79xT3YKUHE378ExuxyhvcHDKpCmAHLUzNcU8XwgDVzSkK2HDmxVtPXDpsRu5zJu9aUqC2hCerYroRCwsxT8NP32Nmq1qXhcmxSYFHYQoXU95AhwbMMo4kx9RQniZDhaRAfpQEYmXa6LmdrBAfuKmgvP57EKG4frSatpnPcz8t49PgVgZomWzgNS3sZjuu4PAqE5c9tDuZD8S62VqwHtbfbvwvE4sU3mvDYLiVH8rucMHax224v9ChViE8fMnzbMPpUkvo1aF2S8D12TCm773TU2CywoN3WLmYsJKwF95xCnH6ky49WUtxEy7sX3Ak4KG1kpY9ku4dg1MDfAw7QEkeHj3F4jmxnZREZaKBmxPUyvSW2qm1FSNursCkm4aVjT2e1HkmxS3GADVD2uqGMvQXU8Rk8bpftbD1zQ37XxC8WNgAox1b8SQzsdwCWzTJEtc36hBjN4uPzMLLZoaicbuLCJnk3KaNuxGp91JzzSmdDf8nYhGwktK5JiDCCxZ9EdopwDCMb88ozYjaqU8FTkdN2oVpRPYrPi6BCuZTL4Pd5YbkJTxv7DKdrJkt2gkdsiirMHfjmWhDrbhSQ67KxRyUfSUjyDE9REWBppbJcsNUX96TRkvVMNtb4SKiLYKdYnDrwkQzNjukBMYRUnG8ZjHZ1rSA6fnUys4kEsv9ws9FjZLaiJKgTfA7C9iXNeQcEpW3EFDh4E6TsCp3nkpVCG4MXhZRut6AavSmKNc3v",
         "DID":[
            [
               "did:iamx:cardanozggW2SuC7Phxth3SAjhtz7YuNfrcDhoRTz5WrSZ2xh38BTwf",
               "Xpi6R1vn5PzPFkBb7nNv7WBouf4cxMbeCqMxM6D3EeE16YbtUvGhDj9B3SFbRhoj",
               "nJmmq4qThvWtxcS6jvXVJg8unEQMHfrAyjh4rMm4GYgD21ud3nSGS242brxtN3Za",
               "MbaAJ9AJH52quhb6mjnhJRqzFF7qr6x92PfYpavjo6s2pq5oNMtbpky5yWwDVdj3",
               "x5s26WXXf4nN5kcPhyS8GD2oWfF8DjLzcdgWbwTU3wXiGBUyrXiyqzAmdnA49Ly7",
               "Ncsisu8MBtYAF2HioDjCLGidfJfuELuxVtumkyJapRAKEZSX3mJnbthAB6imuGYw",
               "rFyTTcjYiNzU3KGgTqMEiqjxvr5gZzaDHw6WLVsNr4S8XJWqGib6wsuxP1VbZpyf",
               "f78qBSmXwexBEYmEawVVq54Mp7PxkZre2Q69AAKVS3qFzZ7BzFpcqxu7trmvZLLB",
               "wWfTwYHJfGqJ6meShUVi69jDeV3XucDwipBWoDxTmpp9zY3eXG62Xu5MbHYdwQHG",
               "Eum8ArCbN71oKJWyAc149JoamrGRJTKCd9GwX2wBvWr97VsZCw4B6CXyjSKCHjvZ",
               "puePL1juS8b8yuU8rsUHrLhvVkGVPz7Wdj6XjcgFg9oLYwyQZNmBB7gmrVf5GrRY",
               "LdLRBcBjyAUcuNiGW9n52mpFSssYBQ79V4yaMbbBbP4JyA1KzXSGsTSNy48N9okb",
               "T4Syb3xLJsrMfjdfRzTYFpNSpYMNfgWkvYMHrEPrDBhSFkooo5FssXT8BS9kwnFs",
               "6uuwiQrXSwJBmFqVe7CDG6Z3j3bTCMdwumyhMNm5aoUdSMWuAWFz47pAH4aDoPCR",
               "5gXiEmqn8ecsxFiZfv4nZKFfjsVHVvxAYuwoJm5DP5W8gDRsG3ucbtGVp9MyuAMC",
               "peW3nAYJzjK5bpkcw7oGojAzV7VWAGfBpyTLY4CTC456N4kwbunXaVdfs9ALiGbv"
            ]
         ],
         "description":"Creator",
         "storageLocation":{
            "uri":"ipfs://QmRGaEGjyzrk3wNCwaPDydJtCrtJVddoeeAxQUHcizDdYU",
            "type":"ipfs"
         }
      },
      {
         "signature":"XwT21YCuCb2XbjgFuPCGuSZaiUEcXsnHYKSkCw8JhpLqyus9RU6Dy2XwjFJeUU6qnwCwnk6nZWKToqg52qNXafxzfSyj6GisrnWMNBMM7E8cVCsU5QX3JCpcadSHVBNws3us4XhtGviry9dE2MxgmaLopnjT4GtiPv5MY32bzEEGPYUgCiYKJzVLFUfeYMVu5e47NE9ZqqD8xdDLPneJnSgWLVGw5aWfhyzk52uUhBMuEe1WaQko876jYn2xmdZWfBEmKA7dHnTQjLjnS48LqzVxPJTg5sf8QRc7i9TiaXN7fkBb7RU9RmQDMjxkxaJGaeBtdhkEXofXVK7ykajvZs6Br8hRXXMBVJZX2kcJdfzwckguiaKGAraCj14b4YyfEtQDiiQjhjJf6JbHEudH1ZqVUG1969Qa4FFQjzJMABJeupo3bJW475FV7UPwjWdFu51j5oXjn19ntUWucGHUs7AurZyXVtooFsdo3YJCzHvTvQ4wh227QnrY6AAHZxNFt8UHXuLoG4XNtBNe5dRa6YDHS1tsXtcNcQEygtbrfyjhJ5KzEEkQxDdoeZKxqro1aKDpeg3R8h9hXSd9qxCZcK982qk38atNnMbMNYcgEPPXggaJapBLpkxEczBKDSqVpRyg9QmcJP3JJQdq5GEmJoZpuzfBpB29GELZ1tJYfYTF8FRZPwP8e7se1McTKjdvHi7T2fuYA58L7cpviYihXo2zAALVHAdDmoTPAci7nSLxLwWBT46HqL4jpjEpdPNRtCNsdar8sDDDqHwyKcXSRmmSz9pdw5mcrpChyFYYxSYfmsQocgm16cVbGkCKznpRSy2eLDbratBtPDqKr6eV2gkQdDkDQtRa1gR6512EU1P3isF1fMTzUmerAWbHFe4SwBMZdQYM2rQnJFJmctLBA9ZdEi5wWmZr5Q3M56",
         "DID":[
            [
               "did:iamx:cardanozggW2SuC7Phxth3SAjhtz7YuNfrcDhoRTz5WrSZ2xh38BTwf",
               "Xpi6R1vn5PzPFkBc81jEs2Fb3rjaJfCatjwKbCk4zCnxwtMdsj5BjEb4Vg7erDXw",
               "wUfjyrjdAckF13nEyHK4YFSJNYyp4vfxwd7ds9LszjgmtBU6f1yTeNzoAVSRAzQv",
               "pCVLPhGvzFFrH5wNfMEvs82KfMtjncgLanuFMH9UjupDJupkPv2eaoV9sFW7ifGP",
               "kUoAcKM98q2tmSfygL316Y9fSGcoC8fEjH9GANQ54aaiHrsUu7JszEAgkuq2Zxaz",
               "qoGznUo2UkBrij7Xn21D8DfSPSm9TtusBM1UWJWe3eZqZnDBgPKfBNMSLUpUauG6",
               "8WHpK1nKHP6kMpPi4WCnprpdpmU9KLzFeVRo8KWkwuQhxu8VDC6FZDRc7eHgVTCL",
               "KGfUnMtBqeMQGDB46JSEyGRW9wQsfmb4hsPM8teUk4uBU1UHJXmdKnxT7wYVw6Np",
               "1a1zEpyhF2deYX4Ki3ekmqMCPGcQ9FFLYPFDjJjnBgpFWkVe5maQHa8WupEEroMG",
               "NFEA6UmQaPypwCqA6aiVRDURWKPHuZFRaHAefmkdR2LoJjwmmNPtHr6iaEGN4fvD",
               "juYMzv4N2VDkKqm7cY8Y8k43Fx1wMzfQDQr9iq7SvWpB4xPMGFMsi6CDn5EjrQV4",
               "PKVLzbUmSkvvXRJ4MVkcD4YM2tDkCiFWQ4MbZcG9JivzeKVsoRKFUjmfkHBHMYe1",
               "iMede6UrLsg72mQezdgxZN8MtuYSVAhkYqToTABigWcnF8XqxX48mpnpeimzbeTZ",
               "5tgeR2o6v7KnRZi7THHs4DJEhrsAJiME2q67nLVz4AXWNomHK4MhGoWJh6kf3hMX",
               "shHHFHkduHRq36jy4gm7X5NEmuj1EzXqmqjwSNhosmWGYg2FmSbY413eBFJ7Toin",
               "UQD3wArwtMJBrzbTkQA6aGmrQRbvjfQNBvS1JMNEgKbN13FMqB9FQXr5N2fynRXA"
            ]
         ],
         "description":"IAMX",
         "storageLocation":{
            "uri":"ipfs://QmaCnFpHZqC6vUfVobUscCxRFn1snb3XH7K8W3ZEAkooeo",
            "type":"ipfs"
         }
      }
   ]
}
```

#### 3. Extended Stake-Pool metadata

This token can be linked in extended Stake-Pool metadata JSON

```
{
  "extended": "https://iamx.id/iamx_extended.json",
  "info": {
    "url_png_icon_64x64": "https://iamx.id/logoSmall_64x64.png",
    "url_png_logo": "https://iamx.id/logoBig.png",
    "location": "Zug,Swiss",
    "social": {
      "twitter_handle": "@iam_x_identity",
      "instagramm_handle": "@iam_x",
      "github_handle": "IAMXID"
    },
    "company": {
      "name": "IAMX AG"
    },
    "about": {
      "me": "The era of your identity serving as the product, controlled and capitalized by corporates is coming to an end.",
      "server": "Dedicated Servers hosted in a professional Swiss server center."
    },
    "@context": "https://github.com/IAMXID/did-method-iamx",    
    "files": [
      {
        "mediaType": "application/ld+json",
        "name": "vPOOL",
        "src": "ipfs://QmVPtEVqDAzhWYVKZPvAtCxHLHRQ11WZK6szSGfQFfrqQa"
      }
    ],
    "type": "Ed25519VerificationKey2020"
    "version" : "1.00",
  },
  "my-pool-ids": {}
}
```

## Cross-Chain Compatibility

To make this standard cross-chain compatible, it is possible to set the value of the src parameter under files to a unique identifier on another blockchain, where the DID might be located.

## Backwards Compatibility

To keep metadata compatible with changes coming up in the future, we use the **`version`** property.

## Rationale
The focus of this standard is on ease-of-use & flexibility. Using this standard, it is possible to reference DIDs not only on Cardano but at any arbitrary location, even cross-chain. It is also relatively simple to understand and implement because it borrows heavily from pre-existing metadata standards.

## Path to Active

By displaying this solution at the Catalyst Guild Hall, we hope to reach more creators that are willing to integrate this solution.

## References

- W3C DID Specification: https://www.w3.org/TR/did-core/#did-syntaxg
- CIP-0066 NFT-Identity

## Copyright

This CIP is licensed under CC-BY 4.0
