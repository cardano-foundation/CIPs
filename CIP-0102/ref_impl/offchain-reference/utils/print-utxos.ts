import { Lucid, Blockfrost } from 'https://deno.land/x/lucid@0.10.7/mod.ts';

import { getEnv } from './env.ts';

const network = getEnv('PUBLIC_CARDANO_NETWORK');
const address = getEnv('SERVICE_WALLET_ADDRESS');
const blockfrostUrl = getEnv(`BLOCKFROST_URL`);
const blockfrostKey = getEnv(`BLOCKFROST_PROJECT_KEY`);

console.log(address);

const blockfrost = new Blockfrost(blockfrostUrl, blockfrostKey);
const lucid = await Lucid.new(blockfrost, network);
const utxos = await lucid.utxosAt(address);

console.log(utxos);