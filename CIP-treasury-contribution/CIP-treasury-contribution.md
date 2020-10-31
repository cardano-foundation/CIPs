---
CIP: ?
Title: Treasury fraction on actual distributed rewards
Author: Federico Pasini <stakecool.io@gmail.com>,
        Antonio Caccese <csp@capitalstakepool.info>,
        Piero Zanetti <lordwotton29@pm.me>
Discussions-To: 
Comments-Summary: 
Comments-URI: 
Status: Standards track
Type: Process
Created: 2020-10-31
License: CC-BY-4.0
Post-History: https://forum.cardano.org/t/double-treasury-taxation-of-40-and-possible-workarounds/41461 and https://forum.cardano.org/t/cip-treasury-fraction-on-actual-distributed-rewards/41697
---

## Summary

Application of Treasury fraction (tau parameter) to actual distributed rewards instead of the whole epoch reward pot

## Abstract

Applying the treasury fraction calculation to the actual distributed rewards instead of the epoch reward pot will garantee as certain the part of reserve that will flow to the treasury, increasing the trasparency of the reward mechanism. 

## Motivation

At the time of the Shelley mainnet launch it has been decided that unclaimed rewards flow back to the reserve instead of going to increase the treasury pot.
Given that this change is clearly a benefit for both delegators and pools it didn't solve the uncertainity of an estimation about the reserve quota that is and will be forwarded to the treasury pot.
The reason is that the treasury quota is currently influenced by other factors like, for example, the total active stake and the pool pledge / pool saturation point ratio in relation with the value of a0 parameter.
In case of lower-than-100% active staking participation and/or lower-than-saturation-point average pool pledging the quota of reserve that will flow to treasury will be higher than what defined by tau parameter in a range between tau and 100%.

## Specification

The proposal refers to documents that decribe how and when the portion of rewards that goes to treasury is calculated and forwarded.

A. Proposed modifications to Shelley Ledger: Formal Cardano Ledger Spec. (SL-D5 v.0.2, 2019/10/08)

   Page 62 of the document that corresponds to page 63 of the pdf file

   1. At the fourth bullet point the sentence:
	    Next we calculate the proportion of the reward pot that will move to the treasury, as determined by the tau protocol parameter. The remaining pot is called the R, just as in section 6.5 of [SL-D1].
	    
      changes into:
	    The reward pot is called the R, just as in section 6.5 of [SL-D1].
	    
   2. At the fifth bullet point the sentence:
	    The rewards are calculated, using the oldest stake distribution snapshot (the one labeled “go”). As given by maxPool, each pool can receive a maximal amount, determined by its performance. The difference between the maximal amount and the actual amount received is added to the amount moved to the treasury.
      
      changes into:
	    The rewards are calculated, using the oldest stake distribution snapshot (the one labeled “go”). As given by maxPool, each pool can receive a maximal amount, determined by its performance. The difference between the maximal amount and the actual amount received is added to the amount moved back to the reserve. Next the portion of rewards that belong to treasury as determined by thetau parameter is calculated and added to the amount moved to treasury.


B. Proposed modifications to Design Specification for Delegation and Incentives in Cardano (SL-D1 v1.21, 2020/07/23) 

   Page 33 of the document that corresponds to page 34 of the pdf file, chapter 5.2 Parameters
   
   1. At the fourth bullet point the sentence:
	     The fraction tau [0, 1] of rewards going to the treasury.

      changes into:
             The fraction tau [0, 1] of distributed rewards going to the treasury.

   Page 35 of the document that corresponds to page 36 of the pdf file, chapter 5.4.4 Treasury

   1. The first sentence of the chapter:
	     A fraction tau of the rewards pot for each epoch will go to the treasury.
	   
      changes into:
             A fraction tau of distributed rewards for each epoch will go to the treasury.
		 
   Page 37 of the document that corresponds to page 38 of the pdf file, chapter 5.5.3 Pool Rewards

   1. At the paragraph that starts with "The actual rewards tkae the apparent performance ...", after the reward formula we add:
	     where actual rewards distributed to the pool will be reduced by the treasury contribution and are given by pf(s,sigma) * (1 - tau)
	     and pool contribution to the treasury is given by pf(s,sigma) * tau.
	     
   2. At the end of the page before the sentence "The diffence R ..." (character "E" in following formula must be considered as sigma summation notation for pools)
	     The sum of pools treasury contributions E(pf(s,sigma) * tau) will be sent to treasury.
		
   Page 44 of the document that corresponds to page 45 of the pdf file, chapter 5.10.4 Tau

   1. The first sentence of the chapter:
	     Setting tau is a policy decision; we will probably use tau = 0.2, i.e. 20% of available epoch rewards will be sent to the treasury.
	     
      changes into:
	     Setting tau is a policy decision; we will probably use tau = 0.2, i.e. 20% of distributed epoch rewards will be sent to the treasury.


## Rationale

Applying the aforementioned modifications to ledger specifications and, as consequence, to the protocol rewards that go to treasury will represent the exact fraction of distributed rewards as defined by the tau protocol parameter. 
Moving the calculation of treasury contribution at the time of pool reward calculation benefits the transparency and clarity of the protocol.
The treasury contribution will depend by the tau parameter only instead of a mix of variables and scenarios that make lifetime of the reserve more difficult to estimate.
Moreover it will also simplify the process in case of future parameter updates and fine tuning.

## Backward Compatibility

This proposal does not break backwards compatibility because it is an off-chain change.

## Copyright

Copyright 2020 Federico Pasini, Antonio Caccese, Piero Zanetti

This file is documentation, and therefore subject to CC-BY-4.0.
