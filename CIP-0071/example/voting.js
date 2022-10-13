import * as helios from '@hyperionbt/helios';

import {Data, fromHex, toHex, getAddressDetails} from 'lucid-cardano';

// These modules are imported from https://github.com/thaddeusdiamond/cardano-nft-mint-frontend
// but elided in the source code of the CIP for space
import * as CardanoDAppJs from '../third-party/cardano-dapp-js.js';
import * as LucidInst from '../third-party/lucid-inst.js';
import * as NftPolicy from "../nft-toolkit/nft-policy.js";
import {shortToast} from '../third-party/toastify-utils.js';
import {validate, validated} from '../nft-toolkit/utils.js';

const BURN_REDEEMER = 'd87a80';
const MAX_NFTS_TO_MINT = 20;
const MAX_ATTEMPTS = 12;
const OPTIMIZE_HELIOS = true;
const SINGLE_NFT = 1n;
const TEN_MINS = 600000;
const TXN_WAIT_TIMEOUT = 15000;

function getVoteCounterSourceCode(pubKeyHash) {
  return `
    spending vote_counter

    const EXPECTED_SIGNER: PubKeyHash = PubKeyHash::new(#${pubKeyHash})

    func main(ctx: ScriptContext) -> Bool {
      ctx.tx.is_signed_by(EXPECTED_SIGNER)
    }
  `;
}

function getBallotSourceCodeStr(referencePolicyId, pollsClose, pubKeyHash, ballotPrefix) {
  return `
    minting voting_ballot

    const BALLOT_BOX_PUBKEY: ValidatorHash = ValidatorHash::new(#${pubKeyHash})
    const BALLOT_NAME_PREFIX: ByteArray = #${ballotPrefix}
    const POLLS_CLOSE: Time = Time::new(${pollsClose})
    const REFERENCE_POLICY_HASH: MintingPolicyHash = MintingPolicyHash::new(#${referencePolicyId})

    enum Redeemer {
      Mint
      Burn
    }

    func assets_locked_in_script(tx: Tx, minted_assets: Value) -> Bool {
      //print(tx.value_sent_to(BALLOT_BOX_PUBKEY).serialize().show());
      //print(minted_assets.serialize().show());
      ballots_sent: Value = tx.value_locked_by(BALLOT_BOX_PUBKEY);
      assets_locked: Bool = ballots_sent.contains(minted_assets);
      if (assets_locked) {
        true
      } else {
        print("Minted ballots (" + minted_assets.serialize().show() + ") were not correctly locked in the script: " + ballots_sent.serialize().show());
        false
      }
    }

    func assets_were_spent(minted: Value, policy: MintingPolicyHash, outputs: []TxOutput) -> Bool {
      minted_assets: Map[ByteArray]Int = minted.get_policy(policy);
      reference_assets_names: Map[ByteArray]Int = minted_assets.map_keys((asset_id: ByteArray) -> ByteArray {
        asset_id.slice(BALLOT_NAME_PREFIX.length, asset_id.length)
      });
      reference_assets: Map[MintingPolicyHash]Map[ByteArray]Int = Map[MintingPolicyHash]Map[ByteArray]Int {
        REFERENCE_POLICY_HASH: reference_assets_names
      };
      tx_sends_to_self: Bool = outputs.head.value.contains(Value::from_map(reference_assets));
      if (tx_sends_to_self) {
        true
      } else {
        print("The NFTs with voting power (" + REFERENCE_POLICY_HASH.serialize().show() + ") for the ballots were never sent-to-self");
        false
      }
    }

    func polls_are_still_open(time_range: TimeRange) -> Bool {
      tx_during_polls_open: Bool = time_range.is_before(POLLS_CLOSE);
      if (tx_during_polls_open) {
        true
      } else {
        print("Invalid time range: " + time_range.serialize().show() + " (polls close at " + POLLS_CLOSE.serialize().show() + ")");
        false
      }
    }

    func main(redeemer: Redeemer, ctx: ScriptContext) -> Bool {
      tx: Tx = ctx.tx;
      minted_policy: MintingPolicyHash = ctx.get_current_minting_policy_hash();
      redeemer.switch {
        Mint => {
          polls_are_still_open(tx.time_range)
            && assets_were_spent(tx.minted, minted_policy, tx.outputs)
            && assets_locked_in_script(tx, tx.minted)
        },
        Burn => {
          tx.minted.get_policy(minted_policy).all((asset_id: ByteArray, amount: Int) -> Bool {
            if (amount > 0) {
              print(asset_id.show() + " asset ID was minted not burned (quantity " + amount.show() + ")");
              false
            } else {
              true
            }
          })
        }
      }
    }
  `;
}

