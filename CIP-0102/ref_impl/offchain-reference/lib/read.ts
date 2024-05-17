import type { Royalty, RoyaltyConstr } from './types/royalties.ts';
import type { output } from "./types/chain.ts";
import { Data, toText } from 'https://deno.land/x/lucid@0.10.7/mod.ts';
import { getAssetsTransactions, getScriptsDatumCbor, getTxsUtxos } from "../utils/query.ts";
import { CIP102_ROYALTY_TOKEN_NAME, fromOnchainRoyalty } from '../conversion.ts';

/**
 * Queries the blockchain for the royalty metadata of a CIP-102 collection
 * @param policyId the policy id of the collection
 * @returns the royalty metadata in the form of an array of royalty recipients
 */
export async function getRoyaltyPolicy(
	policyId: string
): Promise<Royalty[]> {
	const asset_unit = policyId + CIP102_ROYALTY_TOKEN_NAME;
	try {
    // get the last tx of the royalty token
		const lastTx = await getAssetsTransactions(
			asset_unit,
			1,
			1,
			'desc'
		);
		const lastTxHash = lastTx?.at(0)?.tx_hash;
		if (lastTxHash) {
      // get the utxos of the last tx
			const txUtxos = await getTxsUtxos(lastTxHash);

      // parse the utxos to find the royalty metadata
			const royaltyData = await Promise.all(
				txUtxos.outputs.map(async (output: output) =>
					await getRoyaltyMetadata(output)
			));

      // return the royalty metadata in the form of an array of royalty recipients with the fee converted to percentage
			return royaltyData.flat().map((royaltyData) => { 
        return { ...royaltyData, fee: fromOnchainRoyalty(royaltyData.fee) }
      });
		}
	} catch (_error) {
		// Best effort just silently fail
	}
	return [];
}

/**
 * Checks for royalty metadata in a given utxo
 * @param out the utxo to examine
 * @returns an array of royalty recipients if the utxo contains royalty metadata, [] if not
 */
async function getRoyaltyMetadata(out: output): Promise<Royalty[]> {
	let datum;
  // get the datum of the utxo
	if(!out.inline_datum && out.data_hash)
		datum = out.inline_datum ?? await getScriptsDatumCbor(out.data_hash).then(dat => dat.cbor)
	else
		datum = out.inline_datum
	if (datum) {
		try {
      // try to parse the datum, return it as an array of royalty recipients if successful
			const datumConstructor: RoyaltyConstr = Data.from(datum);
			const datumData = datumConstructor.fields[0];
			if (Array.isArray(datumData)) {
				const royalties = datumData
					.map((royaltyMap) => decodeDatumMap(royaltyMap))
					.filter((royalty) => royalty);
				return royalties as Royalty[];
			}
		} catch (_error) {
			// do nothing
		}
	}
	return [];
}

/**
 * Parse a datum & check for royalty metadata
 * @param data the datum to parse
 * @returns a royalty recipient if the datum contains royalty metadata, undefined if not
 */
function decodeDatumMap(
	data: Map<string, string | bigint>
): Royalty | undefined {
	const model: { [key: string]: string | number } = {};

  // parse the datum to a javascript object
	data.forEach((value, key) => {
		model[toText(key)] =
			typeof value === 'string' ? toText(value) : Number(value);
	});

  // check if the object contains the required fields. This could be more robust, but it's functional as is.
	if ('address' in model && 'fee' in model) {
		return model as unknown as Royalty;
	}
}