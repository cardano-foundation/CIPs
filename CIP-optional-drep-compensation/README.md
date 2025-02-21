---
CIP: CIP-DRep-Comp
Title: Optional DRep Compensation
Category: Metadata
Status: Proposed
Authors:
    - Philip DiSarro <info@anastasialabs.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/991
Created: 2025-02-19
License: CC-BY-4.0
---

## Abstract
<!-- A short (\~200 word) description of the proposed solution and the technical issue being addressed. -->
We propose an opt-in standard for DRep compensation that does not require any changes to the ledger. When delegating to a DRep a user can opt-in to donate a percentage of their staking rewards to their DRep. 

## Motivation: why is this CIP necessary?
Introducing DRep compensation into the ledger will be a an absolutely massive undertaking, that will involve a large amount of engineering hours and a non-trivial price-tag. Also, the community has not yet reached consensus on whether DRep compensation is even desirable, or should be mandatory, or what the compensation scheme would even look like.

The best way to approach feature development is to release an MVP, evaluate its reception in the market, and use that data to determine the best way to proceed. This also allows us to introduce the feature without imposing it on anyone, it is opt-in, if you do not wish to compensate your DRep you can simply not opt-in. If, at any time, you wish to adjust the percentage of rewards that you are donating to your DRep you can just issue a new delegation certificate and adjust the amount or opt-out entirely.

## Specification

When tool or wallet builds a DRep vote delegation transaction (any transaction containing a `vote_deleg_cert`, `stake_vote_deleg_cert`, `vote_reg_deleg_cert` or `stake_vote_reg_deleg_cert ` certificate), the user should receive a prompt asking if they want to donate a percentage of their staking rewards to that DRep (i.e. if they want to opt-in to compensate their DRep).

If they choose to opt-in, they enter the percentage of their staking rewards that they would like their DRep to receive. The DRep delegation transaction will include that percentage in the transaction metadata, with metadatum label `3692`, in   the following format:

```json
{
    "3692": {
        "donationPercentage": PERCENTAGE_INTEGER_HERE 
    }
}
```
Where the integer stored in the metadata is the thousandths place in the decimal so 1 would convey that the user is electing to donate 0.01% of their staking rewards to their DRep. This value should be obtained directly from the percentage the user described in the prompt (ie. the user put 0.5% in the prompt then the integer in the metadata would be 5).

When a user claims their staking rewards, their wallet will look up their delegation transaction and determine if they have opted-in to compensate their DRep (by checking the tx metadata). If metadata in the format described above is found, then the wallet will add an additional output to the reward withdrawal transaction that sends the intended percentage of their rewards to their DRep. If there is not enough ada in their reward balance to produce a output which satisfies minimum `lovelacePerUTxOWord`, the wallet will convey this to the user and let them decide how to proceed (or the user can establish how to handle this via wallet settings). 

## Rationale: how does this CIP achieve its goals?
There is little community consensus regarding the topic of DRep delegation, it is a very controversial topic that people on both sides feel very passionate about. 

Great features are the result of endless iteration, the first release is never perfect. We cannot have a meaningful discussion on the impact (both positive and negative) and desirability of DRep compensation without any concrete data from which we can draw conclusions. This implementation was designed to embody the philosophy of rapid feedback based iteration. It is extremely simple to implement and bring to production. This proposal was designed to be favorable to everyone regardless on whether or not they support DRep delegation as it is entirely optional and thus can be entirely ignored by those who do not want to engage with it; furthermore, unlike other solutions, it doesn't involve any changes to the ledger that would have an ecosystem wide impact. 

## Path to Active

### Acceptance Criteria
- [ ] One major wallet supports this standard.
- [ ] Gov-tools supports this standard.

### Implementation Plan

- [ ] Gov-tools to implement the changes required to support this standard in their UI and backend.
- [ ] Lace to implement required DRep delegation metadata queries and construct payouts accordingly.

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). 
