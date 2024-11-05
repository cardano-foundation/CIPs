---
CIP: ?
Title: Affirmation Graph
Category: Tools
Status: Proposed
Authors:
  - Kieran Simkin <hi@clg.wtf>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-10-26
License: CC-BY-4.0
---

## Abstract
We need a truly decentralized alternative to KYC for when we need to establish the authenticity of a wallet or make some judgement about its trustworthiness in a systematic and repeatable manner. This CIP defines a mechanism whereby any member of the community can publicly vouch for the authenticity of a wallet by submitting an "affirmation" transaction, it also provides a mechanism to revoke such an affirmation, if, for example a wallet becomes compromised, or its owner turns out to be a charlatan. 
It is then possible to observe the current UTxO set and draw an "Affirmation Graph", a multidigraph representing the trust relationships between wallets - we can then use an algorithm to assign trust rankings and decide whether or not to trust an unknown wallet.

## Motivation: why is this CIP necessary?
When transacting with an unknown person, currently if we want to make sure we're not dealing with a bot or a grifter, we have to perform our own detective work - examining their current token holdings and transaction history, then we make some informed guess about what we're dealing with. This is both laborious and inconsistent. 

Now that we are in Cardano's Voltaire era; governance is top of the agenda, it would be really nice to be able to hold ballots where each community member gets an equal vote - true democracy requires it. Currently all voting is stake-weighted - ie. 1 ADA = 1 vote - I believe it was a mistake to extend stake-weighted voting outside of its original scope within consensus mechanisms - it enables a small group of wealthy stakeholders to manipulate every vote to their liking, and these rich stakeholders barely overlap with the people most qualified to be making technical and philosophical decisions about the future of the chain - many of the people who are the best qualified, are risk-adverse developers who operate almost entirely on testnet, and have only a few thousand Ada in their mainnet wallet. It's increibly important for the future direction of Cardano that these these people have a fair vote and it's not just completely obliterated by even one whale vote, as it would be now. 

There is also the goal of fraud and scam prevention - currently if you're just sending a transaction to a random wallet, you've really no idea who or what that wallet represents, or if it's even an active address, in some cases your wallet might show the Ada handle of the recipient, but other than that you're basically just seeing random numbers and letters, and if you wanted to look up any further information you would have to use a separate blockchain explorer. 

## Specification
[v1 of the affirmation contract](affirmation.ak)
In order to send an affirmation to a *target* wallet, one must construct a "frankenaddress" consisting of the affirmation contract as the spending part and the *target*'s stake address for the delegation part. To this address you should send the minimum UTxO Ada, and you must mint a single token from the affirmation contract's policy, the token name must be set to your own stake key hash, the token, along with the min UTxO Ada should end up on an output at the script "frankenaddress", and this output must have an inline datum specifying your stake key (if you fail on any of these criteria, the validator will eat your money) 
   - this open UTxO represents your current endorsement of a particular wallet. 

If you wish to revoke an affirmation, all you need do is "spend" the currently open UTxO at their frankenaddress. You must burn the associated token, and sign the transaction with your stake key, which must match the one that's stored on the UTxO datum and in the token name. 

It is worth noting that the target can also be a script address, so this allows smart contracts and NFT collections to receive affirmations too. 

MeshJS (the Typescript Cardano library) [has been updated](https://github.com/MeshJS/mesh/commit/fbfc8dd922ddf4c4df0d59f5fbd4f260af34da5d) so that it knows how to build these transactions, so you can do it in one easy step if you're in TS/JS. [A Python implementation](https://github.com/kieransimkin/affirmation-graph/blob/main/examples/affirm.py) is also available. 

## Rationale: how does this CIP achieve its goals?
It could be argued that, with enough Ada, it is always possible to create many wallets and then submit affirmations for yourself - thus returning the system to being weighted by how much Ada you have - however, this would be a failure to understand the purpose of a decentralized Affirmation Graph - in a this regiem, each individual person is responsible for interrogating the graph to establish a trust score for a particular wallet - but they have complete freedom on how they choose to interpret the graph - for example, you could decide to only trust wallets that have been affirmed by a specific person (perhaps yourself, or a person you know who has affirmed a lot of people and whose judgement you trust), or only trust wallets that have a minimum number of affirmations from anyone, or you could specify that at least two of your friends must have affirmed a wallet. You could even require that a centralized KYC provider has affirmed a wallet - this would allow you actual KYC gating in a semi-decentralized manner - multiple KYC providers might exist, and you might choose to give a higher trust rating to some than others, perhaps depending on how thorough their ID verification process is. Other providers might exist which offer affirmations in return for proving you own a unique Facebook or Google account. 

It is expected that there could be a flood of services offering affirmations in return for jumping through any number of different hoops. It is also expected that mutual affirmations will be offered; "I'll affirm you if you affirm me". None of this does any harm to the value of the graph since we can design our algorithms to sift through the data and derive whatever meaning we please from it - the more we expand the size of the graph, the more we have to work with.

The algorithms for interpreting the graph are expectied to become numerious and varied - some examples will be provided as part of the Affirmation Graph toolchain, and users will be free and encouraged to build their own and contribute them back to the library. 

### Could this amount to a form of social credit scoring?   
Well, you could describe it that way, but the biggest problem with social credit is that it's decided by a centralized authority - there's no centralized authority here, it's an egalitarian collective. I think of it as similar to the way we all have an understanding of how reputable we consider a given person - some of that will be biased by our own position, but some people will be fundamentally more "reputable" than others, we all have an instinctive understanding of who we consider these people to be. There is, perhaps, a danger in making something like reputation so publicly visible - generally these reputation judgements are something we do so regularly in real life that it's an unconscious process a lot of the time, and we're often not even immediately aware of why we've judged a certain person as untrustworthy or not. The Affirmation Graph does still give you the privacy of your own judgements though as there's no way to know what criteria you're basing your decisions on. The only thing thing you're sharing publicly is the set of wallets you endorse - this is really no different to a public friend or follow list like you have on most social networks. 

This CIP is fundamentally about linking the social graph with the blockchain, so that you can have the same level of confidence that you're dealing with a real human-being as you do on Facebook or Twitter. While this is never 100% certain, I would argue that most people can tell the difference between a real human or a bot on social media with a high degree of accuracy - we need to acheieve a similar level of confidence in our judgements about whether or not we trust a wallet on the blockchain. Only then can we have a hope of implementing 1-person-one-vote and having any meaninful form of democractic system - and that's the end goal; to enable Cardano governance to be truly democractic by removing the biases of stake-weighted voting, and instead move to 1 person = 1 vote.

## Path to Active

### Acceptance Criteria
<!-- Describes what are the acceptance criteria whereby a proposal becomes 'Active' -->

### Implementation Plan
- [X] Design and test the smart contract along with its transaction builders in Typescript and Python
- [ ] Get feedback on the smart contract with a view to permanently setting it in stone 
- [ ] Create a React control to enable blockchain explorers and dApps to easily add an "Affirm this wallet" button.
- [ ] Implement "Affirm this wallet" into [Cardano Looking Glass](https://clg.wtf/)

## Copyright
This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

