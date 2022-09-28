# Minimal implementation of CIP-0068

## Concept

The minting policy is a one-shot policy. Only single NFT (pair of `reference NFT` and `user token`) can be minted. When deciding the burn the NFT the whole pair must be burned, otherwise the validator will throw an error.
PlutusTx was used to create the [on-chain code](onchain.hs) and [Lucid](https://github.com/spacebudz/lucid) for the [off-chain part](offchain.ts). It can be run in [Deno](https://deno.land/) and with a few modifications also in [Node.js](https://nodejs.org/) and Browser.

## Api

- mintNFT(assetName : string, metadata: Metadata)
- burnNFT(assetName : string)
- viewNFT(assetName : string)

## Run

```
deno run -A offchain.ts
```