function getCompiledCode(mintingSourceCode) {
  return helios.Program.new(mintingSourceCode).compile(OPTIMIZE_HELIOS);
}

function getLucidScript(compiledCode) {
  return {
    type: "PlutusV2",
    script: JSON.parse(compiledCode.serialize()).cborHex
  }
}

function getBallotSelection(ballotDomName) {
  return document.querySelector(`input[name=${ballotDomName}]:checked`)?.value;
}

async function waitForTxn(lucid, blockfrostKey, txHash) {
  for (var attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    const result = await fetch(`${lucid.provider.data.url}/txs/${txHash}`, {
      headers: { project_id: blockfrostKey }
    }).then(res => res.json());
    if (result && !result.error) {
      return;
    }

    if (attempt < (MAX_ATTEMPTS - 1)) {
      await new Promise(resolve => setTimeout(resolve, TXN_WAIT_TIMEOUT));
    }
  }
  throw `Could not retrieve voting txn after ${MAX_ATTEMPTS} attempts`;
}


export async function mintBallot(blockfrostKey, pubKeyHash, policyId, pollsClose, ballotDomName, ballotPrefix, ballotMetadata) {
  try {
    const cardanoDApp = CardanoDAppJs.getCardanoDAppInstance();
    validate(cardanoDApp.isWalletConnected(), 'Please connect a wallet before voting using "Connect Wallet" button');
    const wallet = await cardanoDApp.getConnectedWallet();

    const lucid = validated(await LucidInst.getLucidInstance(blockfrostKey), 'Please validate that your wallet is on the correct network');
    lucid.selectWallet(wallet);
    const voter = await lucid.wallet.address();

    const voteCounterSourceCode = getVoteCounterSourceCode(pubKeyHash);
    const voteCounterCompiledCode = getCompiledCode(voteCounterSourceCode);
    const voteCounterScript = getLucidScript(voteCounterCompiledCode)
    const voteCounter = lucid.utils.validatorToAddress(voteCounterScript);
    const voteCounterPkh = getAddressDetails(voteCounter).paymentCredential.hash;

    const ballotPrefixHex = toHex(new TextEncoder().encode(ballotPrefix));
    const mintingSourceCode = getBallotSourceCodeStr(policyId, pollsClose, voteCounterPkh, ballotPrefixHex);
    const mintingCompiledCode = getCompiledCode(mintingSourceCode);
    const voteMintingPolicy = getLucidScript(mintingCompiledCode);
    const voteMintingPolicyId = mintingCompiledCode.mintingPolicyHash.hex;

    const vote = validated(getBallotSelection(ballotDomName), 'Please select your ballot choice!');
    const voteDatum = {
      inline: Data.to(Data.fromJson({ voter: voter, vote: vote }))
    };

    const votingAssets = await getVotingAssets([policyId], [], lucid);
    const assetIds = Object.keys(votingAssets.assets);
    var assetIdsChunked = [];
    for (var i = 0; i < assetIds.length; i += MAX_NFTS_TO_MINT) {
      assetIdsChunked.push(assetIds.slice(i, i + MAX_NFTS_TO_MINT));
    }
    if (assetIdsChunked.length > 1) {
      validate(
        confirm(`We will have to split your votes into ${assetIdsChunked.length} different transactions due to blockchain size limits, should we proceed?`),
        "Did not agree to submit multiple voting transactions"
      );
    }

    for (var i = 0; i < assetIdsChunked.length; i++) {
      var mintAssets = {};
      var referenceAssets = {};
      var mintingMetadata = { [voteMintingPolicyId]: {}, version: NftPolicy.CIP0025_VERSION }
      for (const assetId of assetIdsChunked[i]) {
        const assetName = assetId.slice(56);
        const ballotNameHex = `${ballotPrefixHex}${assetName}`;
        const ballotName = new TextDecoder().decode(fromHex(ballotNameHex));
        mintAssets[`${voteMintingPolicyId}${ballotNameHex}`] = SINGLE_NFT;
        referenceAssets[`${policyId}${assetName}`] = SINGLE_NFT;
        mintingMetadata[voteMintingPolicyId][ballotName] = Object.assign({}, ballotMetadata);
        mintingMetadata[voteMintingPolicyId][ballotName].name = ballotName;
        mintingMetadata[voteMintingPolicyId][ballotName].vote = vote;
      }

      const txBuilder = lucid.newTx()
                             .addSigner(voter)
                             .mintAssets(mintAssets, Data.empty())
                             .attachMintingPolicy(voteMintingPolicy)
                             .attachMetadata(NftPolicy.METADATA_KEY, mintingMetadata)
                             .payToAddress(voter, referenceAssets)
                             .payToContract(voteCounter, voteDatum, mintAssets)
                             .validTo(new Date().getTime() + TEN_MINS);

      const txComplete = await txBuilder.complete({ nativeUplc: false });
      const txSigned = await txComplete.sign().complete();
      const txHash = await txSigned.submit();
      shortToast(`[${i + 1}/${assetIdsChunked.length}] Successfully voted in Tx ${txHash}`);
      if (i < (assetIdsChunked.length - 1)) {
        shortToast('Waiting for prior transaction to finish, please wait for pop-ups to complete your vote!');
        await waitForTxn(lucid, blockfrostKey, txHash);
      } else {
        shortToast('Your vote(s) have been successfully recorded!');
      }
    }
    return true;
  } catch (err) {
    shortToast(JSON.stringify(err));
  }
  return false;
}

