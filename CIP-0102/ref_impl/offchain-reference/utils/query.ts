import { asset_transactions, output } from "../lib/types/chain.ts";
import { getEnv } from "../scripts/env.ts";

// Barebones Blockfrost query wrappers. Based on Blockfrost's openAPI.

const blockfrost_url = getEnv("BLOCKFROST_URL");
const headers = {
  project_id: getEnv("BLOCKFROST_PROJECT_KEY"), lucid: "0.10.7"
}

/**
 * Get the transactions of an asset
 * @param asset the asset to query for
 * @param _count unused for now
 * @param _page unused for now
 * @param _order unused for now
 * @returns 
 */
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

/**
 * Get the utxos of a transaction
 * @param txHash the hash of the transaction
 * @returns 
 */
export async function getTxsUtxos(txHash: string): Promise<{ outputs: output[] }> {
  const response =
    await fetch(
      blockfrost_url + "/txs/" + txHash + "/utxos",
      { headers },
    ).then((res) => res.json());

  return response;
}

/**
 * Get a cbor datum from its hash
 * @param datumHash the hash of the datum
 * @returns 
 */
export async function getScriptsDatumCbor(datumHash: string): Promise<{ cbor: string }> {
  const response =
    await fetch(
      blockfrost_url + "/scripts/datum/" + datumHash + "/cbor",
      { headers },
    ).then((res) => res.json());

  return response;
}