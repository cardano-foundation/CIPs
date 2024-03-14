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
  RoyaltyRecipient, 
  DatumMetadata, 
  Metadata, 
  RoyaltyFlag, 
  MediaAssets 
} from "./types.ts";

/**
 * Included in this file:
 *  - createRoyalty() - creates a royalty token with no other assets
 *  - mintNFTs() - mints CIP-68 nfts, may include a royalty token in the transaction as well
 *  - createTimelockedMP() - utility to create a parameterized minting policy
 */

// generated from the onchain-reference directory
const timeLockMintingContract = '5906e90100003232323232323232323232322322322232533300b53300c49107656e746572656400132533300c533300c533300c3322323253330103370e9001000899b89375a602c601a0040062940c034004c00cc02cc050c054c02cc050c054c054c054c054c054c054c054c02c008c004c02400c01c5288a99806a493269735f6e6f745f65787069726564286374782e7472616e73616374696f6e2c206c6f636b5f74696d6529203f2046616c73650014a02a6660186644646600200200644a66602800229404c8c94ccc048cdc78010028a511330040040013018002375c602c0026eb0c048c04cc04cc04cc04cc04cc04cc04cc04cc024c004c02400c0145288a99806a493a6c6973742e686173286374782e7472616e73616374696f6e2e65787472615f7369676e61746f726965732c206f776e657229203f2046616c73650014a0294054cc0352410670617373656400132533300d3370e9000180580089919191919299809a490a7175616e746974793a20001533013332323232323223732660046ea0005221003001001222533333302100213232323233009533301d337100069007099b80483c80400c54ccc074cdc4001a410004266e04cdc0241002800690070b19b8a4890128000015333020001133714911035b5d2900004133714911035b5f2000375c603e66600e00266ec1300102415d00375266e292210129000042233760980103422c2000375266601001000466e28dd718100009bae30210013758603c0046eb4c070004c8cdd81ba8301c001374e603a0026ea80084c94ccc0780044cdc5245027b7d00002133714911037b5f2000375c603a6644646600200200844a6660440022008266006604800266004004604a00266ec130010342207d0037520044466ec1300103422c2000375266600c00c603c00466e29221023a2000333006006301f002337146eb8c078004dd7180f8009bab002132533301e0011337149101025b5d00002133714911035b5f2000375c603a66600a00266ec1300102415d0037520044466ec1300103422c2000375266600c00c00466e28dd7180f0009bae301f001375800426600a6eb40080044c8cdc5244102682700332232333001001003002222533301f3371000490000800899191919980300319b8100548008cdc599b80002533302233710004900a0a40c02903719b8b33700002a66604466e2000520141481805206e0043370c004901019b8300148080cdc700300119b81371a002900119b8a4881012700002375c004444646600200200844a66603c0022008266006604000266004004604200244646600200200644a66603066e1c0052000133714910101300000315333018337100029000099b8a489012d003300200233702900000089980299b8400148050cdc599b803370a002900a240c00066002002444a66602a66e2400920001001133300300333708004900a19b8b3370066e140092014481800040044c94ccc04ccdc3a40000022a66602666e25200200214a22a66028921157175616e74697479203e3d2031203f2046616c73650014a02a66602666e24009200114a22a66028921167175616e74697479203c3d202d31203f2046616c73650014a060200146eb4c05c004c05c004c058004dd6180a00098050008a998072481244578706563746564206f6e20696e636f727265637420436f6e7374722076617269616e74001632323233323001001222533301600214c103d87a80001323253330143370e0069000099ba548000cc064dd380125eb804ccc014014004cdc0801a400460340066eb0c0600080052000323300100100222533301400114bd70099199911191980080080191299980d00088018991999111980f9ba73301f37520126603e6ea400ccc07cdd400125eb80004dd7180c8009bad301a00133003003301e002301c001375c60260026eacc050004cc00c00cc060008c058004c8cc004004008894ccc04c00452f5bded8c0264646464a66602666e3d221000021003133018337606ea4008dd3000998030030019bab3015003375c6026004602e004602a0026eacc048c04cc04cc04cc04cc024c004c02400c54cc0352401254578706563746564206f6e20696e636f727265637420426f6f6c65616e2076617269616e74001623012001149854cc0312411856616c696461746f722072657475726e65642066616c7365001365632533300b3370e90000008a99980798040018a4c2a660180142c2a66601666e1d20020011533300f3008003149854cc0300285854cc03124128436f6e73747220696e646578206469646e2774206d61746368206120747970652076617269616e7400163008002375c0026eb40048c01cdd5000918029baa00149011d4578706563746564206e6f206669656c647320666f7220436f6e737472005734ae7155ceaab9e5573eae815d0aba257481'

/**
 * Create a royalty token with no other assets
 * @param lucid a lucid instance with a wallet already selected
 * @param policy the minting policy to mint off of
 * @param validator the validator to lock reference & royalty datums ator 
 * @param royalty the royalty metadata
 * @returns a TxComplete object, ready to sign & submit
 */
export async function createRoyalty(lucid: Lucid, policy: Script, validator: Script, royalty: RoyaltyRecipient) {
	const royaltyDatum = Data.to<DatumMetadata>({
		metadata: Data.castFrom<Metadata>(Data.fromJson([royalty]), Metadata),
		version: BigInt(1),
		extra: Data.from<Data>(Data.void())
	}, DatumMetadata)

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
 * - RoyaltyRecipient - a new royalty token is minted to the policy in this transaction according to the information in the parameter 
 * @returns an object containing a TxComplete object & the policyId of the minted assets
 */
  export async function mintNFTs(
	lucid: Lucid,
	policy: Script,
  validator: Script,
	sanitizedMetadataAssets: MediaAssets,
	cip102?: "NoRoyalty" | "Premade" | RoyaltyRecipient
) {
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
			const royaltyDatum = Data.to<DatumMetadata>({
				metadata: Data.castFrom<Metadata>(Data.fromJson([royalty]), Metadata),
				version: BigInt(1),
				extra: Data.from<Data>(Data.void())
			}, DatumMetadata)

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
				const metadataDatum = Data.to<DatumMetadata>({
					metadata: Data.castFrom<Metadata>(Data.fromJson(sanitizedMetadataAssets[tokenName]), Metadata),
					version: BigInt(1),
					extra
				}, DatumMetadata)

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
	timestamp: number,
	walletAddress: string
) {
	const paymentHash = lucid.utils.getAddressDetails(walletAddress).paymentCredential?.hash;
  
  if(!paymentHash)
    throw new Error("Payment hash not found")

	const policy: Script = {
	  type: "PlutusV2",
	  script: applyParamsToScript(timeLockMintingContract, [BigInt(timestamp), paymentHash]),
	}
	return policy;
}