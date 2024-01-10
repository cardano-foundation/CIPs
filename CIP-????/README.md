---
CIP: 127?
Title: Dynamic Asset Resale Fee Standard
Status: Proposed
Category: Tokens
Authors:
  - Brock <brockcruess@gmail.com>
Implementors: N/A
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/116
Created: 2024-01-09
License: CC-BY-4.0
---

## Abstract

This proposed standard will serve as a more functional alternative to [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027), allowing resale fee (previously incorrectly referred to as "royalty") information to be updated at any time - natively for unlocked policies, or referenced by [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088) for a locked policy. This proposed standard will also allow for multiple fee rates and output destinations to be built into resale transactions. This proposal is essentially a rewrite of [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) to maintain similar structure and easy comparison, so some of the wording/formatting is courtesy of the [CIP-0027 Authors](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) but is likely modified to highlight the differences between [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) and this proposed CIP.

## Motivation: Why is this CIP necessary?

[CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) provides great groundwork for resale fee functionality, but lacks support for updating fee rates/destination addresses, and also lacks support for multiple fee outputs. Projects may choose to maintain multiple wallets and split resale fees between them. DAOs may want to to govern their own asset collection's resale fee rates and their fee destinations. A use-case example would be a digital collectible project that wants to charge resale fees of 4% to a DAO wallet and 1% to a core team wallet. Another example would be an artist who wants to, just for the next 30 days, send all resale fees of their minted assets to a charity wallet, and decrease their policy's fee rate during that time as well. Because this new standard changes two features of [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027), it is being proposed as a new CIP rather than as an update to [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027).

## Specification

- A new tag of 778 is proposed for this implementation. The 778 tag compliments [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027)'s 777 tag.
- Any unlocked policy can write initial or updated resale fees tags to a new token.
- The resale fees tags are to be written to an unnamed token, using the policy to be used for the intended Cardano Assets.
- The latest minted set of instructions will always be honored. This allows a Cardano Asset maker to change the resale fees at a future date.
- Within this created asset will be the metadata for resale fees distributions.  It will use a tag of 778, and then have two or more tags to identify the percentages of future sales requested as resale fees, and the payment addresses to forward those resale fees to. The first set of two tags will be "rate" and "addr". Any additional tag sets will repeat after the first set of two tags, starting with "rate2" and "addr2", with sequentially increasing numbers for each added set.
- The "rate*" key tags can be any floating point value from 0.0 to 1.0, to represent between 0 and 100 percent. For example, a 12.5 percent resale fee would be represented with "rate": "0.125".
- The "addr*" key tags can be string values, or an array. It is to include a single payment address. By allowing for an array, the payment address can exceed the per line 64 character limitation. This payment address could be part of a smart contract, which should allow for greater flexibility of resale fees distributions, controlled by the asset creator.
- It is encouraged to burn the 778 token after minting, so that it does not add to the total asset count of the policy.
- When referenced by [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088), the [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088) registration information will take priority over any previously minted CIP-0127 tags, allowing for resale fee information to be updated even after the minting policy has locked.


### Example JSON with string

```
{
	"778": {
		"rate": "0.025",
		"addr": "addr1v9nevxg9wunfck0gt7hpxuy0elnqygglme3u6l3nn5q5gnq5dc9un",
     		"rate2": "0.015",
		"addr2": "addr1h2ahhsh2jajhsr4aj6jsajk2ahjaqbxnam1s892as3s1js6qx9kw",
     		"rate3": "0.01",
		"addr3": "addr1j6gqjsy6xgzjye7hq8hksuw1mylqmuqjsq7j182je9h2kn7ah5aj"
	}
}
```

### Example JSON with array

```
{
	"778": {
		"rate": "0.025",
		"addr": [
			"addr1qysvslfjdx6f6s7ddhmhvqhutqpl2xwc8f46apwxmxl3l8snpwar4x0nqul",
			"j5egg2puhn4w9s7tfawxs7568gr8sa3tqtxrrln"
		],
  		"rate2": "0.015",
		"addr2": [
			"addr1q8ykglpxv9ra4vzhccu094xx5v7cnpr7ew2n43cgxpf4myqnpwar4x0nqul",
			"j5egg2puhn4w9s7tfawxs7568gr8sa3tqen5vkl"
		]
	}
}
```

### Process Flow

**Initial Process:**
1) Create policy for planned assets.
2) Mint no name token with community standard resale fees metadata.
3) Burn no name token to free up UTxO (recommended, but not required).
4) Mint planned assets using this same policy.

**Update Process (only if policy remains unlocked):**
1) Mint new no name token with community standard resale fees metadata under the same policy as the initial process.
2) Burn new no name token to free up UTxO (recommended, but not required).

## Rationale: How does this CIP achieve its goals?

By creating a new tag for the distinct purpose of providing an updatable and expandable option for resale fee distribution, Cardano Asset makers and Marketplaces can uniformly apply resale fees to assets with predictable results.

By creating an updatable, expandable alternative to [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027), Cardano Asset makers can get creative with resale fee structures. For example, setting higher resale fees during the initial mint event of a new digital collectible asset collection, then lowering the fees gradually after minting is completed, which fights off the classic "mint and floor" issue that most collections face during mint.

This renewed standard on its own is as simple as [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) so it is easy to adopt.

When referenced by [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088), resale fees can be forever updatable, even after the minting policy of the Cardano Assets has locked. This is also true with [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) when referenced by [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088), however [CIP-0027](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0027) still lacks support for multiple resale fee outputs.

## Path to Active

### Acceptance Criteria

- [ ] Support of resale fee distribution according to this standard by multiple significant marketplaces.

### Implementation Plan

- [ ] Referenced for use under [CIP-0088](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0088), enabling this standard's true long-term functionality for locked policies.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
