```
CIP: ?
Title: Multi-Pool Stake URI Scheme
Author: Robert Phair <rphair@cosd.com>
Discussions-To:
Comments-Summary: No comments yet.
Comments-URI:
Status: Draft
Type: Standards
Created: 2020-09-22
License: CC-BY-4.0
Post-History: https://forum.cardano.org/t/40594
```
## Summary

Support reading and writing weighted lists of stake pools through a URI scheme, facilitating automatic stake allocation in all Cardano wallets and other means of delegation.

## Prerequisites

Support in wallets & exchanges for multi-pool delegation.

## Abstract

Cardano wallets and exchange delegation mechanisms currently have no means to receive an Internet friendly reference to one or more stake pools in a way that establishes their proportion for staking: in general terms, a *portfolio*.

A staking URI scheme will allow such portfolios to be easily developed and shared by the community itself, with a common standard for interpreting these on Cardano wallets and compliant exchanges.

Aside from portfolios, It will also meet the simple but vital use case of individual pool web sites providing a one-click reference directly into a user's delegation wallet.

## Motivation

Centralised sources of information, particularly a Daedalus ranking mechanism [currently biased](https://gist.github.com/ilap/ad088d31e542f73685a3a245b3ad6c50) to only take into account rewards from the top K (currently 150) largest stake pools, have led a growing amount of stake to be disproportionately assigned to pools pushed near & beyond the saturation point.

A growing Cardano blockchain, facing a likely sudden increase in load within the year from the introduction of Smart Contract applications, needs to more rigorously maintain its goal of decentralisation by distributing the balance of rewards, network/computing power, training, and operational knowledge among an increasingly larger group of operators.  Otherwise that sudden increase may require an equally sudden rise in K to a much greater figure without having at least that number of high-quality pools.

There is also a subjective perception within and without the Cardano community that the stake pool conglomerates and Cardano foundational entities are effectively sponsoring centralisation of stake for their own benefit.  Supporting a means for small stake pools and staking peer groups to be individually recognised would reverse this trend both practically and subjectively.

## Specification

Example, trivial case (a single pool):
`web+cardano://stake?COSD`

Example, simple case (a non-weighted portfolio of 3 equal favourites:
`web+cardano://stake?IOG1&OCEAN&EMUR1`

Example, more general case (a weighted portfolio, top 10 pools by 30-day ROA at time of writing):
`web+cardano://stake?CRAB=30.14&MYTH=20.84&NINJA=20.04&HYPE=17.80&MARLN=16.92&KINGS=16.81&COSD=15.62&RAID3=15.32&ZOE=15.20&XORN=14.93`

Syntax explanation (see [Wikipedia: Uniform Resource Identifier](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier)):

* this takes protocol `web+cardano` from the Yoroi reference implementation linked below and adds an "authority" (`//stake`) to differentiate the stake pool reference(s) from a payment request URIs or references to some other Cardano resource.
* For security the hex `pool ID` should be usable here instead of each stake pool name, although with [SMASH](https://github.com/input-output-hk/smash) currently slated for Daedalus integration this may not be necessary to avoid ambiguity.

Syntax items, in order:

* protocol: `web+cardano:`
* authority: `//stake`
    * if authority is omitted, assumed to be a payment URI (see Reference Implementation)
    * if authority is something else, it refers to a different Cardano subsystem than staking.
* arguments (`?` before first argument, `&` before each additional argument
    * `poolTicker` or `poolHexID` (mandatory)
    * `=proportion` (optional): integer or decimal, indicating relative size of stake allocation

Interpretation of `proportion`:

* If only one stake pool is specified, any proportion is meaningless and ignored.
* If all stake pools have a numerical proportion, each component of the resulting stake distribution will have the same ratio as the provided `proportion` to the sum of all the propotions.
* If none of the proportions are given, all proportions are assumed to be equal.
* If some of the proportions are missing, any missing proportions are set to the average of all those specified explicitly.
* If a stake pool is mentioned multiple times, those proportions as determined above are added together.
* When exporting proportions, order is not considered important but for readability should be in descending order by proportion, with the first proportion normalised to 1 (to avoid privacy risk of using actual delegation amounts).

For this specification to be fully implemented by the wallet or exchange itself, it should be possible to do at least these two things, corresponding to both *import* and *export* of stake allocation:

* upon *receiving* a staking URI, invoke a UI to allocate stake in the proportion indicated by the URI (from a single wallet, if supported)
* upon request from the user, format that user's stake allocation as a compliant URI suitable for copying & *sending*.

## Rationale

Since specific plans for "Stake Pool Portfolios" have not been announced (to the author's knowledge), nor have SPOs or delegators been told they will be able to design their own portfolios (except in videos where this idea is discussed as a conjecture), without an alternative the community would have to wait for both software support and "official" portfolios to be curated and offered from a centralised source.

In the meantime, there would be little practical alternative to the current system of:

* large pools maintaining delegation based on mainly on historical position at the top of lists ranked effectively by stake volume, or users following historically significant branding, even if a pool is saturated;
* small pools struggling to be noticed by distinctiveness or popularity on centralised platforms like Twitter and YouTube, sometimes offering exotic or unsustainable incentives to attract delegation.

We offer this rationale how URI-based "crowdsourced" portfolios will provide better results, according to these linking scenarios:

* Current wallet implementations allow wallets to link to pool web sites, but with a means for a browser or mobile app to follow a URI they will also be able to **go in the other direction**.
* The pool web site itself is the richest source of information about a pool's offering, and a URI ensures that information can be **easily transferred** to a user's delegation preference.
* Links **sent between third parties** will allow users and special interest groups to share suggested stake allocations with others by copy & pasting a link, through messaging & social networking.
* Links **generated from the wallet itself** can promote staking strategies that *anyone* determines to be useful: practically, economically, or socially.

...with these benefits for each part of the Cardano staking ecosystem:

* **small pools** : making it easier for potential delegators to find individual pools, while pool ranking sites may always favour the most heavily delegated pools (even when saturated, since many users simply follow brand recognition) and those with the greatest (now impassable) numbers of produced blocks
* **medium sized pools** : supporting inclusion in third-party delegation lists, therefore helping users find delegation without the prejudice of ranking algorithms advantageous only to the K largest stake pools (see [CIP: Non-Centralizing Rankings](https://github.com/shawnim/CIPs/blob/stake_aware_rankings/CIP-ShawnMcMurdo-NonCentralizingRankings/CIP-ShawnMcMurdo-NonCentralizingRankings.md))
* **large pools** : providing to superfluous delegators a simple & effective exit strategy when nearing or passing the saturation point (currently done mostly through the error-prone, easily subverted medium of social networking)
* **communities of pools** : i.e. special interest, self-organising, union-formed, or democratically established peer groups, with any of these criteria and more:
    * merit-based (community or infrastructure contribution)
    * community-based (geographical, technological, or other affiliation)
    * need-based (to help the smallest pools achieve block eligibility / sustainability)
    * charity-based (with verified humanitarian distribution of rewards)
* **automation & integration** : allowing portfolio links to be generated through novel means by a greater variety of new & third party web sites, scripts & software tools, and checking real and hypothetical portfolios for past results and anticipated performance
* **delegators** : having an alternative to picking only the "top of the boards," often losing rewards due to inevitable pool saturation... eventually having a rich ecosystem of alternatives beyond whatever staking portfolios may be curated & integrated into the wallet by central authorities.

### Alternate designs

A developer suggested using a JSON file instead of a URI, which the author believes is not acceptable as a universal recommendation:

* HTTP `Content-Disposition:` headers sent with any downloaded file, as well as file extensions & MIME types, often disrupt that file's interpretation by the system or application: in this case creating a dead end from the user experience that wallet or exchange web site developers would not be able to prevent.
* The generally private nature of this data would lead to issues of confidentiality and censorship, for which the `*.torrent` file specification eventually developed the `magnet:` URI protocol as an alternative: hence the similar URI based solution in this case.
* The simplest, most common use case of pool owners and supporters being able to easily construct a single pool reference, without access to specialised knowledge or resources to post a JSON file (e.g. as one can for a YouTube link from a video ID), would be defeated by *only* allowing JSON data.

JSON files would be a useful portfolio format in addition to the URI as long as developers and users remain aware of the limitations above.  The portfolio specification rules above could also apply to standards for building & interpreting such a JSON file. Therefore I would leave it to the developer community whether JSON processing or syntax should be a part of this CIP or submitted as feature requests for the relevant wallet software.

## Backwards compatibility

This proposal does not break backwards compatibility because it is an offchain change.

## Reference implementation

The URI syntax above has been chosen to follow the same general scheme as the Yoroi wallet payment link URI scheme discussed here: ([implement uri scheme on yoroi frontend #511](https://github.com/Emurgo/yoroi-frontend/pull/511)).  The two types of URIs will easily coexist because only the stake URI links contain an extra `//stake` authority component.

A simpler format was also offered here ([FR: Daedalus payment URLs](https://github.com/input-output-hk/daedalus/issues/883) #883 [comment](https://github.com/input-output-hk/daedalus/issues/883#issuecomment-384121619) (2018-04)), suggesting the need for a staking URI scheme, but only as an aside to consideration of a payment URI syntax, and without the means to accommodate multiple staking addresses.

### Copyright

© 2020 Robert Phair (22 September 2020).  This CIP is licensed under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode) license.