async function getVotingAssets(votingPolicies, exclusions, lucid) {
  if (votingPolicies === undefined || votingPolicies === []) {
    return {};
  }
  const votingAssets = {};
  const utxos = [];
  for (const utxo of await lucid.wallet.getUtxos()) {
    var found = false;
    for (const assetName in utxo.assets) {
      if (!votingPolicies.includes(assetName.slice(0, 56))) {
        continue;
      }
      if (exclusions.includes(assetName)) {
        continue;
      }
      if (votingAssets[assetName] === undefined) {
        votingAssets[assetName] = 0n;
      }
      votingAssets[assetName] += utxo.assets[assetName];
      found = true;
    }
    if (found) {
      utxos.push(utxo);
    }
  }
  return { assets: votingAssets, utxos: utxos };
}

async function walletVotingAssets(blockfrostKey, votingPolicies, exclusions) {
  var cardanoDApp = CardanoDAppJs.getCardanoDAppInstance();
  if (!cardanoDApp.isWalletConnected()) {
    return {};
  }

  try {
    const wallet = await cardanoDApp.getConnectedWallet();
    const lucidInst = validated(LucidInst.getLucidInstance(blockfrostKey), 'Unable to initialize Lucid, network mismatch detected');

    const lucid = validated(await lucidInst, 'Unable to initialize Lucid, network mismatch detected');
    lucid.selectWallet(wallet);
    return await getVotingAssets(votingPolicies, exclusions, lucid);
  } catch (err) {
    const msg = (typeof(err) === 'string') ? err : JSON.stringify(err);
    shortToast(`Voting power retrieval error occurred: ${msg}`);
    return {};
  }
}

export async function votingAssetsAvailable(blockfrostKey, votingPolicies, exclusions) {
  const votingAssets = await walletVotingAssets(blockfrostKey, votingPolicies, exclusions);
  if (votingAssets.assets) {
    const remainingVotingBigInt =
      Object.values(votingAssets.assets)
            .reduce((partialSum, a) => partialSum + a, 0n);
    return Number(remainingVotingBigInt);
  }
  return -1;
}

