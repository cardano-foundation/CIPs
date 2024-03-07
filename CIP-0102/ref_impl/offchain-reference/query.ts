import { asset_transactions, output } from "./types.ts";
import { getEnv } from "./utils/env.ts";

// based on Blockfrost's openAPI
const blockfrost_url = getEnv("BLOCKFROST_URL");
const headers = {
  project_id: getEnv("BLOCKFROST_PROJECT_KEY"), lucid: "0.10.7"
}

export async function getAssetsTransactions(
  asset: string,
  _count: number = 100,
  _page: number = 1,
  _order: 'asc' | 'desc' = 'asc',
  ): Promise<asset_transactions> 
{
  const response =
    await fetch(
      blockfrost_url + "/assets/" + asset + "/transactions",
      { headers },
    ).then((res) => res.json());

  return response;
}

export async function getTxsUtxos(txHash: string): Promise<{ outputs: output[] }> {
  const response =
    await fetch(
      blockfrost_url + "/txs/" + txHash + "/utxos",
      { headers },
    ).then((res) => res.json());

  return response;
}

export async function getScriptsDatumCbor(datumHash: string): Promise<{ cbor: string }> {
  const response =
    await fetch(
      blockfrost_url + "/scripts/datum/" + datumHash + "/cbor",
      { headers },
    ).then((res) => res.json());

  return response;
}