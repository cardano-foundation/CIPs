# Cardano Certification Standard

**Draft version**: 2
**Last modification October 27th 2023**
**Authors:**

- Romain Soulat

## 1 Scope

### 1.1 Goal

This standard was defined for the evaluation of security functionalities included in Decentralized Applications running on the Cardano Blockchain.

The main objectives of the certification should be to demonstrate:

- Compliance with the security specification
- Effectiveness of the security functionalities

### 1.2 Purpose of the evaluation

The objective of the evaluation process is to allow an auditor or certificate issuing body to check whether the security requirements are fit for the intended use and security needs. It also allows them to check that the product:

- Conforms to its specification (functional and security)
- Satisfies the stated security requirements
- Is fit for its intended purpose
- Record the result of the certification in an on-chain certificate

## 2 Documentation to be provided

### 2.1 Introduction

A decentralized Dapp that has security needs (integrity, authentication, availability, confidentiality, ...) needs to show the appropriate security characteristics. Those security characteristics are necessary to establish trust between all the stakeholders.

For this reason, those characteristics needs to be presented to all stakeholders: auditor/certificate issuing body, end-users, ... Those characteristics are presented in the form of a Security Target for the product.

## 2.2 Target of Evaluation

### 2.2.1 General

The CCS should be flexible enough in what is evaluated so that it can be applied to a wide range of DApps. The CCS should be able to be applied to the whole DApp or only to a the most critical parts of it.

The TOE could be a DApp, a part of a DApp, a set of full DApps, or a set of parts of DApps.

One aspect that should be considered is the dependencies with external libraries.

The evaluation of a TOE containing only a part of a DApp should not be misrepresented as the evaluation of a whole DApp.

The evaluation of a TOE containing only a part of a DApp should be able to be used for the future evaluation of the whole DApp.

## 2.2.2 TOE boundaries

The concept of TOE boundary is fundamental to the specification of the Security Target.

A TOE may be a complete DApp, a part of a DApp, a set of DApps, or a set of parts of DApps. The Security Target needs to clearly identify the logical boundaries of the TOE.

Any parts of the overall product that are not included in the TOE are considered to be outside the scope of the evaluation.

## 2.2.3 Parametrization of a TOE

A DApp could be parametrized in many ways prior to deployment. Parts of a DApp could be created on-the-fly by the DApp itself. The TOE should clearly list the set of parameters that were considered.

An evaluation of such a TOE should clearly list the set of parameters that were considered and on which the evaluation was based on. A certificate can only refer to a version of the TOE with a parameter choice that matches one in the set considered for the evaluation.

## 2.2.4 Operational environment of the TOE

Everything outside the TOE boundary belongs the Operational Environment (OE) of the TOE. In the case of the evaluation of part of DApp, the non-TOE parts of the DApp are parts of the OE.

The Security Target needs to describe the assumptions on the OE so that together with the security functionalities provided by the TOE, the security objectives are met.

### 2.3 Security Target

The Security Target is used to specify the functions dedicated to the security of said product but also to describe the interface between the product and its environment in which it will operate. The developer, the people in charge of certification, the DApp operator, the end-users are therefore all interested by the Security Target.

The Security Target shall include the following information:

- Identification of the product and version to be evaluated
- Identification of the developer
- Product rationale and context in which the product will be used
- The assets to be protected
- The environment-specific measures (needed?)
- The threats to be countered
- The security functionalities to counter those threats

#### 2.3.1 Identification of the product and version to be evaluated

The product to be evaluated needs to be unambiguously identified. For example, through a git repository and a commit hash, or another versioning system.

#### 2.3.2 Identification of the developer

The developer of the product needs to be unambiguously identified. 
Needed/Wanted in our decentralized word? I like the idea but maybe not mandatory? For example, Certik has started a KYC process for the developers of the DApps they list.

#### 2.3.3 Product rationale and context in which the product will be used

The product rationale should include the following element if relevant: 

- intended use
- the environment in which the product will operate
- the threats within the environment
- Summary of the security characteristics of the product
- Dependencies on other software that are outside of the scope of the evaluation

