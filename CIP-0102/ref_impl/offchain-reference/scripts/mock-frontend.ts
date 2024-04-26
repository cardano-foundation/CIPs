import { createTimelockedMP, mintNFTs } from "../lib/mint.ts";
import { MediaAssets, RoyaltyRecipient } from "../lib/types.ts";
import { getAssetsTransactions } from "../utils/query.ts"
import { getRoyaltyPolicy } from "../lib/read.ts";
import { Lucid, Blockfrost, Network, Script, PlutusVersion } from "https://deno.land/x/lucid@0.10.7/mod.ts";
import { getEnv } from "./env.ts";
import contracts from "../../onchain-reference/plutus.json" with { type: "json" };

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


// const response = await getAssetsTransactions("2b29ff2309668a2e58d96da26bd0e1c0dd4013e5853e96df2be27e42001f4d70526f79616c7479")
// const response = await getRoyaltyPolicy("60a75923cfc6e241b5da7fd6328d8846275ce94c15fcfc903538e012")

const response = await testTimelockedMint(lucid, timelockedMP, alwaysFails, walletAddress)

console.log(response)

// these are examples of constructing transactions from the frontend. 

export async function testTimelockedMint(lucid: Lucid, mp: Script, validator: Script, walletAddress: string) {

  // configuration - these would come from user input. Adjust these however you wish.
  const mock_image = "ipfs://QmeTkA5bY4P3DUjhdtPc2MsT8G8keb7HAxjccKrLJN2xTz"
  const mock_name = "test"
  const mock_deadline = new Date("2024-12-31T23:59:59Z").getTime()
  const mock_size = 5
  const mock_fee = 625 // 10 / 0.016

  // parameterize minting policy
	const parameterized_mp = createTimelockedMP(lucid, mp.script, mock_deadline, walletAddress);

  // define media assets for each nft
	let assets: MediaAssets = {}
	for(let i = 0; i < mock_size; i++) {
		let tempdetails = {
			name: mock_name + i,
			image: mock_image
			};
		assets[mock_name + i] = tempdetails
	}

  // define royalty policy
	const royalties: RoyaltyRecipient[] = [{
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