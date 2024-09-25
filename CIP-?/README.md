# CIP-?: NFT and Token Authentication

---
- **CIP**: ?
- **Title**: NFT and Token Authentication
- **Authors**: Emir Olgun <emirolgun@gmail.com>
- **Discussions-To**: https://github.com/littlefish-foundation/CIPs/discussions
- **Status**: Proposed
- **Created**: 2024-09-17
- **License**: CC-BY-4.0
---

## Abstract
This CIP proposes a standard for using Fungible and Non-Fungible Tokens (NFTs) as authentication tokens on the Cardano blockchain, enabling decentralized Single Sign-On (SSO) capabilities. It defines a metadata structure for these authentication NFTs, providing a framework for secure, verifiable, and decentralized authentication mechanisms.

## Motivation
As blockchain technology continues to evolve, there's a growing need for decentralized authentication systems that leverage the inherent security, transparency, and immutability of distributed ledgers. Traditional authentication mechanisms often rely on centralized authorities and are susceptible to single points of failure and security breaches. By using NFTs as authentication tokens, we can create unique, verifiable credentials secured by the blockchain, enabling users to authenticate across multiple platforms without relying on centralized identity providers. This approach enhances user privacy, data control, and aligns with the decentralized ethos of blockchain technology.

## Specification
### Metadata Structure
The proposed metadata structure for authentication NFTs version 1.0.0 is as follows:

```json
{
  "721": {
    "<policy_id>": {
      "<asset_name>": {
        "name": "String",
        "image": "String (IPFS URI)",
        "mediaType": "String",
        "description": "String",
        "files": [
          {
            "name": "String",
            "mediaType": "String",
            "src": "String (IPFS URI)"
          }
        ],
        "sso": {
          "version": "String (Semantic Versioning)",
          "uniqueIdentifier": "String",
          "issuer": "String",
          "issuanceDate": "String (ISO 8601)",
          "expirationDate": "String (ISO 8601)",
          "isTransferable": "Integer (0 or 1)",
          "tiedWallet": "String (Stake Address)",
          "isMaxUsageEnabled": "Integer (0 or 1)",
          "maxUsage": "Integer",
          "isInactivityEnabled": "Integer (0 or 1)",
          "inactivityPeriod": "String",
          "role": ["String"]
        }
      }
    }
  }
}
```
### Field Descriptions
- **name:** The name of the authentication token.
- **image:** IPFS URI of the token's image.
- **mediaType:** Media type of the image file (e.g., "image/png").
- **description:** A brief description of the token's purpose.
- **files:** An array of additional files associated with the token.
- **name:** The name of the file.
- **mediaType:** Media type of the file.
- **src:** IPFS URI of the file.
- **sso:** Object containing SSO-specific metadata.
	- **version:** Version of the SSO metadata structure (e.g., "1.0.0").
	- **uniqueIdentifier:** A unique identifier for the token.
	- **issuer:** Name or identifier of the issuing authority.
	- **issuanceDate:** Date and time when the token was issued (ISO 8601 format, e.g., "2023-01-01T00:00:00Z").
	- **expirationDate:** Date and time when the token expires (ISO 8601 format).
	- **isTransferable:** Integer indicating whether the token can be transferred (0 = No, 1 = Yes).
	- **tiedWallet:** Stake address of the wallet the token is tied to if non-transferable.
	- **isMaxUsageEnabled:** Integer indicating whether there's a limit on token usage (0 = No, 1 = Yes).
	- **maxUsage:** Maximum number of times the token can be used.
	- **isInactivityEnabled:** Integer indicating whether there's an inactivity period (0 = No, 1 = Yes).
	- **inactivityPeriod:** Period of inactivity after which the token becomes invalid.
	- **role:** Array of roles associated with the token (e.g., ["admin", "user"]).

### Notes on Implementation
- **Unique Identifier:** The uniqueIdentifier field can be used to reference external systems or provide an additional layer of uniqueness beyond the policy_id and asset_name.
- **Date Formats:** All dates should be in ISO 8601 format and in UTC time zone to ensure consistency.
- **Integer Flags:** The integer fields used as flags (isTransferable, isMaxUsageEnabled, isInactivityEnabled) should be either 0 or 1, representing false and true respectively.
Rationale
- **Off-Chain Data:** Information such as maxUsage and inactivityPeriod need be tracked off-chain and compared with the metadata.

