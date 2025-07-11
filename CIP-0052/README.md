---
CIP: 52
Title: Cardano audit best practice guidelines
Status: Proposed
Category: Meta
Authors:
  - Simon Thompson <simon.thompson@iohk.io>
Implementors: []
Discussions: 
  - https://github.com/cardano-foundation/CIPs/pull/252
  - https://github.com/cardano-foundation/CIPs/pull/344
  - https://github.com/cardano-foundation/CIPs/pull/406
  - https://github.com/cardano-foundation/CIPs/pull/560
Created: 2022-04-25
License: CC-BY-4.0
---

## Abstract

These guidelines describe the audit process in general before setting out for DApp developers what information they will need to supply to auditors as part of the process. These are guidelines rather than requirements, and different auditors may engage differently, providing complementary services. The guidelines aim to establish a common baseline, including alternative ways of satisfying high-level requirements. Appendices provide (1) a glossary, (2) an audit FAQ, (3) a list of auditors for Cardano, and (4) a sample audit report.

## Motivation: why is this CIP necessary?

This CIP aims to promote the process of audit for DApps on Cardano, to improve the overall standard of assurance of DApps built for Cardano, and thus to contribute the improvement of the wider Cardano ecosystem.  

## Specification

### Introduction

DApp users seek assurance about DApps that they wish to use. This comes from running automated tools on DApps and their components, as well as by audit of complete DApps. Secure evidence of these tool (level 1) and audit (level 2) results is provided by a certification service, and made available to users through a service such as a DApp store or wallet. In the longer term, results of formal verification (level 3) will also form part of the certification process.

DApp developers seek to drive adoption through their DApps being certified. Wallets and DApp stores are enhanced by providing certification services, and the wider Cardano ecosystem is strengthened through certification becoming widespread. Best practice standards can be developed by the audit and tooling communities, and systematised by the Cardano Foundation. This document is a first step in that direction.

**Assurance can only ever be partial:** a DApp can be shown to have some good features and to avoid some bad ones, but this is not a guarantee that using a DApp will not have negative consequences for a user. This is not simply because tools and audits cannot give complete coverage, but also because attacks may come at lower (e.g. network, browser) or higher (e.g. crypto-economic) levels than addressed here.

These are guidelines rather than requirements, and different auditors may engage differently, providing complementary services. The guidelines aim to establish a common baseline, including alternative ways of satisfying high-level requirements. Appendices provide (1) a glossary, (2) an audit FAQ, (3) a list of auditors for Cardano, and (4) a sample audit report.

### Prerequisites

#### Key terms

***(Smart) contract***: a program that runs on blockchain. In the case of Cardano, this will be a Plutus program that will contain Plutus Core components that run on blockchain as well as other code that runs off chain. All auditors will scrutinise on-chain code, some will examine off-chain code too.Some auditors might also provide orthogonal services eg. auditing a zero-knowledge protocol or an economic model.

***DApp***: a complete “distributed” application that runs on blockchain. This will include off-chain code written in other languages, e.g. running in a browser, and will integrate or link with other services such as wallets and oracles.

***Assurance***: the process of establishing various properties of systems, both positive (it does this) and negative (it doesn’t do this), with different degrees of certainty.

***Audit***: the process of establishing assurance by means of manual examination of artefacts, systems, processes etc. Can involve some tooling, but it is a human-led process.

***Tooling***: using automated processes to establish degrees of assurance of systems. Tools may be run on target DApps by parties providing such a service.

***Evidence***: artefacts coming out of tooling and audit that can support assertions of assurance of systems. Examples include formal proofs, test suites, prior counterexamples and so on, as well as audit reports.

***Certification***: the process and technology of giving to DApp end-users and developers secure evidence of forms of assurance about DApps and their component smart contracts. In the case of Cardano our approach is to provide information on  chain as transaction metadata. 

*Note*: “certification” has also been used informally to cover the combined process of testing, audit, verification and providing evidence of these, as in “level 1 certification”. If it is felt that it is too confusing to use the term in both senses, then another term should be found, e.g. *evidencing* or *witnessing*. 

***Component***: a discrete part of the complete system supplied by a third party, such as a wallet, (part of) which will be run on the user’s system.

