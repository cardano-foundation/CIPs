import { 
  Assets, 
  Constr, 
  Data, 
  Lucid, 
  Script, 
  Tx, 
  applyParamsToScript, 
  fromText, 
  toUnit 
} from "https://deno.land/x/lucid@0.10.7/mod.ts";

import {
	toCip102RoyaltyDatum,
	Royalty,
	RoyaltyFlag
} from './types/royalties.ts'

import {
	NFTMetadata,
	NFTDatumMetadata
} from './types/chain.ts'

import {
	MediaAssets,
	TxBuild
} from './types/utility.ts'

/**
 * Included in this file:
 *  - createRoyalty() - creates a royalty token with no other assets
 *  - mintNFTs() - mints CIP-68 nfts, may include a royalty token in the transaction as well
 *  - createTimelockedMP() - utility to create a parameterized minting policy
 */

/**
 * Create a royalty token with no other assets
 * @param lucid a lucid instance with a wallet already selected
 * @param policy the minting policy to mint off of
 * @param validator the validator to lock reference & royalty datums ator 
 * @param royalty the royalty metadata
 * @returns a TxComplete object, ready to sign & submit
 */
export async function createRoyalty(lucid: Lucid, policy: Script, validator: Script, royalty: Royalty) {
	const royaltyDatum = toCip102RoyaltyDatum([royalty])

  // generous tx validity window
	const validTo = new Date();
	validTo.setHours(validTo.getHours() + 1);
  
  // user wallet info
	const utxos = await lucid.wallet.getUtxos();
	const walletAddress = await lucid.wallet.address();

  // the royalty token
	const policyId = lucid.utils.mintingPolicyToId(policy);
	const nftUnit = toUnit(policyId, fromText("Royalty"), 500);

  // the royalty validator address
	const validatorAddress = lucid.utils.validatorToAddress(validator)
  
	const transaction = await lucid
	  .newTx()
	  .collectFrom(utxos)
	  .attachMintingPolicy(policy)
	  .mintAssets(
		{ [nftUnit]: BigInt(1) },
		Data.to(new Constr(0, [])) // Constr(1, []) to Burn
	  )
	  .validTo(validTo.getTime())
	  .addSigner(walletAddress)
	  .payToContract(
		validatorAddress,
		{ inline: royaltyDatum },
		{ [toUnit(policyId, fromText("Royalty"), 500)]: 1n }
	  ).complete()
  
	return transaction;
  }

/**
 * Mints CIP-68 nfts as specified in the sanitizedMetadataAssets parameter.
 * @param lucid a lucid instance with a wallet already selected
 * @param policy the minting policy to mint off of
 * @param validator the validator to lock reference & royalty datums at
 * @param sanitizedMetadataAssets the asset specification to mint off of
 * @param cip102 The cip102 parameter allows for 3 cases:
 * - "NoRoyalty" - no royalty is attached to the collection - obviously not recommended here but hey, it's your collection
 * - "Premade" - the royalty has already been minted to the policy - no need to mint new tokens, but include the flag to indicate a royalty token exists
 * - Royalty - a new royalty token is minted to the policy in this transaction according to the information in the parameter 
 * @returns an object containing a TxComplete object & the policyId of the minted assets
 */
  export async function mintNFTs(
	lucid: Lucid,
	policy: Script,
  validator: Script,
	sanitizedMetadataAssets: MediaAssets,
	cip102?: "NoRoyalty" | "Premade" | Royalty
): Promise<TxBuild> {
  // extract royalty information or mark undefined
	const royalty = cip102 === "NoRoyalty" || cip102 === "Premade" ? undefined : cip102;

  // get utxos from users wallet
	const utxos = await lucid.wallet.getUtxos();
	if (!utxos || !utxos.length || !utxos[0]) {
		return { error: 'empty-wallet' };
	}
	const referenceUtxo = utxos[0];

  // calculate the assets to mint
	const tokenNames = Object.keys(sanitizedMetadataAssets);
	console.log(policy)
	const policyId = lucid.utils.mintingPolicyToId(policy);
	const assets: Assets = {};
	if(royalty)
		assets[toUnit(policyId, fromText("Royalty"), 500)] = 1n;
	tokenNames.forEach((tokenName) => {
    assets[toUnit(policyId, fromText(tokenName), 100)] = 1n;
    assets[toUnit(policyId, fromText(tokenName), 222)] = 1n;
	});

  // addresses to send assets to
	const validatorAddress = lucid.utils.validatorToAddress(validator)
  const walletAddress = await lucid.wallet.address()

  // generous tx validity window
	const validTo = new Date();
	validTo.setHours(validTo.getHours() + 1);

	let incompleteTx = await lucid
		.newTx()
		.collectFrom([...utxos, referenceUtxo])
		.attachMintingPolicy(policy)
		.mintAssets(assets, Data.to(new Constr(0, [])))
		.validTo(validTo.getTime())
		.addSigner(walletAddress)

  // send assets & datums to associated addresses  
	const attachDatums = (tx: Tx): Tx => {
		if(royalty) {
      // construct the royalty datum
			const royaltyDatum = toCip102RoyaltyDatum([royalty])

      // attach the royalty token & datum to the transaction
			tx = tx.payToContract(
				validatorAddress,
				{ inline: royaltyDatum },
				{ [toUnit(policyId, fromText("Royalty"), 500)]: 1n }
			)
		}

    // attach the royalty flag to the reference tokens if a royalty policy exists
    const has102Royalty = cip102 === "Premade" || royalty !== undefined;
    const extra = has102Royalty 
      ? Data.to<RoyaltyFlag>({ royalty_included: BigInt(1) }, RoyaltyFlag)
      : Data.from<Data>(Data.void());

		for(const tokenName of tokenNames) {
        // construct the reference datum
				const metadataDatum = Data.to<NFTDatumMetadata>({
					metadata: Data.castFrom<NFTMetadata>(Data.fromJson(sanitizedMetadataAssets[tokenName]), NFTMetadata),
					version: BigInt(1),
					extra
				}, NFTDatumMetadata)

        // attach the reference token & datum to the transaction
				tx = tx.payToContract(
					validatorAddress, 
					{ inline: metadataDatum }, 
					{ [toUnit(policyId, fromText(tokenName), 100)]: BigInt(1) }
				)
		}

		return tx;
	}

	incompleteTx = await attachDatums(incompleteTx)

	const tx = await incompleteTx.complete()

	return { tx, policyId };
}

/**
 * parameterize the timelocked minting policy with your wallet address & minting deadline
 * @param lucid a lucid instance with a wallet already selected
 * @param timestamp the minting deadline
 * @param walletAddress the wallet address allowed to mint
 * @returns the minting policy in a Script object
 */
export function createTimelockedMP(
	lucid: Lucid,
	mp: string,
	timestamp: number,
	walletAddress: string
) {
	const paymentHash = lucid.utils.getAddressDetails(walletAddress).paymentCredential?.hash;
  
  if(!paymentHash)
    throw new Error("Payment hash not found")

	const policy: Script = {
	  type: "PlutusV2",
	  script: applyParamsToScript(mp, [BigInt(timestamp), paymentHash]),
	}
	return policy;
}