export async function countBallots(blockfrostKey, pubKeyHash, policyId, pollsClose, voteOutputDom, ballotPrefix) {
  try {
    const cardanoDApp = CardanoDAppJs.getCardanoDAppInstance();
    validate(cardanoDApp.isWalletConnected(), 'Please connect a wallet before voting using "Connect Wallet" button');
    const wallet = await cardanoDApp.getConnectedWallet();

    const lucid = validated(await LucidInst.getLucidInstance(blockfrostKey), 'Please validate that your wallet is on the correct network');
    lucid.selectWallet(wallet);
    const oracle = await lucid.wallet.address();

    const voteCounterSourceCode = getVoteCounterSourceCode(pubKeyHash);
    const voteCounterCompiledCode = getCompiledCode(voteCounterSourceCode);
    const voteCounterScript = getLucidScript(voteCounterCompiledCode)
    const voteCounter = lucid.utils.validatorToAddress(voteCounterScript);
    const voteCounterPkh = getAddressDetails(voteCounter).paymentCredential.hash;

    const ballotPrefixHex = toHex(new TextEncoder().encode(ballotPrefix));
    const mintingSourceCode = getBallotSourceCodeStr(policyId, pollsClose, voteCounterPkh, ballotPrefixHex);
    const mintingCompiledCode = getCompiledCode(mintingSourceCode);
    const mintingPolicyId = mintingCompiledCode.mintingPolicyHash.hex;

    var voteAssets = {};
    const votes = await lucid.utxosAt(voteCounter);
    for (const vote of votes) {
      const voteResult = Data.toJson(Data.from(vote.datum));
      for (const unit in vote.assets) {
        if (!unit.startsWith(mintingPolicyId)) {
          continue;
        }
        const voteCount = Number(vote.assets[unit]);
        voteAssets[unit] = {
          voter: voteResult.voter,
          vote: voteResult.vote,
          count: voteCount
        }
      }
    }

    const votePrinted = JSON.stringify(voteAssets, undefined, 4);
    document.getElementById(voteOutputDom).innerHTML =
     `<pre style="text-align: start">${JSON.stringify(voteAssets, undefined, 4)}</pre>`;
    return votePrinted;
  } catch (err) {
    shortToast(JSON.stringify(err));
  }
}

export async function redeemBallots(blockfrostKey, pubKeyHash, policyId, pollsClose, voteOutputDom, ballotPrefix) {
  try {
    const cardanoDApp = CardanoDAppJs.getCardanoDAppInstance();
    validate(cardanoDApp.isWalletConnected(), 'Please connect a wallet before voting using "Connect Wallet" button');
    const wallet = await cardanoDApp.getConnectedWallet();

    const lucid = validated(await LucidInst.getLucidInstance(blockfrostKey), 'Please validate that your wallet is on the correct network');
    lucid.selectWallet(wallet);
    const oracle = await lucid.wallet.address();

    const voteCounterSourceCode = getVoteCounterSourceCode(pubKeyHash);
    const voteCounterCompiledCode = getCompiledCode(voteCounterSourceCode);
    const voteCounterScript = getLucidScript(voteCounterCompiledCode)
    const voteCounter = lucid.utils.validatorToAddress(voteCounterScript);
    const voteCounterPkh = getAddressDetails(voteCounter).paymentCredential.hash;

    const ballotPrefixHex = toHex(new TextEncoder().encode(ballotPrefix));
    const mintingSourceCode = getBallotSourceCodeStr(policyId, pollsClose, voteCounterPkh, ballotPrefixHex);
    const mintingCompiledCode = getCompiledCode(mintingSourceCode);
    const mintingPolicyId = mintingCompiledCode.mintingPolicyHash.hex;

    var voterRepayments = {};
    const votesToCollect = [];
    const votes = await lucid.utxosAt(voteCounter);
    for (const vote of votes) {
      const voteResult = Data.toJson(Data.from(vote.datum));
      var hasVote = false;
      for (const unit in vote.assets) {
        if (!unit.startsWith(mintingPolicyId)) {
          continue;
        }
        hasVote = true;
        const voteCount = Number(vote.assets[unit]);
        if (!(voteResult.voter in voterRepayments)) {
          voterRepayments[voteResult.voter] = {}
        }
        voterRepayments[voteResult.voter][unit] = voteCount;
      }

      if (hasVote) {
        votesToCollect.push(vote);
      }
    }

    const txBuilder = lucid.newTx()
                           .addSigner(oracle)
                           .collectFrom(votesToCollect, Data.empty())
                           .attachSpendingValidator(voteCounterScript);
    for (const voter in voterRepayments) {
      txBuilder.payToAddress(voter, voterRepayments[voter]);
    }
    const txComplete = await txBuilder.complete({ nativeUplc: false });
    const txSigned = await txComplete.sign().complete();
    const txHash = await txSigned.submit();
    shortToast(`Successfully counted ballots in ${txHash}`);
  } catch (err) {
    shortToast(JSON.stringify(err));
  }
}

