import { createTimelockedMP, mintNFTs } from "../lib/mint.ts";
import { MediaAssets, Royalty, TxBuild } from "../lib/types/index.ts";
import { getRoyaltyPolicy } from "../lib/read.ts";
import { Lucid, Blockfrost, Network, Script, PlutusVersion } from "https://deno.land/x/lucid@0.10.7/mod.ts";
import { getEnv } from "./env.ts";
import contracts from "../../onchain-reference/plutus.json" with { type: "json" };

/**
 * MAIN
 * Sets up a mock frontend with a collection of required variables
 * Then selects an action based on the parameter passed in by the user
 */

const purpose = Deno.args[0];

// get environment variables
const blockfrostUrl = getEnv("BLOCKFROST_URL")
const projectId = getEnv("BLOCKFROST_PROJECT_KEY")
const cardanoNetwork = getEnv("PUBLIC_CARDANO_NETWORK")
const walletAddress = getEnv("WALLET_ADDRESS")
const privateKey = getEnv("WALLET_PRIVATE_KEY")

// set up a blockfrost-connected lucid instance
const bf: Blockfrost = new Blockfrost(blockfrostUrl, projectId)
const lucid: Lucid = await Lucid.new(bf, cardanoNetwork as Network)
lucid.selectWalletFromPrivateKey(privateKey)

// isolate the contracts' cbor
const type: PlutusVersion = "PlutusV2";
const alwaysFails = {
  type,
  script: contracts.validators.find((v) => v.title === "always_fails.spend")?.compiledCode ?? ""
}

const timelockedMP = {
  type,
  script: contracts.validators.find((v) => v.title === "minting.minting_validator")?.compiledCode ?? ""
}

// interpret the user input and execute the requested action
selectAction().then(console.log)

// Frontend Utilities

/**
 * Utility to select an action based on the purpose parameter passed in by the user
 */
async function selectAction() {
	switch(purpose) {
		case "mint-collection":
			return await runTx(() => testTimelockedMint(lucid, timelockedMP, alwaysFails, walletAddress))
		case "get-royalties":
			return await getRoyaltyPolicy(Deno.args[1])
		default:
			return { error: "no transaction selected" }
	}
}

/**
 * A simple function to attempt to build a tx, sign it, and submit it to the blockchain
 * @param txBuilder the frontend transaction builder, often just a simple tunnel to the offchain library
 */
async function runTx(txBuilder: () => Promise<TxBuild>) {
	const txBuild = await txBuilder()
	if(!txBuild.tx) {
		return txBuild.error;
	}
	else {
		//console.log(txBuild)
		const signedTx = await txBuild.tx.sign().complete();
		const txHash = await signedTx.submit();
		return txHash;
	}
}

/** 
 *  Examples of constructing transactions from the frontend using the endpoints defined in this library. 
 *   - testTimelockedMint: a collection with CIP 68 NFTs and a CIP 102 royalty
 * */

function testTimelockedMint(lucid: Lucid, mp: Script, validator: Script, walletAddress: string): Promise<TxBuild> {

  // configuration - these would come from user input. Adjust these however you wish.
  const mock_image = "ipfs://QmeTkA5bY4P3DUjhdtPc2MsT8G8keb7HAxjccKrLJN2xTz"
  const mock_name = "test"
  const mock_deadline = new Date("2024-12-31T23:59:59Z").getTime()
  const mock_size = 5
  const mock_fee = 1.6

  // parameterize minting policy
	const parameterized_mp = createTimelockedMP(lucid, mp.script, mock_deadline, walletAddress);

  // define media assets for each nft
	const assets: MediaAssets = {}
	for(let i = 0; i < mock_size; i++) {
		const tempdetails = {
			name: mock_name + i,
			image: mock_image
			};
		assets[mock_name + i] = tempdetails
	}

  // define royalty policy
	const royalties: Royalty[] = [{
		address: walletAddress,
		fee: mock_fee
	}]

	return mintNFTs(
		lucid,
		parameterized_mp,
    validator,
		assets,
		royalties[0]
	)
}