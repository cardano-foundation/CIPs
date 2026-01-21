---
CIP: XXX
Title: High Assurance Best Practices
Category: Tools
Status: Draft
Authors:
 - Romain Soulat <romain.soulat@iohk.io>
Implementors: []
Discussions:
 - https://github.com/cardano-foundation/CIPs/pull/926

Created: 2024-06-20
License: CC-BY-4.0
---
## Abstract

The proposal aims to establish a comprehensive framework for developing High Assurance (HA) software within the Cardano ecosystem. Drawing inspiration from industry standards such as DO-178C/333, IEC 61508, EN 50128, and Common Criteria, this CIP provides guidelines and best practices to ensure the reliability, safety, and security of software components. The proposal outlines a structured approach to requirement elicitation, software development, verification, and validation to achieve high levels of assurance.

## Motivation: why is this CIP necessary?
As Cardano continues to grow, the need for robust, secure, reliable and trustworthy software becomes increasingly critical. High Assurance software is essential for applications where failure can lead to significant financial, operational, or reputational damage. This CIP addresses the need for standardized practices to ensure that software components meet stringent safety and security criteria. Such a label (CIP-XXX compliant) will bring trust and confidence in the Cardano ecosystem if critical parts of the infrastructure, and main dApps follow the recommendations. Stakeholders include developers, auditors, regulators, and end-users who demand the highest levels of assurance in blockchain software components.

## Specification

### Activities
#### Safety & Security Analysis
**Objective** Conduct thorough safety and/or security assessments to identify and mitigate potential risks and vulnerabilities

Safety Analysis
- Perform safety analysis such as Fault Tree Analysis (FTA), Failure Mode and Effect Analysis (FMEA), Functional Hazard Analysis (FHA), …
- Identify potential failure modes and their impact on the system
- Implement mitigations to reduce or eliminate the likelihood of a failure event, or the severity of the impact 

Security Assessment
- Conduct security assessment, including asset identification, threat modeling, severity analysis
- Identify potential attack scenarios and their impact on the system if successful
- Implement mitigations to increase the financial means, or technical capabilities of the attacker, or reduce/eliminate the severity of the impact



#### Requirement Traceability
**Objective** Ensure all software requirements are well defined, traceable, and verifiable.

Requirement definition:
- Clearly define all functional and non-functional requirements
- Use structured templates to capture requirements to ensure completeness and clarity
- Use unique IDs for each requirement for traceability

Traceability Matrix
- Develop a traceability matrix linking each requirement to its corresponding design, implementation, and testing artifacts
- Have traceability both ways: From requirements to implementation and back to ensure that: all requirements have been implemented; and no additional undocumented features have been included in the implementation

#### Rigorous testing
**Objective**: Implement comprehensive strategies to ensure robust and reliable software.

Unit testing
- Unit tests for each component, ensuring that each component behaves as intended.
- Test for common weaknesses
- High code coverage should be reached at this level (e.g. 100% MC/DC?)

Integration testing
- Integration tests to verify that the different components interact correctly
- Test for attack scenarios
- Should cover the different scenarios of the integrated software

System testing
- Perform system-level tests to validate the complete system into its intended environment
- Test for attack scenarios
- Include performance testing, stress testing, usability testing, …(?)
- Ensure that the system meets both functional and non-functional requirements

Code coverage
- Measure code coverage to ensure that all parts of the code have been tested
- Critical components should have a very high level of coverage (e.g. 100% MC/DC or something like that ?)

Automated testing
- Implement automated testing framework to facilitate testing and regression analysis
- Tools could perform automated attack scenarios to reach higher coverage than what is reachable by hand.

#### Formal verification
**Objective**: Use of formal verification techniques to prove the correctness of either (or both) the correctness of the specification, the correctness of the implementation with respect to a formalized version of the specification.

Formal specification
- Use of formal specification languages to describe the expected behavior and properties of the software components.
- Specification should cover all aspects of the system, including functional behavior, safety and security requirements

Automated source code formal verification
- Apply source code formal verification such as deductive verification, abstract interpretation, model checking, to verify that the software models satisfy the specified properties
- Tools could also automatically check for common weaknesses and vulnerabilities

Specification and proof review
- The properties should be verified to be the correct expression of the specification
- The properties should be traced to the natural language specification if the natural language version is considered to be higher level.
- The proofs should be reviewed for correctness, completeness and any assumption should be carefully independently verified.