#### 2.3.4 Assets to be protected

The Security Target must describe the assets to be protected. It must specify the expected protection for those assets (integrity, authentication, availability, confidentiality, [Maybe list examples for each?] ). It is important to note that the protection of those assets might lead to the creation of other assets. For example, the protection of an access token might require the creation of a dedicated wallet and hence of a private key, which will be considered as an asset.

#### 2.3.5 The environment-specific measures

[The CC list a bunch of environment specific measures that might not make sense in our context]
To meet the security requirements, it is possible that the product, or part of the product needs to be used in a specific environment. These measures can include organisational security measures. For example, the product will be deployed by an operator according to X, Y, Z deployment procedures, private keys will be stored in a secure way, etc.

#### 2.3.6 Description of threats

The Security Target must describe the threats that the product is expected to counter. A threat needs to be characterized by the following elements:

- a threat agent (users, administrator, malicious user, ...)
- a type of threat (unauthorized access, denial of service, transaction error, ...)
- the impacted asset (access token, private key, ada, tokens, ...)

#### 2.3.7 Security functionalities

The Security Target must describe the security functionalities that the product has implemented to counter the threats. 
This is the most important part of the Security Target.

















## 3 Evaluation Criteria

This section sets out the evaluation criteria designed to verify the compliance of the product to its specification. A succesful evaluation will result in the possibility of the issuance of a certificate.

[I think that some of those are not really well suited for Level 1 certification]

### 3.1 Analysis of the Security Target

The auditor/certificate issuer should:

- Check that the Security Target contains the elements described in section 2.2,
- Check that the Security Target is not misleading and contains at least the on-chain component of a DApp,
- Check that the security functions are relevant with the generic threats existing against the DApp,
- Check that security functions are all connected to at least a threat against an asset

### 3.2 Installation of the product

The auditor/certificate issuer should:

- Check that the product can be compiled and configured according to the Security Target,
- Check that the product can be deployed on a Testnet or Devnet representative to the Mainnet,

### 3.3 Review of the source code

The auditor/certificate issuer should:

- Give an expert opinion on the quality of the source code and structuring of the source code.

### 3.4 Testing 

The auditor/certificate issuer should:

- Test the product according to the Security Target,
- Explore well known weaknesses and vulnerabilities of the type of product under evaluation,
- Explore the capability of the product to run on the targeted environment,
- Evaluate the coverage of the tests of the requirements,
- Evaluate the coverage of the tests of the source code,

### 3.5 Evaluation of found vulnerabilities

[Maybe this one is more of an expert opinion and should not be considered for some certification levels]
The auditor/certificate issuer should:

- If vulnerabilities are found, evaluate the exploitation possibility of each vulnerability

[We can use the severity evaluation from the CTI proposal and add a threshold to say if a vulnerability should be addressed or not]

The auditor/certificate issuer should rely on its own expertise and on known weaknesses/vulnerabilities enumerations and databases. The auditor/certificate issuer is expected to provide a list or a reference of the list of weaknesses and vulnerabilities assessed whether they are found or not.

There are generally two types of vulnerabilities:

- Vulnerabilities that are specific to the product under evaluation. Those vulnerabilities are found by the competence and expertise of the auditor/certificate issuer.
- Vulnerabilities that are generic to DApps or the type of DApp under evaluation. Those vulnerabilities can be gathered in well-maintained databases and enumerations. They can also be discovered in the audit report of similar products.

[Should we add something about auditors should published the found vulnerabilities in a public database?]

## 4 Result of evaluation
[Check compliance to CIP-52]
The evaluation report should provide:

- The Security Target,
- A summary of documentation available to the users with associated links,
- The list of all vulnerability assessed, either through a comprehensive list, links to lists, or both,
- The list of identified vulnerabilities with their severity,
- The list of tools used for the evaluation,
- A summary of the tests conducted.

If no vulnerability is found [or if the vulnerabilities severity is below a threshold?], the auditor/certificate issuer should provide the choice to the developer to issue a certificate for the product.

The certificate should be issued on-chain [in compliance with CIP-0096] and contain the evaluation report in the off-chain metadata. 

