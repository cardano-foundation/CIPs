---
CIP: HeptaSean-DomainValidation
Title: Domain Validation for Cardano Addresses
Authors: Benjamin Braatz <bb@bbraatz.eu>
Comments-URI: https://forum.cardano.org/t/cip-draft-domain-validation-for-cardano-addresses/106328
Status: Draft
Type: Process
Created: 2022-08-21
License: CC-BY-4.0
---

## Abstract
This Cardano Improvement Proposal (CIP) specifies a process, by which a
relation between Cardano addresses and Domain Name System (DNS) domains can
be established.
Such a relation can be used in both directions:
Wallet apps can allow to discover addresses based on given domains and they
can also annotate given addresses with domains found for them.

## Motivation
Different proposals have been made to, on one hand, increase the confidence
that the receive address is the correct one when sending transactions, on
the other hand, make discovery and input of addresses in wallet apps
easier.

For example, [ADA Handles](https://adahandle.com/) can be used in some
wallet apps instead of an address.
[adadomains.io](https://www.adadomains.io/) is another project with a
similar goal.
But these solutions are not decentralised and depend on the projects behind
them continuing their work.

This CIP proposes a decentralised process for relating Cardano addresses
to DNS domains and validating these relations in both directions.
This relates Cardano addresses to the established identities of projects,
organisations, and companies given by the domains they own and manage.

Moreover, the tokens used to define the relation from addresses to domains
can be minted by the owners of the addresses themselves.
This leaves the full control of the process with these owners and does not
give it to commercial entities, which may or may not continue to operate
and may or may not exploit a monopolistic position regarding the provision
of identities for addresses on the Cardano blockchain.

## Specification

### Domain Tokens
In the direction from a Cardano address to a DNS domain, the relation is
established by Cardano native tokens with an asset name of `Domain`
(`446f6d61696e` as hexadecimal bytes) and metadata attached to them in
their minting transactions.

These tokens are meant to be minted by the owner of the address(es) and the
domain(s) – or someone acting on their behalf.
Therefore, they will have varying policy IDs and they are to be found only
by the asset name.

Like, for example, in
[CIP 25](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0025),
only the metadata attached to the latest minting transaction for the same
combination of policy ID and asset name must be considered, so that it can
be overwritten by newer minting transactions – even without sending the
token to the target address(es).

If, however, `Domain` tokens with different policy IDs are found at an
address, the metadata found for all of them, must be taken into account.

The domain tokens are only used as containers for or pointers to data – the
domain names – in this CIP.
They do not convey ownership of the domain and anyone can mint a token
claiming a connection to any domain.
It is the purpose of the validation in later sections to ensure the truth
of these claims.

This also means that it doesn't necessarily make sense to use time-locked
or even Plutus policies for them.
A policy with only constraints on the public key hash(es) is probably
enough, but this CIP does not prohibit more complicated policies.

### Domain Token Metadata
The `transaction_metadatum_label` for the DNS domains recorded in the
metadata of `Domain` tokens shall be registered as `53` (the standard port
number of DNS):

| transaction_metadatum_label | description  |
| --------------------------- | ------------ |
| 53                          | DNS Domain   |

The metadatum at this label is a single UTF-8 string – the domain that is
represented by this token, in JSON representation:
```json
{ "53": "example.org" }
```

Since strings in the metadata of Cardano transactions are restricted to 64
bytes, this domain is also restricted to 64 bytes.

The domain must be a DNS domain name as specified in
[RFC 1034](https://datatracker.ietf.org/doc/html/rfc1034) and following.
For internationalised domain names as specified in
[RFC 5890](https://datatracker.ietf.org/doc/html/rfc5890) and following,
the Punycode encoding of
[RFC 3492](https://datatracker.ietf.org/doc/html/rfc3492) has to be used.

### DNS Validation
The first method for establishing the relation in the opposite direction –
from a DNS domain to Cardano addresses – is realised by TXT records in DNS
itself as specified in
[RFC 1035](https://datatracker.ietf.org/doc/html/rfc1035).

We use TXT records at `_addresses._cardano.` subdomains such as, for
example, `_addresses._cardano.example.org`.
Using an underscore `_` at the beginning of a subdomain for such special
purposes to avoid clashes with subdomains used for other purposes is a
well-known technique used by a lot of network standards.
The `_addresses.` subsubdomain is used to allow other processes and CIPs to
later also use `_cardano.` for other purposes.

Each TXT record contains exactly one Cardano address without any additional
content.
Since the DNS allows multiple TXT records for a (sub)domain, we can relate
an arbitrary number of addresses with a domain with this approach.

### HTTP(S) Validation
The second method for establishing the relation from a DNS domain to
Cardano addresses is realised by JSON documents that can be obtained from
well-known URIs as specified in
[RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615).

The files should be obtainable from the path
`/.well-known/cardano/addresses.json` at the domain.
This leads, for example, to the URLs
`http://example.org/.well-known/cardano/addresses.json` and
`https://example.org/.well-known/cardano/addreses.json`.
If HTTPS is available on the web server (it should be), the HTTP URL may,
but does not have to be a redirect to the HTTPS URL.

The JSON document at this URL has the following structure:
```json
[ { "address": "addr1…",
    "Comment": "<Purpose of this address>" },
  { "address": "addr1…",
    "Comment": "<Purpose of this address>" } ]
```
It is a list of JSON objects, which must have an `"address"` field and may
have arbitrary additional fields.

### Discovery and Verification of Relations
A wallet app or other tool that discovers and verifies relations between
Cardano addresses and DNS domains must proceed as follows:

If a Cardano address is given:
* Find all domains related to it by `Domain` tokens as given below.
* For all of these domains, find all addresses related to them by DNS
  and/or HTTP(S) as given below.
* The result are all domains that point back to the given address.
* Domains *not* pointing back to the given address *must* be ignored.

If a DNS Domain is given:
* Find all addresses related to it by DNS and/or HTTP(S) as given below.
* For all of these addresses, find all domains related to them by `Domain`
  tokens as given below.
* The result are all addresses that point back to the given domain.
* Addresses *not* pointing back to the given domain *must* be ignored.

For a Cardano address, all related domains are found by:
* All tokens with an asset name of `Domain` (`446f6d61696e`) that are
  currently at an unspent transaction output (UTxO) of that address are
  searched.
* For these tokens, the latest minting transaction with associated metadata
  is determined.
* For these minting transactions, the respective domain in the metadata is
  added to the set of related domains.

For a DNS domain, all related addresses are found by:
* A DNS query for TXT records at the subdomain `_addresses._cardano` of the
  given domain is made.
  If TXT records are found, all addresses in these records are considered
  DNS-related addresses.
* A HTTP(S) request is made to the path
  `/.well-known/cardano/addresses.json` at the given domain.
  If a JSON file is obtained, all addresses given in this JSON file are
  considered HTTP(S)-related addresses.
* If both, HTTP(S)-related addresses and DNS-related addresses are found,
  only their intersection is the set of related addresses.
  If one of the sets is found, it is the set of related addresses.
  If none is found, the set of related addresses is empty.

If the relation is established in both directions, applications can give a
rating to the verification, for example, one star for DNS, one for HTTP,
and one for HTTPS for a maximum of three stars.

If possible, applications should give all related domains for a given
address and all related addresses for a given domain and allow to choose
between them where appropriate.

Applications can display additional metadata given in the JSON files
obtained by the HTTP(S) validation method.

## Rationale

### Simplicity
At most decision points, we have opted for simplicity to encourage as many
projects, organisations, and people as possible to adopt this without the
need for exceptional expertise to implement it.

The `Domain` tokens contain just the domain name of one domain as a string
and nothing more, which reduces the space needed on-chain for these
metadata (and the transaction fees for minting the tokens).
If multiple domains are needed, the owner can easily mint `Domain` tokens
under different policies to achieve this.

The information in the TXT records of the DNS validation method are just
the addresses and nothing more.

Only the JSON files of the HTTP(S) validation method contain additional
metadata.
These can, in most cases, be modified most easily.
Thus, it is sensible to have additional metadata at this place.

### Scalability
Businesses like exchanges or shops often use customer-specific receive
addresses.
Validating all of them by the process of this CIP could lead to very large
sets of related addresses for the main domain.

An easy way to handle this is to use subdomains to group related addresses,
for example by purpose, customer group, individual customers, or by time.

Organisations can also choose to only validate their main addresses used
over an extended period of time by both methods, while the additional
addresses are only validated by HTTP(S) (on a different subdomain, so that
the requirement is still fulfilled that DNS- and HTTP(S)-related addresses
coincide), where the management can easily be automated through standard
server-side web programming methods.

### Security
The process validates that the person who decides to mint and/or send a
token containing a DNS domain name to a specific Cardano address also
controls the DNS and/or HTTP(S) server for that domain.

Proving the control of a domain by TXT records in DNS and by resources at a
`/.well-known` path over HTTP(S) is used and considered sufficient in a lot
of successful protocols and applications:
* Let's Encrypt use both techniques in their Automatic Certificate
  Management Environment, specified in
  [RFC 8555](https://datatracker.ietf.org/doc/html/rfc8555#section-8.3), to
  ascertain that a domain is controlled by a server and a TLS certificate
  can be issued for it.
* Sender Policy Framework (SPF), specified in
  [RFC 7208](https://datatracker.ietf.org/doc/html/rfc7208#section-3),
  DomainKeys Identified Mail (DKIM), specified in
  [RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376#section-3.6.2),
  and Domain-based Message Authentication, Reporting, and Conformance
  (DMARC), specified in
  [RFC 7489](https://datatracker.ietf.org/doc/html/rfc7489#section-6.1),
  are standards for validating mail origins, which all use TXT records in
  DNS to give authoritative information about the policies of a domain
  regarding mail originating from that domain.
* As further examples, [Google](https://support.google.com/a/answer/183895)
  and [dnswl.org](https://www.dnswl.org/) also use TXT records to validate
  control of a domain.

### Unsolicited `Domain` Tokens
A third party could mint a token with an unrelated domain and send it to an
address in an unsolicited transaction.
If this third party also controls the DNS/HTTP(S) servers of that domain,
they could also achieve the validation process being successful.

Additional methods to remedy this, for example signatures by all claimed
addresses on the token or its minting transaction, would have sacrificed
too much of the simplicity of the approach.
Existing projects like [ADA Handle](https://adahandle.com/) also do not
remedy unsolicited sending of identifiers to an address.

The risk is acceptable, since the critical use case is the other direction:
A user wants to send to a specific project, organisation, or shop, for
which the domain is known and validate that the address belongs to it.
And this use case is not affected by unsolicited tokens, but only by
attackers gaining control over the DNS/HTTP(S) servers of the project,
organisation, or shop.

Sending an unsolicited `Domain` token can only redirect transactions that
people wanted to send to the domain controlled by the attacker to the
receiver of the unsolicited token, which does not seem to be a very
sensible attack vector.

A small risk remains that the receiver of the token may be defamed by the
attacker's domain appearing next to the receiver's legitimate domains, when
an application shows all validated domains for an address.

Address owners should monitor such unsolicited transactions and send such
tokens to unused addresses or back to the sender.

## Reference Implementation and Example
A reference implementation of the processes described in [Discovery and
Verification of Relations](#discovery-and-verification-of-relations) can be
found in the accompanying Python script
[cardano-domain-validation.py](cardano-domain-validation.py).
For the queries to the Cardano blockchain, it uses
[koios.rest](https://api.koios.rest/).

### Example Preparation
We use two example domains – the author's domains `bbraatz.eu` and
`heptasean.de` – that have been configured for domain validation as
specified in this CIP:
```console
$ dig _addresses._cardano.bbraatz.eu TXT
_addresses._cardano.bbraatz.eu.	3600 IN	TXT	"addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5"
_addresses._cardano.bbraatz.eu.	3600 IN	TXT	"addr1q9wvykt8vpvgrqjr9lgm8d9dstgl3h2wesdrqlxa4gqdv62wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysv6v74x"
_addresses._cardano.bbraatz.eu.	3600 IN	TXT	"Not an address"
$ curl https://bbraatz.eu/.well-known/cardano/addresses.json
[ { "address": "addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5" },
  { "address": "addr1q8fe7mx9xdpr063tkp8k5r65psy9p469az04rh86epcaxz2wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ys3ufz2q" },
  { "address": "Not an address" } ]
```
For this domain, we have information in DNS as well as in JSON via HTTPS.
One address – `addr1…jatmn5` – is in both, while one is only in DNS and one
only in the JSON file.
The latter two should be ignored by implementations, since DNS and HTTP(S)
validation have to coincide.
The entries that are not addresses should also be ignored.
```console
$ dig _addresses._cardano.heptasean.de TXT
$ curl https://heptasean.de/.well-known/cardano/addresses.json
[ { "address": "addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5",
    "Comment": "Main Wallet" },
  { "address": "addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0xxllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q",
    "Comment": "Token Trading" },
  { "address": "addr1qyjwqxz8sry4ul522x5zfp4na2t5m4qkuxtpzw0tll99a8zwlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0yscp2j47",
    "Comment": "No Domain token" } ]
```
For this domain, we do not have information in DNS, but only in JSON via
HTTPS.
This should be accepted by implementations, but result in a lower rating.
The JSON file makes use of the additional keys to give comments for
addresses.
Two addresses – `addr1…jatmn5`, already configured for the other domain,
and `addr1…whjr9q` – will be valid, while the third will not get a
corresponding domain token and should, hence, be ignored by
implementations.

We find `Domain` tokens for our example domains at the corresponding example
addresses:
```console
$ curl "https://api.koios.rest/api/v0/address_assets?_address=addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0xxllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q&asset_name=eq.446f6d61696e"
[ { "policy_id": "2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417",
    "asset_name": "446f6d61696e",
    "quantity": "1" } ]
$ curl "https://api.koios.rest/api/v0/asset_info?_asset_policy=2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417&_asset_name=446f6d61696e&select=minting_tx_metadata"
[ { "minting_tx_metadata":
    [ { "key": "53",
        "json": "heptasean.de" },
      { "key": "721",
        "json":
        { "2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417":
          { "Domain":
            { "name": "Domain: heptasean.de",
              "image": […] } } } } ] } ]
```
Since this address is only connected to the second domain `heptasean.de`,
we only find one token there for that same domain.
As you can see, there are also standard NFT metadata included, so that the
domain token can be identified (and looks nice) in wallet apps not
supporting this present CIP.
This is not required by this specification, though.
```console
$ curl "https://api.koios.rest/api/v0/address_assets?_address=addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5&asset_name=eq.446f6d61696e"
[ { "policy_id": "4f2aebe9413c5b7b461aa9faa47e5a0664dfc0d3d7d33f1576d775bb",
    "asset_name": "446f6d61696e",
    "quantity": "1" },
  { "policy_id": "9dc5bc52956b0aae62a40ab0628951fb26cf3ebc27fdfe849b1fa142",
    "asset_name": "446f6d61696e",
    "quantity": "1" },
  { "policy_id": "2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417",
    "asset_name": "446f6d61696e",
    "quantity": "1" } ]
$ curl "https://api.koios.rest/api/v0/asset_info?_asset_policy=4f2aebe9413c5b7b461aa9faa47e5a0664dfc0d3d7d33f1576d775bb&_asset_name=446f6d61696e&select=minting_tx_metadata"
[ { "minting_tx_metadata":
    [ { "key": "53",
        "json": "bbraatz.eu" },
      { "key": "721",
        "json":
        { "4f2aebe9413c5b7b461aa9faa47e5a0664dfc0d3d7d33f1576d775bb":
          { "Domain":
            { "name": "Domain: bbraatz.eu",
              "image": […] } } } } ] } ]
```
On this address, we find three `Domain` tokens.
The first token represents the connection to the first domain `bbraatz.eu`.
```console
$ curl "https://api.koios.rest/api/v0/asset_info?_asset_policy=9dc5bc52956b0aae62a40ab0628951fb26cf3ebc27fdfe849b1fa142&_asset_name=446f6d61696e&select=minting_tx_metadata"
[ { "minting_tx_metadata":
    [ { "key": "53",
        "json": "example.com" },
      { "key": "721",
        "json":
        { "9dc5bc52956b0aae62a40ab0628951fb26cf3ebc27fdfe849b1fa142":
          { "Domain":
            { "name": "Domain: example.com",
              "image": […] } } } } ] } ]
```
The second token claims that this address also belongs to the domain
`example.com`, but on that domain we will neither find a DNS nor a HTTP(S)
validation, so that implementations should ultimately ignore it.
```console
$ curl "https://api.koios.rest/api/v0/asset_history?_asset_policy=2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417&_asset_name=446f6d61696e&select=minting_txs"
[ { "minting_txs":
    [ { "tx_hash": "8ef972221023f0c78dfa31c480e48f3a344beb633319e49e72ddf6823a48e36f",
        "block_time": 1660482520,
        "quantity": "1",
        "metadata":
        [ { "key": "53",
            "json": "heptasean.de" },
          { "key": "721",
            "json":
            { "2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417":
              { "Domain":
                { "name": "Domain: heptasean.de",
                  "image": […] } } } } ] },
      { "tx_hash": "a2d246cc72682900d264478e82d3ce4aeb35a01683699744f6043791d95d8a88",
        "block_time": 1660482379,
        "quantity": "1",
        "metadata":
        [ { "key": "53",
            "json": "example.org" },
          { "key": "721",
            "json":
            { "2ca754177885f5c0431e38d216a26ded1e35aa3a6d6dd163ffd41417":
              { "Domain":
                { "name": "Domain: example.org",
                  "image": […] } } } } ] } ] } ]
```
We have already seen the third token on the other address `addr1…whjr9q`.
Looking at the minting history, we can see that both instances were minted
with different transactions, where the later transaction changed their
metadata to the one we see now, pointing to the domain `heptasean.de`.
The first minted token (which incidentally was the one sent to
`addr1…whjr9q`) originally pointed to the domain `example.org`.
Neither CIP 25 nor this CIP care about the concrete transaction history of
a specific instance of a token, but give the metadata in the latest minting
transaction for any token with that combination of policy ID and asset
name, which is also what the Koios API will give us by default.

### Example in Reference Implementation
When executing the reference implementation on our example domains, we get:
```console
$ python3 cardano-domain-validation.py bbraatz.eu
★★★ addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5
$ python3 cardano-domain-validation.py heptasean.de
★★☆ addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5
    Comment: Main Wallet
★★☆ addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0xxllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q
    Comment: Token Trading
```
For the first domain – `bbraatz.eu` – it gives us the only configured
address – `addr1…jatmn5` – with a rating of 3/3.
For the second domain – `heptasean.de` – it gives us both configured
addresses with the additional comments given as metdata for them and a
rating of 2/3, since we have not used DNS validation for these.

Vice versa, when executing the implementation for our example addresses, we
get:
```console
$ python3 cardano-domain-validation.py addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0xxllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q
★★☆ heptasean.de
    Comment: Token Trading
$ python3 cardano-domain-validation.py addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5
★★★ bbraatz.eu
★★☆ heptasean.de
    Comment: Main Wallet
```
For the first address – `addr1…whjr9q` – we only get the second domain
linked to it with its comment and rating.
For the second address – `addr1…jatmn5` – it gives us both domains with
their different ratings and the additional comment metadata for the second
one.

## Path to Active

### Usage
In order for this CIP to become active, it should be implemented by
relevant wallet apps and Cardano blockchain explorers and be used by
relevant projects and/or organisations to validate their addresses.

### Registrations
The `transaction_metadatum_label` `53` from the section
[Domain Token Metadata](#domain-token-metadata) has to be registered in the
registry according to
[CIP 0010](https://github.com/cardano-foundation/CIPs/tree/master/CIP-0010).

The well-known URI `/.well-known/cardano` from the section
[HTTP Validation](#http-validation) has to be registered according to
[RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615#section-3.1).
This registration can also be reused for other CIPs that need data at a
well-known location on a web server.

## Backwards Compatibility
Since this is a newly proposed process, there are no backwards
compatibility issues.

## Copyright
This CIP is licensed under
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