***Service***: a part of the system, such as Blockfrost, that is provided by an online server accessed through a well-defined protocol.

***Scope***: the parts of the DApp that are subject to audit. A repository may contain much more than Plutus code. Some audits will look at the complete app, some will just concentrate on on-chain transactions, others on the web interface around it. The possible scopes are divided in three main categories:
* On-chain
* Off-chain
* Context: the business and economic models for the DApp  

***Deployment***: once a DApp is developed it is deployed by submitting the relevant on-chain scripts onto the Cardano blockchain as transaction validator scripts. The scripts being deployed  might be the scripts that have been audited, or be instances of them in the case that the audited scripts are *parametric*.

#### Audit FAQ

##### *What is an audit?*

An audit is a comprehensive investigation of a DApp that provides an in-depth analysis on bugs, vulnerabilities, code quality and correctness of implementation. An audit does not necessarily analyse completed DApps and often will instead analyse a fragment of a DApp. For example many auditors will only analyse the on-chain code of a DApp.  

##### *Who provides an audit?*

Audits are provided by companies that specialise in the area of the developed DApp. In this case it will be experts on the Cardano blockchain and Plutus smart contracts.

##### *How does audit work? What is the process?*

This first part of the process is tendering, where developers will need to provide preliminary information about their DApp to candidate auditors, as described below.

Once a contract is agreed, the next step in the process is to provide the auditors with the necessary information to perform the audit as set out in the guidelines below. Auditors may work with developers to ensure that the documentation and other materials for audit are prepared to the standard that is required for the audit to take place. Different auditors will have different requirements, but the guidelines below establish the minimum requirements.

Auditors will typically produce a first version of a report, which the developer can use as a guide to improving their DApp, before submitting changes to produce the final version of the code on which the final, published report is based. Once a DApp is audited, it will be deployed on the Cardano blockchain.

##### *When should a developer contact an auditor?*

A developer should contact an auditor when they have a final working version of a DApp or fragment of a DApp that they want to have audited. Once the contract is agreed, the developer will need to provide the auditor with a final version of the DApp for audit. 

However, it is recommended to contact a potential auditor as early as possible because many auditors also provide consultation services for the design and development of the DApps. A developer is encouraged to contact the auditor as early as possible so as to mitigate any design issues which may be very hard if not impossible to fix. Early contact is also encouraged because securing a time slot with an auditor in advance shortens the DApp’s overall time to market, finally, early contact allows for scheduling and potentially avoids long delays between starting and completing an audit.

##### *What is audited when an audit takes place?*

All audits will examine the on-chain code that is used to validate transactions submitted to advance the smart contracts that constitute part of a DApp. Audit may also cover more of the code in a DApp, including on- and off-chain code written in Plutus, as well as other languages, e.g. JavaScript running in a browser. 

##### *What guarantees can and cannot be given by an audit?*

An audit ***is not*** a guarantee of unbreakable security nor a way to offset trust or responsibility. An audit will provide an in-depth review of the source code of a DApp. The audit will provide a comprehensive code review detailing any found vulnerabilities, comments on the quality of code as well as an analysis of the implementation in regards to the supplied specification. An audit cannot guarantee that all possible vulnerabilities will be found or that the deployed DApp will perform as intended. This is especially true in the cases where an audit only looks at a fragment of a DApp or when a DApp has been updated.

##### *Who are the stakeholders involved in the audit process?*

DApps are used by *DApp users*, and built by *DApp developers*. Audit is performed by *audit companies*, using tools developed by themselves and other *tool developers*. Tooling can be run by *tool service providers*, and evidence of those and other results produced by *certification providers*. Audit is also impacted by components (e.g. light wallets) and services (e.g. blockfrost) provided by *ecosystem members*. Standards can be developed by *industry consortia* or *governance organisations* (e.g. the Cardano Foundation). In the widest sense, all *holders of Ada* stand to benefit from Cardano building an expectation that DApps are certified.

### Cardano auditors