####  Code quality and standards
**Objective** Adhere to coding standards and best practices to maintain code quality, readability, and maintainability.

- Coding standards(?)
  - Static analysis
  - Use of static analysis tools to detect coding errors, security weaknesses, poor quality code, …

- Code documentation
  - Document all the code, with inline comments, and external documentation
  - Document the purpose, the functionality, the interfaces of each component
  - Ensure the documentation is up to date and refers to the latest version of the software component

#### Independent Verification and Validation
**Objective**: Establish an independent review process to assess software compliance with defined requirements and standards.

### Presentation of evidence
**Objective**: Ensure transparent and accessible presentation of evidence. This evidence should be provided on-chain, following a standardized format, to enable any stakeholder to understand the identified threats, mitigations, assumptions, and operational policies as well as to verify that all specified activities have been performed.

#### Evidence Format

**Introduction**: Overview of the software component, including its purpose and scope.
**Security and Safety Objectives**: Detailed description of the security and safety goals including the assets to be protected.
**Identified Threats and Feared events**: List of potential security and safety threats or feared events, with detailed descriptions, including the likelihood, the attacker power, the targeted assets.
**Mitigations and Countermeasures**: Explanation of how each identified threat is mitigated or countered.
**Assumptions**: Assumptions about the operational environment, including trust assumptions and external dependencies that are used to mitigate threats.
**Operational Policies**: Policies governing the operation and maintenance of the software, including access control, monitoring, and incident response.
**Verification of Activities**: Evidence that all specified activities in the Specification section have been performed.

#### Presentation on-chain

Using CIP-68, present the evidence on-chain. A few stakeholders could hold a user token (e.g. dApp operator, any other?). The reference NFT could be held either held at a smart contract, allowing for software and verification updates, or revocation.

TODO: Define the schemas, what is in the datum, what is stored off-chain.

## Rationale: how does this CIP achieve its goals?

The proposed framework is designed to enhance the reliability, security, and safety of Cardano software components. By adopting practices from established standards like DO-178C/333, ISO 61508, CENELEC 50128, and Common Criteria, the Cardano ecosystem can leverage proven methodologies to achieve high assurance levels. These standards are widely recognized and have been successfully implemented in industries such as aerospace, automotive, and railway, providing a solid foundation for achieving similar outcomes in blockchain applications. The rationale includes:
- Requirement Traceability: Ensures all functionalities are implemented correctly and can be tested thoroughly.
- Formal Methods: Provides mathematical guarantees of software correctness, reducing the likelihood of critical bugs.
- Rigorous Testing: Identifies potential issues early in the development cycle, ensuring robust and reliable software.
- Independent Verification and Validation: Ensures unbiased assessment of software quality, increasing confidence in the final product.
- Safety and Security Analysis: Proactively addresses risks, ensuring the software is resilient against attacks and failures.


## Path to Active

### Acceptance Criteria
- Community consensus on the importance and applicability of High Assurance Software standards. (Intersect WG Plutus, Certification)
- One successful pilot project demonstrating the effectiveness of the proposed standards.
- Adoption and endorsement by key stakeholders within the Cardano ecosystem (Auditors, developers, …)

### Implementation Plan

Community Engagement and Consensus Building
- Conduct discussions in the relevant Intersect working groups to raise awareness about the importance of High Assurance Software.
- Gather feedback and build consensus among developers, auditors, end-users, and other stakeholders.

Documentation and Standardization
- Develop detailed documentation outlining the proposed standards and guidelines.
- Develop documentation for each different step of the proposal.
- Create templates and tools to assist developers in implementing these standards.

Establishment of a Certification Committee
- Form a certification committee composed of experts from the Cardano community, industry, and academia.
- Define the roles and responsibilities of the certification committee, including the certification of evaluation by auditors.
- Develop and maintain the certification criteria and processes based on the proposed High Assurance Software standards.
- Ensure the committee operates transparently and engages with the broader community.

Pilot Projects
- Identify and execute pilot projects to test the proposed standards in real-world scenarios.
- Collect data and feedback to refine and improve the standards by the certification committee.

Implementation and Monitoring
- Encourage widespread adoption of the standards across the Cardano ecosystem.
- Encourage auditors to comply to this CIP
- Encourage dApp stores or aggregators 

## Copyright
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
