---
CIP: 71
Title: Non-Fungible Token (NFT) Proxy Voting Standard
Status: Proposed
Category: Tools
Authors:
  - Thaddeus Diamond <support@wildtangz.com>
Implementors: []
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/351
Created: 2022-10-11
License: CC-BY-4.0
---

## Abstract

This proposal uses plutus minting policies to create valid "ballots" that are sent alongside datum "votes" to a centralized smart contract "ballot box" in order to perform verifiable on-chain voting in NFT projects that do not have a governance token.

## Motivation: why is this CIP necessary?

This proposal is intended to provide a standard mechanism for non-fungible token (NFT) projects to perform on-chain verifiable votes using only their NFT assets. There are several proposed solutions for governance that involve using either a service provider (e.g., Summon) with native assets or the issuance of proprietary native assets.  However, there are several issues with these approaches:
- Airdrops of governance tokens require minUTxO ada attached, costing the NFT project ada out of pocket
- Fungible tokens do not have a 1:1 mechanism for tracking votes against specific assets with voting power
- Sale of the underlying NFT is not tied to sale of the governance token, creating separate asset classes and leaving voting power potentially with those who are no longer holders of the NFT

This standard provides a simple solution for this by using the underlying NFT to mint a one-time "ballot" token that can be used only for a specific voting topic. Projects that adopt this standard will be able to integrate with web viewers that track projects' governance votes and will also receive the benefits of verifiable on-chain voting without requiring issuance of a new native token.

We anticipate some potential use cases:
- Enforcing an exact 1:1 vote based on a user's existing NFT project holdings
- Enforcing vote validity by rejecting invalid vote options (e.g., disallowing write-ins)
- Creating "super-votes" based on an NFT serial number (e.g., rare NFTs in the 9,000-10,000 serial range get 2x votes)

> **Warning**
> This specification is not intended for for governance against fungible tokens that cannot be labeled individually.

## Specification

### A Simple Analogy