| Audit company   | URL                                     | Contact email      | Public key      |
| -----------     | -----------                             | -----------        | -----------        |
| FYEO Inc.       | https://gofyeo.com/blockchain-security  | sales@gofyeo.com  | |
| Hachi           | https://hachi.one                       | team@hachi.one        | |
| MLabs           | https://mlabs.city                      | info@mlabs.city      | 64BC640B5454215D12165EEAEEFF303D2643ABA2 (PGP, ed25519) |
| Runtime Verification           | https://www.runtimeverification.com | contact@runtimeverification.com  | |
| Tweag                | https://www.tweag.io                  | sales@tweag.io                  | |
| Vacuumlabs (audits → Invariant0) | https://vacuumlabs.com/   | info@invariant0.com  | 16541FD112978F3C6D49E79881E6B1F9C0BC6BF9 (PGP, ed25519) |
| CertiK      | https://www.certik.com/products/smart-contract-audit/   | sales@certik.com  | |
| Invariant0  | https://invariant0.com/                     | info@invariant0.com  | 3C010EA5654D57D0AEF0E50B75D3AA3D42D52499 (PGP, ed25519) |


### Tendering
In order to provide a quote for audit, developers will need to supply
* A specification of the DApp to be audited (more details below).
* The scope of the audit.
* An estimate of the scale of the audit work, e.g. the number of lines in the on-chain code to be audited, or the code itself, in its current state of development.

### Submission
In order to be audited, developers will need to supply the following documentation.

#### *Specification / design documents*

Submitters shall provide specification and design documents that describe in a precise and unambiguous way the architecture, interfaces and requirements characterising the DApp. 

The documentation shall identify the expected behaviour of the code, given without direct reference to the code itself. The description should also include high-level examples demonstrating use cases of the DApp. All assumptions about how the DApp will be used will be described. The documentation shall identify and document all the interfaces with other components and services.

Submitters might also wish to explain mitigating actions that they have taken to protect against potential failures and attacks to the DApp.

#### *On-Chain Specification* 

The format of transactions accepted by the smart contracts should be specified using the template provided in the auxiliary document `Tx-spec.md`.

The document should clearly specify the properties to be satisfied by the smart contract.
* Properties shall be as extensive as possible and ideally would cover functionality, robustness, safety, liveness and efficiency, e.g. cost of execution, of the smart contract. 
* Discussion should describe whether any of the properties addresses common vulnerabilities pertaining to Cardano blockchain or the smart contract domain in general. 

A formal specification is recommended but not mandatory. 

#### *Off-Chain Specification*

For off-chain analysis additional information should be provided for the components and services interfaced:
* For all interfacing components, a specification shall be given detailing their expected behaviour in relation to the DApp, including any assumptions, constraints and requirements of the component that are expected to hold by the DApp developers.
* It also shall be stated whether any of the interfacing components have been certified.

#### *Testing*

Ideally, submitters should submit a description of how the DApp has been tested, the results of the tests, and details of how those test results can be replicated.In particular:
* The test cases and their results shall be recorded or reproducible in a machine-readable format to facilitate subsequent analysis.
* Tests are to be performed for each targeted platform (browser, wallet etc).
* The identity, configuration and version of all test components involved shall be documented.
* The checksum and version of the DApp submitted for certification shall correspond to the same version making the subject of the test report. 
* An evaluation of the test coverage and test completion should be provided. 

In the case that off-chain code is included in the scope of the audit, testing should be able to assess the performance and robustness of the DApp against significant throughput, under substantial workload, and in the scenario of a DoS attack.

#### *Source code and version*

A final version of the source code should be provided that works with the use cases specified in the documentation. Information needs to be provided to allow the DApp to be built in an unambiguous and reproducible way, including any external components and services that the DApp uses.  This could be in the form of


* The URL for a commit to a repository.
* Build information for the DApp: a pure nix build is particularly suitable, since this will identify versions of  libraries, compilers, OS, etc.
* For the on-chain code for a DApp, the specific contracts to be audited.

#### *Versioning*

Versioning information needs to be given in a way that allows end users of a DApp to determine whether or not the version of the DApp that they are using is covered by certification information held on blockchain.


This can be done in a number of different ways, depending on the type of audit. These include:
1. The hash of a URL for a commit to a publicly-available repository.
2. A hash that identifies the files that contain the on-chain code that has been audited, e,g computing, from the root of the repository, listed in lexicographic order.

#### *Registration*

