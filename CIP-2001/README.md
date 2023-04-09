---
CIP: 2001
Title: Automated Stake Pool Node Version Reporting
Authors: Marcus Ubani - hello@larissa.health
Type: Standards
Status: Draft
Created: 2023-04-09
License: CC-BY-4.0
---

## Abstract

This CIP proposes a mechanism to automatically report the node version of stake pools in the Cardano network, 
making it easier for delegators to identify and delegate to well-maintained pools. 
This would be achieved by including node version information during KES or node updates, which can then be displayed in wallets.
The CIP-number is inspired by the novel Odysee in Space (2001, 2010), and seeks to ease the general process for delegators and SPOs. 

Among those members who participated in the discussion in Discord and shared their views and ideas were 
Tommy Kammerer, George [APEX], Danny Tuppeny [WEN_K],  Homer [AAA], Vahid [A4G], Rick [RCADA], Sean [ENVY], Rich [ECP]


## Motivation

Outdated nodes and unmaintained stake pools pose potential security risks to the Cardano network. 
By providing an automated way for delegators to identify the node version of stake pools, 
they can make more informed decisions when delegating their ADA, 
ultimately contributing to a more secure and better-maintained network.

## Specification

1. During KES or node updates, stake pool operators (SPOs) would submit a new KES update that includes the current node version.
2. The transaction for the KES update would include a message with the node version and the datum.
3. An additional CLI command or an extension of an existing command would be implemented to facilitate this process.
4. Wallets and other user interfaces would display the node version for each stake pool, allowing delegators to easily identify well-maintained pools.

## Rationale

The automated reporting of node versions offers several benefits for both delegators and stake pool operators:

### Delegators
1. Can easily identify the node version a stake pool is running on.
2. Can make more informed decisions to support specific node versions and contribute to a healthier ecosystem.
3. Are less likely to delegate to unmaintained or outdated stake pools.
4. Receive assurance on the pool's maintenance status at the protocol level.

### Operators
1. Are less likely to miss their KES rotation.
2. Can demonstrate their responsiveness to node version updates.
3. Can verify if their block producer is capable of minting a block.

## Backward Compatibility

This proposal will require changes to the CLI commands.
In an even more automated version the protocol would need to accommodate the automated reporting of node versions. 
Existing stake pools would need to adopt the new process, but it should not have a significant impact on their operations.

## Test Cases

Test cases should be developed to ensure that the automated reporting of node versions functions correctly, 
and that the information is accurately displayed in wallets and other user interfaces.

## Implementations

I am currently not aware of similar processes.
But reference implementations, prototypes, or work-in-progress code related to this proposal should be provided as they become available.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