The basic analogy here is that of a traditional state or federal vote.  Imagine a citizen who has a state ID (e.g., Driver's License) and wants to vote, as well as a central voting authority that counts all the ballots.
1. Citizens go to to a precinct and show their ID to the appropriate authority
2. Citizens receive a ballot with choices for the current vote
3. Citizens mark their selections on the ballot
4. Citizens sign their ballot with their name
5. Citizens submit their ballot into a single "ballot box"
6. Central voting authorities process the vote after polls close
7. Citizens await the election results through a trusted news outlet

This specification follows the same process, but using tokens:
1. A holder of a project validates their NFT by sending it to self
2. The holder signs a Plutus minting policy to create a "ballot" NFT linked to their unique NFT
3. The holder marks their desired vote selections on the ballot
4. The holder signs a tx that sends the "ballot" NFT to a "ballot box" (smart contract) with their "vote" (datum)
5. Authorized vote counting wallets process UTxOs and their datums in the "ballot box" smart contract after polls close
6. Authorized vote counters report the results in a human-readable off-chain format to holders

> **Note**
> Because of the efficient UTxO model Cardano employs, steps #1 through #4 occur in a single transaction.

### The Vote Casting Process

#### "Ballot" -> Plutus Minting Policy

Every holder that participates in the vote will have their project NFT in a wallet that can be spent from (either hardware or software, typically accessed via [CIP-30](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030)).  To create a ballot, the voting authority will create a Plutus minting policy with a specific combination of:

```ts
type BallotMintingPolicy = {
  referencePolicyId: MintingPolicyHash,             // Reference policy ID of the original NFT project
  pollsClose: Time,                                 // Polls close (as a Unix timestamp in milliseconds)
  assetNameMapping: func(ByteArray) -> ByteArray    // Some function (potentially identity) to map reference NFT name 1-for-1 to ballot NFT name
};
```

This Plutus minting policy will perform the following checks:
1. Polls are still open during the Tx validFrom/validTo interval
2. The ballot NFTs were validly minted (at the least, the user sent-to-self the reference assets and the vote weight/choices are correct)
3. The minted assets are sent directly to the ballot box smart contract in the minting transaction (see [the potential attack below](#Creation-of-Ballot-Without-Casting-a-Vote))

For the voter, each vote they wish to cast will require creating a separate "ballot" NFT.  In the process, their reference NFT never leaves the original wallet.  Sample [Helios language](https://github.com/Hyperion-BT/Helios) pseudocode (functions elided for space) is as follows:

```ts
func main(redeemer: Redeemer, ctx: ScriptContext) -> Bool {
  tx: Tx = ctx.tx;
  minted_policy: MintingPolicyHash = ctx.get_current_minting_policy_hash();
  redeemer.switch {
    Mint => {
      polls_are_still_open(tx.time_range)
        && ballots_are_validly_minted(tx.minted, minted_policy, tx.outputs)
        && assets_locked_in_ballot_box(tx, tx.minted)
    },
    // Burn code elided for space...
  }
}
```

> **Note**
> `ballots_are_validly_minted()` includes all required and custom checks (e.g., the holder has sent the reference NFT to themselves in `tx.outputs`) to validate newly minted ballots

#### "Vote" -> eUTxO Datum

To cast the vote, the user sends the ballot NFT just created to a "ballot box".  Note that for reasons specified in [the "attacks" section below](#Creation-of-Ballot-Without-Casting-a-Vote) this needs to occur during the same transaction that the ballot was minted in.

The datum is a simple object representing the voter who cast the vote and the vote itself:

```ts
type VoteDatum = {
  voter: PubKeyHash,
  vote: object
};
```

The `voter` element is extremely important in this datum so that we know who minted the ballot NFT and who we should return it to.  At the end of the ballot counting process, this user will receive their ballot NFT back.

Note that we are trying to avoid being overly prescriptive here with the specific vote type as we want the only limitations on the vote type to be those imposed by Cardano.  Further iterations of this standard should discuss the potential for how to implement ranked-choice voting (RCV) inside of this `vote` object, support multiple-choice vote selection, and more.

#### "Ballot Box" -> Smart Contract

Essentially, the "ballot box" is a smart contract with arbitrary logic decided upon by the authorized vote counter.  Some examples include:

1. A ballot box that can be redeemed at any time by a tx signed by the authorized vote counter
2. A ballot box that can be redeemed only after polls close
3. A ballot box that can be redeemed once a majority of voters have sent in a ballot
4. A ballot box that can be redeemed only by the specific wallet specified in the `voter` datum of each UTxO
5. A ballot box that can be redeemed only after polls close, has to burn the ballots it redeems, and has to send the minUTxO back to the voter address

Because the ballot creation and vote casting process has already occurred on-chain we want to provide the maximum flexibility in the protocol here so that each project can decide what is best for their own community.  Helios code for the simple case enumerated as #1 above would be:

```ts
const EXPECTED_SIGNER: PubKeyHash = PubKeyHash::new(#0123456789abcdef)

func main(ctx: ScriptContext) -> Bool {
  ctx.tx.is_signed_by(EXPECTED_SIGNER)
}
```

### The Vote Counting Process

#### "Ballot Counter" -> Authorized Wallet

Given the flexible nature of the ["ballot box" smart contract](#Ballot-Box---Smart-Contract) enumerated above, we propose a simple algorithm for counting votes and returning the ballots to the user:

1. Ensure the polls are closed (can be either on or off-chain)
2. Iterate through all UTxOs in forward-time-order locked in the "ballot box" and for each:
	* Determine which assets are inside of that UTxO
	* Mark their most recent vote to match the `vote` object in the UTxOs datum
3. Ensure any required quorums or thresholds were reached
4. Report on the final ballot outcome

Javascript-like pseudocode using the [Lucid library](https://github.com/spacebudz/lucid) for the above algorithm would be as follows:

```js
function countVotes(ballotPolicyId, ballotBox) {
  var votesByAsset = {};
  const votes = await lucid.utxosAt(ballotBox);
  for (const vote of votes) {
    const voteResult = Data.toJson(Data.from(vote.datum));
    for (const unit in vote.assets) {
      if (!unit.startsWith(ballotPolicyId)) {
        continue;
      }
      const voteCount = Number(vote.assets[unit]);         // Should always be 1
      votesByAsset[unit] = {
        voter: voteResult.voter,
        vote: voteResult.vote,
        count: voteCount
      }
    }
  }
  return votesByAsset;
}
```

There is no requirement that the "ballot counter" redeem all "ballots" from the "ballot box" and send them back to the respective voters, but we anticipate that this is what will happen in practice.  We encourage further open-sourced code versions that enforce this requirement at the smart contract level.

### Reclaiming Ada Locked by the Ballot NFTs

Even if the ballot NFT is returned to the user, this will leave users with ada locked alongside these newly created assets, which can impose a financial hardship for certain project users.

We can add burn-specific code to our Plutus minting policy so that ballot creation does not impose a major financial burden on users:

```ts
func main(redeemer: Redeemer, ctx: ScriptContext) -> Bool {
  tx: Tx = ctx.tx;
  minted_policy: MintingPolicyHash = ctx.get_current_minting_policy_hash();
  redeemer.switch {
    // Minting code elided for space...
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
```

The Helios code above simply checks that during a burn (as indicated by the Plutus minting policy's `redeemer`), the user is not attempting to mint a positive number of any assets.  With this code, *any Cardano wallet* can burn *any ballot* minted as part of this protocol.  Why so permissive? We want to ensure that each vote is bringing the minimal costs possible to the user.  In providing this native burning mechanism we can free up the minUTxO that had been locked with the ballot, and enable the user to potentially participate in more votes they might not have otherwise.  In addition, users who really do not like the specific commemorative NFTs or projects that choose to skip the "commemorative" aspect of ballot creation now have an easy way to dispose of "junk" assets.

## Rationale: how does this CIP achieve its goals?

### Using Inline Datums (On-Chain) Instead of Metadata (Off-Chain)

There are several existing open-source protocols (e.g., [VoteAire](https://github.com/voteaire/voteaire-onchain-spec)) that use metadata to record votes in Cardano transactions without requiring any additional minting or smart contracts.  However, since the vote counting occurs off-chain by validating metadata the vote counter is the ultimate arbiter of what is a "valid" vote.  In this specification, the validity of the vote is ensured in the Ballot creation process, so that any vote in the ballot box is guaranteed to be valid.  We strongly believe that moving the entire process into flexible on-chain logic will improve the transparency of the voting process and meet the needs of the use cases discussed in ["Motivation"](#Motivation) and ["Ballot Box"](#Ballot-Box---Smart-Contract).

### Commemorative NFTs with Optional Token Burning

There is a question as to whether we should enforce the requirement that votes be burned when they are counted by the vote counter.  However, we do not want that to be a standard as many users of NFT communities have expressed an interest in receiving commemorative NFTs (similar to an "I Voted" sticker).  Instead, we propose that the ballot Plutus minting policy be burn-able by anyone who holds the NFT in their wallet.  This way, locked ada can be reclaimed if the user has no further use for the commemorative NFT (see an example of this in the [Implementation](./example/)).

### Potential Attacks and Mitigations

#### Creation of Ballot Without Casting a Vote

Imagine a user who decides to create ballots for the current vote, but not actually cast the vote by sending it to the ballot box.  According to checks #1 and #2 in [the Plutus Minting Policy](#Ballot---Plutus-Minting-Policy), this would be possible.  After the ballot was created, the user could sell the reference NFT and wait until just before the polls close to surreptitiously cast a vote over the wishes of the new project owner.  Check #3 in the minting policy during the mint transaction itself prevents this attack.

#### Double Voting in Multiple Transactions

A user could wait until their first vote casting transaction completes, then create more ballots and resubmit to the ballot box.  The result would be the creation of more assets that count toward the ultimate vote.  However, Cardano helps us here by identifying tokens based on the concatenation of policy ID and asset identifier.  So long as the mapping function in the [Plutus minting policy for ballots](#Ballot---Plutus-Minting-Policy) is idempotent, each subsequent time the user votes the policy will create an additional fungible token with the same asset identifier.  Then, the ballot counter can ignore any prior votes based on each unique asset identifier to avoid duplicate votes (see ["'Ballot Counter' -> Authorized Wallet"](#Ballot-Counter---Authorized-Wallet)).

#### Double Creation of the Same Ballot

A user could attempt to create multiple ballots of the same name for a given reference NFT.  If the reference NFT is actually a fungible token and not an NFT, then our assumptions will have been broken and this is an unsupported use case.  But if our assumption that this is an NFT project are correct, then simply checking that the quantity minted is equal to the quantity spent inside of the Plutus minting policy will prevent this.  The [example code](./example/voting.js) attached does just that.

#### Returning the "Ballot" NFTs to the Wrong User

During the construction of the ballot NFTs we allow the user to specify their vote alongside a `voter` field indicating where their "ballot" NFT should be returned to once the vote is fully counted.  Unfortunately, this is not strictly checked inside the Plutus minting policy's code (largely due to CPU/memory constraints).  So, we rely on the user to provide an accurate return address, which means that there is the potential for someone who has not actually voted to receive a commemorative NFT.  This does not impact the protocol though, as the "ballot" NFT was legally minted, just returned to the incorrect location.  That user actually received a gift, as they can now burn the ballot and receive some small amount of dust.

### Potential Disadvantages

There are several potential disadvantages to this proposal that may be avoided by the use of a native token or other voting mechanism.  We enumerate some here explicitly so projects can understand where this protocol may or may not be appropriate to use:

- Projects concerned with token proliferation and confusing their user base with the creation of multiple new assets might want to avoid this standard as it requires one new token policy per vote/initiative
- Projects wishing to create a "secret ballot" that will not be revealed until after polls close should not use this because the datum votes appear on-chain (and typically inline)
  - Performing an encrypted vote on-chain with verifiable post-vote results is an exercise left to the standard's implementer
- Projects wishing for anonymity in their votes should not use this standard as each vote can be traced to a reference asset

### Optional Recommendations

In no particular order, we recommend the following implementation details that do not impact the protocol, but may impact user experience:

- The mapping function described in the [Plutus minting policy for ballots](#Ballot---Plutus-Minting-Policy) should likely be some sort of prefixing or suffixing (e.g., "Ballot #1 - <REFERENCE NFT>"), and NOT the identity function.  Although the asset will be different than the reference NFT due to its differing policy ID, users are likely to be confused when viewing these assets in a token viewer.
- The "ballot" NFT should have some sort of unique metadata (if using [CIP-25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025)), datum (if using [CIP-68](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068)) or other identification so that the users can engage with the ballot in a fun, exciting way and to ensure there is no confusion with the reference NFT.
- The "vote" represented by a datum will be easier to debug and analyze in real-time if it uses the new "inline datum" feature from Vasil, but the protocol will still work on Alonzo era transactions.
- The "ballot box" smart contract should likely enforce that the datum's "voter" field is respected when returning the ballots to users after voting has ended to provide greater transparency and trust for project participants.

### Backward Compatibility

Due to the nature of Plutus minting policies and smart contracts, which derive policy identifiers and payment addresses from the actual source code, once a vote has been started it cannot change versions or code implementations. However, because the mechanism we propose here is just a reference architecture, between votes projects are free to change either the "ballot" Plutus minting policy or the "ballot box" smart contract as they see fit.  There are no prior CIPs with which to conform with for backward interoperability.

### References

- [CIP-0025](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025): NFT Metadata Standard
- [CIP-0030](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0030): Cardano dApp-Wallet Web Bridge
- [CIP-0068](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0068): Datum Metadata Standard
- [Helios Language](https://github.com/Hyperion-BT/Helios): On-Chain Cardano Smart Contract language used in example code
- [Lucid](https://github.com/spacebudz/lucid): Transaction construction library used in code samples and pseudocode
- [VoteAire Specification](https://github.com/voteaire/voteaire-onchain-spec): Open-source voting specification using metadata off-chain

## Path to Active

### Acceptance Criteria

- [ ] Presentation to, and adoption by, projects that may benefit from ranked-choice voting
- [ ] Open-source implementations from other NFT projects that make use of this CIP

### Implementation Plan

- [x] Minimal reference implementation making use of [Lucid](https://github.com/spacebudz/lucid) (off-chain), [Plutus Core](https://github.com/input-output-hk/plutus) [using Helios](https://github.com/Hyperion-BT/Helios) (on-chain): [Implementation](./example/)

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