The proposed metadata structure extends existing NFT metadata standards to include authentication-specific information without conflicting with current practices. By encapsulating authentication data within the sso object, we maintain compatibility and avoid namespace collisions. The fields included in the sso object provide essential information required for authentication mechanisms, such as validity periods, usage limits, and role-based access control.

Using NFTs as authentication tokens leverages the blockchain's properties to ensure uniqueness, verifiability, and immutability of credentials. The inclusion of fields like tiedWallet allows for tokens that are bound to specific wallets, enhancing security for non-transferable tokens.

## Backwards Compatibility
This CIP introduces a new metadata structure that is compatible with existing NFT standards. Systems that do not implement this CIP can safely ignore the sso object in the metadata without affecting their operations.

## Reference Implementation
An example implementation of minting an authentication NFT with the specified metadata:

```json
{
  "721": {
    "f1f2f3...": {
      "AuthToken": {
        "name": "Authentication Token",
        "image": "ipfs://Qm...abc",
        "mediaType": "image/png",
        "description": "An authentication token for accessing XYZ service.",
        "files": [
          {
            "name": "Terms of Service",
            "mediaType": "application/pdf",
            "src": "ipfs://Qm...def"
          }
        ],
        "sso": {
          "version": "1.0.0",
          "uniqueIdentifier": "token-12345",
          "issuer": "XYZ Company",
          "issuanceDate": "2023-01-01T00:00:00Z",
          "expirationDate": "2023-12-31T23:59:59Z",
          "isTransferable": 0,
          "tiedWallet": "stake1u...xyz",
          "isMaxUsageEnabled": 1,
          "maxUsage": 100,
          "isInactivityEnabled": 1,
          "inactivityPeriod": "P30D",
          "role": ["user", "premium"]
        }
      }
    }
  }
}
```
### Verification steps for an authentication system:

- **Retrieve the NFT Metadata:** Use the policy_id and asset_name to fetch the token's metadata from the blockchain.
- **Validate the Issuer:** Confirm that the issuer field matches a trusted issuing authority.
- **Check Expiration:** Ensure the current date and time are before the expirationDate.
- **Verify Ownership:** If isTransferable is 0, confirm that the token is held in the wallet specified by tiedWallet.
- **Enforce Usage Limits:** If isMaxUsageEnabled is 1, track and ensure the token's usage does not exceed maxUsage.
- **Enforce Inactivity Limits:** If isInactivityEnabled is 1, track the last usage timestamp and invalidate the token if the period exceeds inactivityPeriod.
- **Apply Role-Based Access:** Use the role array to grant or restrict access to resources.
### Security Considerations
- **Private Key Security:** Implementers must ensure that private keys associated with wallets holding authentication NFTs are securely stored and managed.
- **Metadata Validation:** Systems must rigorously validate the token's metadata, including checking issuer authenticity, expiration dates, and other constraints before granting access.
- **Non-Transferable Tokens:** If isTransferable is 0, systems must verify that the token resides in the wallet specified by tiedWallet. However, since tokens can be transferred without consent in UTXO-based blockchains, additional measures (e.g., off-chain checks) are required to enforce non-transferability.
- **Usage Tracking:** Usage limits (isMaxUsageEnabled) and inactivity periods (isInactivityEnabled) require off-chain state management. Implementers must ensure secure and tamper-proof tracking mechanisms to prevent abuse.
- **Replay Attacks:** Systems should be designed to prevent replay attacks where a captured authentication token is reused maliciously.
- **Revocation:** There is no native mechanism for revoking NFTs. Implementers should plan for token revocation strategies, such as blacklisting certain tokens or incorporating expiration dates.
## References
- CIP-25: [NFT Metadata Standard](https://cips.cardano.org/cip/CIP-25)
- ISO 8601: [Date and Time Format Standard](https://www.iso.org/iso-8601-date-and-time-format.html)
- Semantic Versioning: semver.org
## Copyright
[This CIP is licensed under CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).