import type { RoyaltyRecipient, output } from './types.ts';
import { Constr, Data, toText } from 'https://deno.land/x/lucid@0.10.7/mod.ts';
import { getAssetsTransactions, getScriptsDatumCbor, getTxsUtxos } from "./query.ts";

export const CIP102_ROYALTY_TOKEN_HEX = '001f4d70526f79616c7479'; // (500)Royalty

type RoyaltyConstr = Constr<
	Map<string, string | bigint> | Map<string, string | bigint>[]
>;

export function toCip102ContractRoyalty(percentage: number): number {
	return Math.floor(1 / (percentage / 1000));
}

export function percentageFromCip68Royalty(value: number): number {
	return Math.trunc((10 / value) * 1000) / 10;
}

export function getCip68BlockfrostVersion(version: string) {
	switch (version) {
		case 'CIP68v1':
			return 1;
		case 'CIP68v2':
			return 2;
		default:
			return undefined;
	}
}

export async function getCip102RoyaltyMetadata(
	policyId: string
): Promise<RoyaltyRecipient[]> {
	const assetName = policyId + CIP102_ROYALTY_TOKEN_HEX;
	// ------ uncomment when blockfrost will be ready ----------
	// const asset = await CardanoAssetsService.getAssets1(assetName);
	// if (asset.metadata) {
	//   return [asset.metadata]
	// }
	try {
		const lastTx = await getAssetsTransactions(
			assetName,
			1,
			1,
			'desc'
		);
		const lastTxHash = lastTx?.at(0)?.tx_hash;
		if (lastTxHash) {
			const txUtxos = await getTxsUtxos(lastTxHash);
			const royaltyData = await Promise.all(
				txUtxos.outputs.map(async (output: output) =>
					await getRoyaltyMetadata(output)
			));
			return royaltyData.flat();
		}
	} catch (_error) {
		// Best effort just silently fail
	}
	return [];
}


async function getRoyaltyMetadata(out: output): Promise<RoyaltyRecipient[]> {
	let datum;
	if(!out.inline_datum && out.data_hash)
		datum = out.inline_datum ?? await getScriptsDatumCbor(out.data_hash).then(dat => dat.cbor)
	else
		datum = out.inline_datum
	if (datum) {
		try {
			const datumConstructor: RoyaltyConstr = Data.from(datum);
			const datumData = datumConstructor.fields[0];
			if (Array.isArray(datumData)) {
				const royalties = datumData
					.map((royaltyMap) => decodeDatumMap(royaltyMap))
					.filter((royalty) => royalty);
				return royalties as RoyaltyRecipient[];
			}
		} catch (_error) {
			// do nothing
		}
	}
	return [];
}

function decodeDatumMap(
	data: Map<string, string | bigint>
): RoyaltyRecipient | undefined {
	const model: { [key: string]: string | number } = {};
	data.forEach((value, key) => {
		model[toText(key)] =
			typeof value === 'string' ? toText(value) : Number(value);
	});
	if ('address' in model && 'fee' in model) {
		return model as unknown as RoyaltyRecipient;
	}
}