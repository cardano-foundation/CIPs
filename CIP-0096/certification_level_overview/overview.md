# Certification Levels Overview

## Abstract

The Certification Levels details are being finalized by the Certification Working Group.
Three different levels of certification for the Cardano ecosystem are being defined, with an additional one for audits or reports that do not match any of the three levels.
The goal is to provide a clear and transparent way to communicate the level of quality of a given project or product in the Cardano ecosystem to all stakeholders.
Contrary to [CIP-0052](https://developers.cardano.org/docs/governance/cardano-improvement-proposals/cip-0052/), there will be requirements to be achieved. This standard does not aim at imposing tools and techniques to be used, but rather objectives to be reached.

## Certification Levels

### Level 0 - Security Audit & Reports

#### Level 0: Overview

Level 0 provides the capability to an auditor, a DApp operator, or a DApp developer to provide the result of any security audit. 

#### Level 0: Certificate broadcast on chain

The broadcasted certificate must follow CIP-0096 schema as an `AUDIT` certificate.

### Level 1 - Automated testing

#### Level 1: Overview

Level 1 provides a *basic level of assurance in functional and security verification*. The goal of this level is for the developer to provide, at very low cost, a basic level of assurance to the end user that the DApp has been tested, is functional, and has some basic levels of security.

The major part of the work is to be done by the developer. At this level, the automated tool can be seen as assuming the role of the "evaluator" in the evaluation process. 

#### Level 1: Certificate broadcast on chain

The broadcasted certificate must follow CIP-0096 schema as a `CERTIFY` certificate with a level of 1.
The off-chain information shall contain the full evaluation report.
The certificate shall be issued to the scripts as computed by the automated tool.

### Level 2 - Manual Audit

#### Level 2: Overview

Level 2 provides a *higher level of assurance in functional and security verification*. The goal of this objective is to have an independant entity to challenge the developer's work. At this level, the documentation provided by the developer is challenged by the evaluator, and further penetration testing is expected to be performed.

#### Level 2: Certificate broadcast on chain

The broadcasted certificate must follow CIP-0096 schema as a `CERTIFY` certificate with a level of 2.
The off-chain information shall contain the full evaluation report.
The certificate shall be issued to the scripts as computed by the automated tool.

### Level 3 - Formal Verification

#### Level 3: Overview

Level 3 provides strong guarantees on the correctness of the DApp. The goal of this level is to provide a formal proof that the DApp behaves as expected.

#### Level 3: Certificate broadcast on chain

The broadcasted certificate must follow CIP-0096 schema as a `CERTIFY` certificate with a level of 3.
The off-chain information shall contain the full evaluation report.
The certificate shall be issued to the scripts as computed by the automated tool.