export async function burnBallots(blockfrostKey, pubKeyHash, policyId, pollsClose, ballotPrefix) {
  try {
    const cardanoDApp = CardanoDAppJs.getCardanoDAppInstance();
    validate(cardanoDApp.isWalletConnected(), 'Please connect a wallet before voting using "Connect Wallet" button');
    const wallet = await cardanoDApp.getConnectedWallet();

    const lucid = validated(await LucidInst.getLucidInstance(blockfrostKey), 'Please validate that your wallet is on the correct network');
    lucid.selectWallet(wallet);
    const voter = await lucid.wallet.address();

    const voteCounterSourceCode = getVoteCounterSourceCode(pubKeyHash);
    const voteCounterCompiledCode = getCompiledCode(voteCounterSourceCode);
    const voteCounterScript = getLucidScript(voteCounterCompiledCode)
    const voteCounter = lucid.utils.validatorToAddress(voteCounterScript);
    const voteCounterPkh = getAddressDetails(voteCounter).paymentCredential.hash;

    const ballotPrefixHex = toHex(new TextEncoder().encode(ballotPrefix));
    const mintingSourceCode = getBallotSourceCodeStr(policyId, pollsClose, voteCounterPkh, ballotPrefixHex);
    const mintingCompiledCode = getCompiledCode(mintingSourceCode);
    const mintingPolicy = getLucidScript(mintingCompiledCode);
    const mintingPolicyId = mintingCompiledCode.mintingPolicyHash.hex;

    const utxos = await lucid.wallet.getUtxos();
    const utxosToCollect = [];
    const mintAssets = {};
    var hasAlerted = false;
    for (const utxo of utxos) {
      var foundAsset = false;
      for (const unit in utxo.assets) {
        if (unit.startsWith(mintingPolicyId)) {
          if (Object.keys(mintAssets).length >= MAX_NFTS_TO_MINT) {
            if (!hasAlerted) {
              alert(`Can only burn ${MAX_NFTS_TO_MINT} ballots to burn at a time.  Start with that, then click this button again.`);
              hasAlerted = true;
            }
            break;
          }
          foundAsset = true;
          if (!(unit in mintAssets)) {
            mintAssets[unit] = 0n;
          }
          mintAssets[unit] -= utxo.assets[unit];
        }
      }

      if (foundAsset) {
        utxosToCollect.push(utxo);
      }
    }

    const txBuilder = lucid.newTx()
                           .addSigner(voter)
                           .collectFrom(utxosToCollect)
                           .mintAssets(mintAssets, BURN_REDEEMER)
                           .attachMintingPolicy(mintingPolicy)
                           .validTo(new Date().getTime() + TEN_MINS);
    const txComplete = await txBuilder.complete({ nativeUplc: false });
    const txSigned = await txComplete.sign().complete();
    const txHash = await txSigned.submit();
    shortToast(`Successfully burned your ballots in ${txHash}`);
  } catch (err) {
    shortToast(JSON.stringify(err));
  }
}
