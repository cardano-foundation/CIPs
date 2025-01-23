---
CIP: 142
Title: Cardano dApp-Wallet Network Magic Extension
Status: Draft
Category: Wallets
Authors:
  - Steven Johnson <steven.johnson@iohk.io>
  - Nathan Bogale <nathan.bogale@iohk.io>
Implementors:
  - Lace <https://www.lace.io/>
Discussions:
Created: 2024-01-17
License: CC-BY-4.0
---

## Abstract

This CIP extends CIP-0030 to provide functionality for dApps to determine the specific network magic number of the connected Cardano network. While CIP-0030's `getNetworkId()` allows distinguishing between mainnet and testnet, this extension enables dApps to identify specific test networks through their magic numbers.

## Motivation: why is this CIP necessary?

Currently, CIP-0030 only provides a way to distinguish between mainnet (1) and testnet (0) through the `getNetworkId()` function. However, there are multiple test networks in the Cardano ecosystem (preview, preprod, etc.), each with its own magic number. dApps often need to know the specific test network they're connected to for proper configuration and interaction. This extension addresses this limitation by providing access to the network magic number.

## Specification

### Extension Identifier

This extension uses the following TEMPORARY identifier:
```ts
{ "cip": XXXX }
```

### API Extension

When this extension is enabled, the following function is added to the API under the `cipXXXX` namespace:

#### `api.cipXXXX.getNetworkMagic(): Promise<number>`

Errors: `APIError`

Returns the magic number of the currently connected network. For example:
- Mainnet: 764824073
- Preview Testnet: 2
- Preprod Testnet: 1
- Custom Testnet: (other values)

This function will return the same value unless the connected account changes networks.

Example usage:
```typescript
const api = await window.cardano.lace.enable({
  extensions: [{ cip: XXXX }]
});

const magic = await api.cipXXXX.getNetworkMagic();
console.log(`Connected to network with magic number: ${magic}`);
```

### Error Handling

The function uses the existing `APIError` type from CIP-0030 with the following error codes:
- `InvalidRequest` (-1): If the request is malformed
- `InternalError` (-2): If an error occurs while retrieving the magic number
- `Refused` (-3): If access to the magic number is refused
- `AccountChange` (-4): If the account has changed

## Rationale: how does this CIP achieve its goals?

### Why a New Extension?

While CIP-0030's `getNetworkId()` provides basic network identification, the growing Cardano ecosystem requires more specific network identification, especially for development and testing purposes. This extension:

1. Maintains backward compatibility by not modifying existing CIP-0030 functionality
2. Uses explicit namespacing to avoid conflicts
3. Provides a simple, focused solution to a specific need

### Design Decisions

1. **Explicit Namespacing**: The extension uses the `cipXXXX` namespace to clearly separate its functionality from the base CIP-0030 API.
2. **Promise-based API**: Follows CIP-0030's pattern of returning Promises for consistency.
3. **Reuse of Error Types**: Leverages existing error types from CIP-0030 to maintain consistency.

## Path to Active

### Acceptance Criteria

- [ ] Implementation by at least one wallet provider
- [ ] No reported conflicts with other CIP-0030 extensions


## Backwards Compatibility

This extension is fully backward compatible with CIP-0030. It:
- Does not modify any existing functionality
- Is opt-in through the extensions mechanism
- Uses its own namespace

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode). 