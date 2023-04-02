---
CIP: ????
Title: Cardano FUDS (Financial Updates & Disclosure Specification)
Category: Tokens
Status: Proposed
Authors:
  - Adam Dean <adam@crypto2099.io>
Implementors: TBD
Discussions:
  - https://github.com/cardano-foundation/cips/pulls/?
Created: 2023-04-02
License: CC-BY-4.0
---

# Abstract

Cardano Financial Updates & Disclosure Specification (FUDS) details a specification allowing on-chain projects to
publicly publish and disclose financial information that has historically been hosted in disparate locations and
formats; leading to confusion and lack of investor clarity.

Projects can benefit by having a template to follow for well-rounded financial disclosure and the community and
third-party services can benefit by easily being able to consume, analyze, and report findings based on publicly
published information.

# Motivation: Why is this CIP necessary?

One of the primary arguments for "Why blockchain?" is due to its nature as a publicly distributed, immutable and
auditable ledger which should increase consumer confidence through an ethos of ***"Don't trust. Verify."***
transparency. However, when it comes to many projects building and developing atop blockchain technologies we see the
development of opaqueness, obfuscation, and confusion in relation to how project funds and tokens are managed, housed,
and distributed.

This can substantially "muddy the waters" when it comes to a potential investor attempting to do their own research and
due diligence prior to investing in projects. Potential investors are asked to review "white papers" that often range
from exceptionally simplistic pie charts to math-heavy formulas and archaic "technobabble". Very seldom are things like
token distributions and project wallets clearly and transparently communicated to the investing public.

While most of the documentation in this CIP applies to token projects building atop the blockchain, the specification
contained herein could also be used as a template for similar disclosures for entities such as: NFT Projects, DAOs, and
other projects.

## Goal: Increase Transparency

By creating a community-accepted standard format for financial updates and disclosures we can simplify the disclosure
process for both token projects and marketplace aggregator services (DEXes, etc.) that attempt to provide information to
consumers and investors. Following standards allows us to educate and inform investors, consumers, and developers around
a common set of data points, minimizing the time it takes to "Do Your Own Research" (DYOR) while increasing confidence
in the reported dataset and verification of on-chain data to corroborate information contained within the disclosure.

## Goal: Utilize On-Chain Published Information

