---
CIP: ????
Title: Cardano URIs - Authentication
Category: Wallets
Status: Proposed
Authors:
  - Adam Dean <adam@crypto2099.io>
  - Trym Bruset <trym.bruset@iohk.io>
Implementors: [ ]
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/?
Created: 2024-06-15
License: Apache-2.0
---

## Abstract

This CIP extends [CIP-13] to provide a `web+cardano:` URI structure that can
initiate a session authentication workflow with the wallet of the user. This
allows for cryptographic _Proof of Attendance_ or interaction as a unique
challenge may be presented to a user at a location (kiosk, event, etc.) and the
user's wallet may be used to pass a signature proving attendance or involvement.

## Motivation: why is this CIP necessary?

Building atop the foundation and success of [CIP-99]; this proposal aims to
define a framework standard for authenticating a user interaction through a
wallet signature.

This authentication standard allows for entities to collect user or attendee
registration information (at least an anonymized wallet address) and a proof
that the wallet completed a challenge (authenticated).

This can be helpful as protocols such as [CIP-99] result in a non-trivial
expense to issue tokens. While this authentication is possible to do
using `signData` and the Hardware Wallet Workaround<sup>TM</sup> for traditional
[CIP-30] wallet connections on desktop browsers, it is much more cumbersome for
mobile users, particularly at live events.

### Example Use Cases

* Allowing attendees at a real-world event to enter into a raffle or drawing:
    * Users scan a QR code with their mobile wallet at the event, their wallet
      authenticates to a server recording successfully registered addresses and
      providing them to the hosts to determine a winner
* Users associate their wallet with a traditional registration
    * Users registering at an event, hotel, etc. can securely authenticate their
      wallet address and the company performing registration can link the user
      to their wallet. This can then be used for rewards and "anonymized"
      authentication at future session.
* Gaming
    * Through the use of cryptographically secure authentication, a gaming
      contest can provide secure authentication for play sessions that can be
      used for determining achievements, leaderboards, and other trackable
      activities. Rewards can be issued after-the-fact based on the collected
      address and gaming activities.

## Specification

**COMING SOON<sup>TM</sup>**

## Rationale: how does this CIP achieve its goals?

Given that the goal of this CIP is to define a standard for wallet
authentication, we achieve this goal by defining a standard that works and is
useful across a variety of situations and circumstances and is documented and
supported enough to be useful.

By having a well-documented standard and showcasing support amongst ecosystem
participants (wallets); projects can build solutions upon this standard with
confidence in knowing that when it comes time for production deployments it will
"just work".

## Path to Active

### Acceptance Criteria

- [ ] Demonstrate a working MVP
- [ ] Open source an MVP Authentication Server
- [ ] Receive and implement community feedback
- [ ] Have at least one mobile wallet supporting this standard

### Implementation Plan

We will reach out to wallet providers who have already shown a willingness and
capability to implement `web+cardano:` URI solutions and develop a working
end-to-end MVP example of a user authentication and session storage flow.

## Copyright

This CIP is licensed
under [Apache-2.0](http://www.apache.org/licenses/LICENSE-2.0).

[CIP-13]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0013/README.md

[CIP-99]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0099/README.md

[CIP-30]:https://github.com/cardano-foundation/CIPs/blob/master/CIP-0030/README.md