It is planned that DApps will be registered on the Cardano blockchain. This is currently under discussion. Once that discussion has been settled, it will also be possible to provide on-chain evidence of audit, linked to a registered entity. The mechanism for this is described in a separate document which it is intended to make into another CIP. A current draft of that document is here: [Proof of Audit document](https://docs.google.com/document/d/1FvgX8QiGKVPv4c7HanZ92zwstD9U1amOf8eHvyIb1dI).

### Requirements for Auditors

#### *Responsibilities*
Auditors shall be able to carry out the following activities: 
* Review the requirement specification document against the intended environment and use so as to:
   * Identify any inconsistencies, security flaws or incomplete requirements
   * Identify any implicit assumptions and whether they are justifiable or not
   * Evaluate the adequacy of strategies applied by the submitter to guarantee the consistency, correctness and completeness of the requirements
   * Identify a threat model to guarantee that any identified mitigations are indeed appropriate against a list of possible vulnerabilities for Cardano smart contracts, and which is currently being finalised.
*  The source code shall be audited by manual and/or automated means. In particular,
   * The source code shall be reviewed against the requirements to ensure that all of these are properly taken into account and completely fulfilled.
   * The adequacy of the source code documentation and traceability with the requirements shall be assessed.
   * The source code shall be free from coding patterns/programming mistakes that may introduce exploitable vulnerabilities/failures leading to security issues.
* Produce a detailed audit report describing scope, methodology, and results categorised by severity. In particular,
   * Any discrepancies, deviations or spotted vulnerabilities shall be described and classified with an appropriate severity level. Recommendations to rectify the identified deficiencies shall also be provided whenever appropriate.
   * When automated tools are used as a replacement for manual review/code inspection, they shall be documented or referenced. Note that it’s the responsibility of the auditor to ensure that such tooling may not exhibit potential failures that can adversely affect the review outcome.
   * Any strategies/methodologies used to assess the consistency, correctness and completeness of the requirements shall also be documented or referenced.

#### *Key competencies*

Auditors shall provide credentials for the following competencies:
* They shall have an in-depth knowledge of the syntax and semantics of the smart contract language to be audited, the underlying blockchain technology and associated computation and cost models.
* They shall be competent in the strategies and methods used to elaborate threat models.
* They shall be competent in assessing the suitability of methods (or combination of methods) used to justify the consistency, correctness and completeness of requirements against the list of common vulnerabilities pertinent to the smart contract domain and to guarantee (as far as possible) the absence of security flaws in the design.
* They shall be competent in various test and verification methods and have solid background in the various test coverage criteria (i.e., statement, data flow, branching, compound condition, MC/DC and Path).
* They shall also be able to assess whether the set of test cases produced for each specific test objective/property are sufficient enough to cover all the possible functional cases.
* They shall have analytical and critical thinking ability pertaining to the:
   * deployment and execution of smart contracts on the underlying blockchain technology;
   * Potential attacks or sequence of events relative to the smart contract’s logic that may lead to an unsafe state or invalidate some of the fundamental properties of the contract.
* They shall be able to judge the adequacy of the justifications provided by submitters w.r.t., development processes (e.g., requirement elicitation techniques, threat models, test objectives and test cases, coding standard, quality management, etc) for Level 2 certification.

#### *Disclosure*
Disclosure
It is common – but not universal – practice for disclosure/publication of audit report, for example as a part of a responsible disclosure policy. A typical policy would be to publish a report after a certain period (e.g. 30-90 day) or at the point that a DApp goes live, whichever is earlier.

## Rationale: how does this CIP achieve its goals?

These guidelines are the result of a process of discussion between IOG staff and members of the audit and academic communities over a series of online meetings in February and March 2022. Audit organisations involved include Tweag, WellTyped, Certik, Runtime Verification, BT Block, MLabs, Quviq and Hachi/Meld, all of which supported the guidelines outlined here.

## Path to active

### Acceptance Criteria

- [ ] Evidence that Cardano audits are being performed according to this proposed standard, by reference to specific audit(s) citing CIP-0052 and containing these audit elements.

### Implementation Plan

- [x] Initial set of Cardano auditors provided with CIP, with others added afterward along with contact information and verification keys.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