Currently, both CoinMarketCap<sup>[[1](#fn1)]</sup> and CoinGecko<sup>[[2](#fn2)]</sup>; two of the most relied upon
aggregator resources for blockchain token projects, utilize Google Docs as a method for token projects to submit
"self reporting" information about their projects. This process lacks transparency and verifiability.

By utilizing on-chain published information via a shared document standard we can:

1. Minimize the difficulty in the discovery and listing of new tokens projects
2. Cryptographically validate the authenticity (provenance) of the published information
3. Provide a set of open source software (OSS) tooling making it as easy as possible for third-party services to
   integrate
   Cardano token projects into their services.

## Goal: Allow Auditors to Verify Information

By creating a standard for projects to follow and third party services to consume, we can enable an ecosystem of
verifiable trust. This is pertinent to aforementioned projects like CoinMarketCap and CoinGecko but also to
community-internal tool providers such as TapTools and Xerberus that attempt to provide project analytics and data
insights.

The screenshots below show the current inconsistency in non-native Cardano aggregators with relation to their display
of information about Cardano token projects.

[CoinMarketCap HOSKY Listing](https://coinmarketcap.com/currencies/hosky-token/)

![HOSKY on CoinMarketCap](hosky-cmc.jpg)

[CoinGecko HOSKY Listing](https://www.coingecko.com/en/coins/hosky)

![HOSKY on CoinGecko](hosky-cg.jpg)

# Specification



Documentation on the standard format will be presented in CBOR format below and JSON schema documentation will
also be provided.

## Document Format

```cbor

uri.scheme = text
uri.path = text

uri = {
    uri.scheme,
    + uri.path
}

asset.bech32 = text .size (44)
asset.policy_id = bytes .size (28)
asset.asset_id = bytes .size (0..32)

asset-id = {
    bech32 : asset.bech32,
    ? policy_id : asset.policy_id,
    ? asset_id : asset.asset_id
}

owners = (
    airdrops-bounty : 0,
    burn : 1,
    ecosystem-incentives : 2,
    exchange-cold-wallet : 3,
    exchange-hot-wallet : 4,
    escrow : 5,
    marketing-operations : 6,
    masternodes-staking : 7,
    private-sale-investor : 8,
    public : 9,
    team-advisors-contractors : 10,
    treasury : 11,
    liquidity-provisioning : 12
)

allocation-types = (
    private-sale : 0,
    public-sale : 1,
    team-controlled : 2
)

unlock-data = {
    timestamp : text,
    unlock_quantity : uint,
    unlock_percentage : float
}

funding-types = (
    seed-sale : 0,
    ico-sale  : 1
)

allocation-wallet = {
    name : text,
    description : text,
    address : text,
    owner : &owners,
    ? locked : "locked" / "unlocked",
    ? future_use : &owners,
    ? proof : uri / text,
    ? allocated_quantity : uint,
    ? allocated_percentage : float,
    ? allocation_type : &allocation-types,
    ? unlock_schedule : [* unlock-data]
}

funding-detail = {
    timestamp : text,       ; time of investment
    type : &funding-types,  ; type of funding/round
    price : float,          ; price per token (USD)
    raised : float,         ; amount raised (USD)
    ? valuation : float,    ; valuation at time of raise (USD)
    ? investor : text,      ; name of the investor
    ? source : uri          ; URI to more information about the raise
}

financial-disclosure = {
    subject : asset-id,
    name : text,
    symbol : text,
    ? explore : uri,
    ? holders : uri,
    ? max_supply : uint,
    ? emission : "inflationary" / "fixed" / "deflationary"
    ? generation_date : text,
    ? allocation : [* allocation-wallet],
    ? funding : [* funding-detail]
}
```

**TODO**

- [ ] Expand on explanation of fields and what purpose they aim to serve.
- [ ] Add JSON schema docs
- [ ] Add examples

# Rationale: How does this CIP achieve its goals?

This specification is written and designed to work in conjunction with a registration and validation
specification such as [CIP-88](https://github.com/cardano-foundation/cips/pull/467). Validation and connection
of the data contained herein to a specific token project is considered out of scope for the purpose of this
CIP which should focus on the development and iteration of the disclosure standard.

For the first draft of this CIP the specification has been attempted to model after the CoinMarketCap and
CoinGecko information requested from their Google Docs solutions<sup>[[1](#fn1),[2](#fn2)]</sup> to attempt to be as compatible as possible with
existing ecosystem-agnostic platforms for simplicity of integration.

In order to maximize cross-platform compatibility it is recommended that these financial disclosure documents
be published as well-formed JSON documents utilizing decentralized, quasi-permanent storage solutions such as
Arweave or IPFS. However, platforms should accept documents published via traditional means such as HTTPS or FTP.

In order to prove the validity of the document, when publishing to the blockchain the document should be
published in the format of a URI that points to the document itself along with a SHA256 checksum of the document
contents (similar to how stake pool metadata is currently handled).

# Path to Active

## Acceptance Criteria

- [ ] Complete all "TODO" tasks based on currently identified shortcomings as well as feedback received.
- [ ] Receive community feedback and refinement from affected parties and potential implementors.
- [ ] Achieve buy-in from ecosystem participants to analyze and display data based on this spec

## Implementation Plan

- [ ] Invite identified stakeholders and market experts to review and provide feedback to the specification.
- [ ] Published OSS solutions for generation of FUDS documentation for projects
- [ ] Published OSS solutions for indexing of FUDS documentation for aggregators

# Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

# Footnotes

<sup id="fn1">1</sup>:
[CoinMarketCap Google Doc](https://docs.google.com/spreadsheets/d/1ON2o9fZtdj6aa_uaT7ALtGx1VxFnIDUi8-uS-fWji0o/edit#gid=1300521795)
for token project financial disclosure

<sup id="fn2">2</sup>:
[CoinGecko Google Doc](https://docs.google.com/spreadsheets/d/1Lh7HF2cJf5ElaGxoeMARU1XN6kB_EAeaMeyZKn6FMGI/edit?folder=0AGn_XsJsQytxUk9PVA#gid=743142986)
for token project financial disclosure