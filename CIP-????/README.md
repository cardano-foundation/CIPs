---
CIP: XXXX
Title: Efficient Proofs for Dynamic Sets on Cardano
Status: Proposed
Category: Tools
Authors:
    - Pal Dorogi <pal.dorogi@gmail.com>
Implementors: []
Discussions:
    - https://github.com/cardano-foundation/CIPs/pull/816
Created: 2024-05-17
License: CC-BY-4.0
---

## Abstract

This Cardano Improvement Proposal (CIP) describes a solution for ensuring the uniqueness (at minting time) of dynamically minted NFTs on the Cardano blockchain. 

The solution uses a new accumulator scheme, leverages a complete binary hash tree for compact accumulation and dynamic updates which relies on a trusted Plutus script, specifically designed to perform accumulator verification.

When a user wants to mint or burn an NFT, they rebuild the tree from the blockchain (or can use any 3rd-party service provider), 
create a new root hash or accumulator for the modified (added/deleted element) tree, and a proof, and send these data to the blockchain. 

The on-chain code verifies the proof and the updated state, and if the verification is successful, the minting or burning transaction is processed.

## Motivation: why is this CIP necessary?

NFTs are unique digital assets that can represent ownership of a wide range of items, such as art, collectibles, and in-game items. One challenge with minting NFTs on the Cardano blockchain is ensuring the uniqueness of each token at minting time. When a user wants to mint an NFT using a decentralized application (dApp), the on-chain code is unable to verify that the NFT being minted with the same policy ID is unique. 
This can lead to the creation of duplicate NFTs, which can cause confusion and disputes over ownership.

This CIP aims to address this challenge by providing a solution for efficiently and securely tracking the dynamic minting and burning of NFTs on the Cardano blockchain. This will ensure that each NFT is truly unique and that ownership is properly recorded.

## Specification

### Data Structures
The solution uses the following data structures:

- Complete binary hash tree: The tree is used to accumulate the elements in the set, and to provide proofs.
- Open-interval pairs: a pair of elements, in which the first element is less than the second element, and the two elements are consecutive. The pairs are used to represent the values in the complete binary hash tree, and to enforce the uniqueness of the elements in the set.
- Accumulator: a single hash value that represents the state of the complete binary hash tree. The accumulator is stored on the blockchain, and is updated whenever an element is added or removed from the set.
- Proof: a set of hashes that allows the verification of a particular node in the complete binary hash tree, without requiring the entire tree. The proof is generated when an element is added or removed from the set, and is sent to the blockchain along with the updated accumulator.

### Key features:

- Unlike traditional hash Merkle trees, the solution stores values in every node.
- These values are represented as (open-interval) pairs of - consecutive elements with each node in the tree.
- Offers proofs for membership, non-membership, addition, and deletion.
- Proof size scales logarithmically with the number of elements.

> Example: Verifying the presence/absence of an element `x` in the tree `T` as a model of accumulated set `S = {x1, ..., xn}`, one must prove that a pair `(xα, xβ)`, where `xα ≺ x ≺ xβ` (absence), or either of the pairs `(xα, x)` and `(x, xβ)` (presence), are present in the `T` tree.

In addition, verifying addition of an element `x` requires proving the existence of `(xα, xβ)`, where `xα ≺ x ≺ xβ` of the tree `T` to be appended, and ensuring that the pairs `(xα, x)` and `(x, xβ)`, are present in the new updated tree `T'` while maintaining completeness. Deletion from the `T` requires similar proofs.


> Note: Open-interval pairs enforce the uniqueness of the elements by setting the initial value to some minimum and maximum bounds. For example `(xα: -Infinity, xβ: +Infinity)`.

In a username service implementation, the lower and upper bounds could be represented by lowercase letters (in lexicographical order), for example the `xα: "a"` and `xβ: "c"`, with the additional constraint that the first letter of the element must be `"b"`. This ensures that only elements starting with `"b"` are included in the interval. However, in other implementations, they could take any form that enforces the condition `xα ≺ x ≺ xβ`, such as hashes (ranging from `"0x0000...00"` to `"0xFFFF...FF"`).


### Brief Overview of Proofs

The accumulator `accT` of the tree `T` is the `hashRoot(T)`, calculated by combining the hashes of the node's value, the hashRoot of its left child, and the hashRoot of its right child: `accN = hash( hashVal(value) || hashRoot(leftChild) || hashRoot(rightChild))`, where `||` represents the concatenation of byte arrays.

> Note: Any node `N` of the tree `T` can be accumulated in the same way as above.

The proof provided by the solution consists of a compact path (minimal subtree) from the root node `Nr` to the provable node(s), ensuring that the root hash of this subtree matches the root hash of the entire tree `T`, and at least one (depends on the proof type) node's value of the provable node is included in the proof.

For example, a complex addition proof involves creating a minimal subtree from two nodes:

1. The node with value `(xα, xβ)` called `Vu`, where `xα ≺ x ≺ xβ`, proving that the element `x` does not exist in the tree.
2. The parent node `Np`, which contains the value `Vp`, the new leaf will be appended to.

> Note: to enforce completness of the tree the nodes' value contains the index `xi` that represents the size of the tree in the current state. Therefore, the appendable node's index `xi` is always half (by integer deivision) of the new size of the tree (`old_state.tree_size +/- 1` depends on the operation)

During validation, the Plutus script checks the following:
- The accumulator in the old state matches with the calculated root hash from the provided proof (minimal subtree), and the two values (`Vu` and `Vp`) provided by the users.
- The Plutus script generates three new values (`Vu'`, `Vp'` and `Vl`) from the two provided values and the element `x` to be added into the tree by:
  - Replacing the `Vu`'s `(xα, xβ)` with `(xα, x)` and
  - Replacing the `Vp`'s values if it's required (see details in the implemented proofs)
  - Creating a new leaf value `Vl` with `(x, xβ)`.
- Finally, the accumulator of the new state matches with calculated in the plutus script from the original proof, and where the two values (`Vu` and `Vp`) are replaced by the three new values during the validation process.

During the validation the value where:
1. the current node's `valHash == hashVal(Vu)`, the `hashVal` will be replaced by `Vu'` and where
2. the current nodes's `valHash == hashVal(Vp)`, the `hashVal` will be replaced with `Vp'` and one of its children will be replaced by the `hash( hashVal(Vl) || empty_hash || empty_hash)`

> Note: which children is replaced is depends on the new tree size (even-odd rule)


### Implementation

This scheme is implemented within the Cardano blockchain system. The blockchain will store only the states of the tree T, which include:

- The accumulator (root hash) of the tree T
- The operation performed (added/deleted)
- The current size of the tree and
- The element added or deleted.

The state change will be bound to and carried by an authorization token held at the relevant script address.

Each state change (element added or removed) is validated by the corresponding Plutus minting script (mint/burn). This validation process is based on the old state, the user's input as redeemer, and the provided new state by the user(s) as an inline datum of the Extended UTXO (EUTxO) containing the authorization token.

> Note: The redeemer contains the proof(s) and the required values (`Val`s) are required for minting and burning elements.

Therefore, the validation process utilizes these three parts:
- The existing old state stored on chain as an EUTxO.
- The user's provided new state as an output.
- The append or delete proof and the required Values as the user's input.

Indeed, the implementation resembles a state machine, tracking transitions from an initial state (represented by the root hash of the empty tree, which contains the initial lower and upper bounds) to various states as operations are performed on the tree.

> Note: Users can reconstruct the whole tree to any of these states using the specified transparent off-chain append and delete functions. Each state transition is validated by the blockchain system, ensuring the integrity and correctness of the tree's structure throughout its evolution. This approach provides a reliable and transparent mechanism for managing dynamic sets of elements on the Cardano blockchain.

### Complete Binary Tree vs. Minimal Subtree

- **Complete Binary Tree Data Structure**: Represents the complete structure of the tree, including Val, left and right child nodes.
- **Minimal Subtree**: Used for proofs and contains only hash values of vals, nodes and branches along the path of specific nodes.


### Node Structure

Each node in the Complete binary tree (name InmtegriTree) consists of:
- `Val`: A data structure containing information about the node, including the index of the node in the tree in level-order i.e. size of the tree (`xi`) and the  pairs of consecutive elements (as two bounds) of the open-interval (`xa` and `xb`).
- `Children`: left and right child nodes.

Typescript's example:
``` typescript

export type Val =  { xi: string; xa: string; xb: string }

export type IntegriTree = {
  val: Val;
  left: IntegriTree;
  right: IntegriTree;
}
```

> Note: the current typescript implementation of IntegriTree uses an array of Vals for efficient operations.

### Root Hash Calculation of IntegriTree

The off-chain root hash calculateion of the tree or any of its branch is calculated using the following function:
``` typescript

  /**
   * Calculates the hash for a specified node in the tree.
   * @param index - The index of the node.
   * @returns The hash for the specified node.
   */
  private hashNode(index: number): string {
    if (index >= this.elements.length) {
      return emptyHash
    }

    const val = this.elements[index]
    const leftChildIndex = 2 * index + 1
    const rightChildIndex = 2 * index + 2

    const valHash = hashVal(val)
    const leftHash = this.hashNode(leftChildIndex)
    const rightHash = this.hashNode(rightChildIndex)

    return combineThreeHashes(valHash, leftHash, rightHash)
  }
```

> Note: A compact array based structure is used for off-chain representation of the tree.

## Minimal Subtree (Proof)

The proof provided by the solution is a minimal subtree together with the required values (depends on the proofs). In other words, the minimal subtre is a path from the root node to the provable node (membership or non-membership) contains hash of the nodes' value the hash of the child not in the path down to the node and the child contains the node as path down to the provabel node.

> Note: The minimal subtree is used for proofs and contains only hash values of Vals, nodes and branches along the path of specific nodes (e.g., membership, non-membership, update, delete).

Typescript definition example of the minimal subtree (TreeProof)

``` typescript
export type TreeProof =
  | {
      // `hash` is the valHash of the Val of the node
      HashNode: { hash: string; left: TreeProof; right: TreeProof }
    }
  | {
      // `hash` is the rootHash of a node, a branch etc.
      NodeHash: { hash: string }
    }
```


This structure regenerates the exact hash of the tree as the whole IntegriTree would be hashed.

In merkle tree the leaf pairs (that contain data) are hashed up to the tree while in IntegriTree the nodes' values (`Val`) are part of the proof.
For example, for the following Proof

``` typescript
const proof = HashNode {
  hash: valHash(Val{ xi: 1, xa: "a", xb: "adam"}),
  left: HashNode {
            hash: valHash(Val{ xi: 2, xa: "adam", xb: "b"}),
            left: emptyHash,
            right: emptyHash
        },
  right: emptyHash
}
```

It's easily can be proven that "adam" is in the tree, but "aby" is not, having a `Val { xi: "1", xa: "a", xb: "adam"}` and the Proof
as the proof's `rootHash(proof)` exactly the same with the rootHash of the whole integritree, and the hash of proof contains the hash of the required proovable `Val`

### Root Hash Calculation of the minimal subtree

The root hash of the minimal subtree use similar function as in the IntegriTree, see the `aiken`'s implementation below:

``` gleam
pub fn root_hash(root: Proof) -> Hash {
  when root is {
    NodeHash { hash } -> hash
    HashNode { hash, left, right } ->
      combine_three_hashes(hash, root_hash(left), root_hash(right))
  }
}
```

### Membership and Non-Membership Proofs

IntegriTree provides proofs for both membership and non-membership of elements in the tree:

- **Membership**: If an `x` element is in the tree, there exists at least one node where either `xa = x` or `xb = x`.
- **Non-Membership**: If an element is not in the tree, there exists a node where `xa < x < xb`.

### Append and Delete Proofs

Proofs are available for appending new elements to the tree and deleting existing elements:

- **Append Proof**: If an element is not in the tree, the proof contains the non-membership (update node's) value `Vu`, the value `Vp` of the node will be the parent of the new appendable node of the new element, and the minimal subtree of the two `Val`'s nodes.
- **Delete Proof**: If an element is in the tree, the proof contains the two membership (update nodes') values the `Vu1` and `Vu2` (the `(xα, x)` and `(x, xβ)`),  and the value `Vp` the parent node of the last (in level-order) node in the tree, and the minimal subtree create from the nodes of the three values.


### Val Types of the Proof

There are two types of Vals are used with the Proof:

- **Updateable Node's (`Nu`'s)**: Nodes' val that are already part of the tree but may have their values updated.
- **Parent Node's (`Np`'s)**: Nodes' val where a new leaf will be appended to or removed from.

### Completeness Enforcement

The tree must always maintain its completeness which enforced by the sequential index of nodes in the tree.

### Technical briefs of the IntegriTree

- The tree model **`T`** representing the set **`X = {x1, ..., xn}`** is and must always be a **`Complete Binary Tree`**.
- A `Complete Binary Tree` can have an incomplete last level, as long as all the leaves in that level are arranged from left to right.
- A **node** (**`N`**) of the `T` tree has two pointers: one to its left child, and one to its right child.
- A **leaf** (**`L`**) is a node  that has two empty hashes (**`ε, ε`**) as its children.
- Every node in `T` must be assigned a sequential index **`i`** starting from **`1`**, with the root of T having index 1, and this index `i` increases by 1 whenever a new node **`Ni`** is added. The value of `i` is always equal to the number of nodes (and not the numb er of elements) in `T`.
- Therefore, the nr. of elements of the tree is always the `tree size - 1`
- The depth (**`d`**) is defined as the length of the simple path (number of edges) from the `root` node of `T` to node `N`.
- The node's index (`i`) must always be exactly double of its parent's index if it's the left child, or 2 times of the parent's index plus 1 if it's the right child.
- The integrity of `T` is ensured by the sequential index (`i`).
- Therefore the node index determines the position of any node within the 'T' tree and positions in its parent, except for the root node (as it doesn't have a parent).
  - The position of a node in the tree is determined by **`P = i - 2^d + 1`** which means it's the **`Pth`** node on level `d` of the `T` tree.
  - The **left**/**right** position within a node follows the **`even-odd`** rule:  if its index `i` is even, the child is on the left side; otherwise, it's on the right. This position is determined by **`Pn = In - 2Ip`** (`Ip` is the parent's index)  where `Pn` is 0 when the child is on the left, 1 when it's on the right, and results in an **error** otherwise.
- In order to keep track of changes in the state of the `T` tree, there are two types of nodes:
  - Updateable node (**`Nu`**): These nodes are already part of the tree, but their values will be updated sometime by an update process.
  - Parent node (**`Np`**): These are then nodes where a new leaf `L` will be appended to or the last leaf removed from.
- The right child (`Nr`) of an parent node (`Np`), must always be an empty hash, represented as **`ε`**. The left child can be either an empty hash (**`ε`**) or a leaf.

## Rationale: how does this CIP achieve its goals?

The solution described in this CIP achieves the goal of ensuring the uniqueness of NFTs minted on the Cardano blockchain by using an off-chain data structure to track the minting and burning of NFTs, and storing the hash of this data structure together with the proofs on the blockchain. This allows the on-chain code to verify the uniqueness of an NFT at minting time, without requiring the entire data structure to be stored on the blockchain.

Also, it allows anyone to independently build the off-chain data tree by retrieving on-chain minting/burning transactions. Therefore, there is no need for centralized solutions to validate the integrity of the tree, promoting decentralization and transparency within the Cardano ecosystem. Though, any - even un-trusted or adversarial -  3rd-party services can be used to be queried for a proof.

The use of IntegriTree as the off-chain data structure allows for efficient and secure tracking of the minting and burning of NFTs. IntegriTree is a new accumulator scheme that leverages a complete binary hash tree for compact accumulation and dynamic updates. 

The tree is used to accumulate the elements in the set, and to provide proofs. 
The values are represented as open-interval pairs of consecutive elements with each node in the tree. IntegriTree offers proofs for membership, non-membership, addition, and deletion, with a proof size that scales logarithmically with the number of elements.

The use of an accumulator to represent the state of the IntegriTree allows for the updated state to be verified and recorded on the blockchain in a single transaction. This simplifies the process of updating the state, and reduces the risk of errors or disputes.


## Path to Active

### Acceptance Criteria
The acceptance criteria for this CIP to become active are as follows:

- [ ] The solution described in the CIP has been implemented and tested on the Cardano blockchain.
- [ ] The implementation has been reviewed and approved by subject matter experts.
- [ ] The community has had sufficient time to review and provide feedback on the CIP and the implementation.
- [ ] Any concerns or issues raised during the review and testing process have been addressed and resolved.

## Implementation Plan


The implementation plan for this CIP is as follows:

- [ ] The solution described in the CIP will be implemented and tested - on the Cardano blockchain by the proposer of the CIP.
- [ ] The proposer will submit the implementation for review and approval by subject matter experts.
- [ ] The proposer will make the implementation and the CIP available for review and feedback by the community.
- [ ] The proposer will address and resolve any concerns or issues raised during the review and testing process.
- [ ] Once the acceptance criteria have been met, the proposer will submit a pull request to the Cardano Improvement Proposals repository to update the status of the CIP to active.

## References

- [Minimal Subtrees](https://link.springer.com/chapter/10.1007/978-3-319-61199-0_8)
- [Strong Accumulators from Collision-Resistant Hashing](https://users.dcc.uchile.cl/~pcamacho/papers/strongacc08.pdf)
- [CONIKS: Bringing Key Transparency to End Users](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-melara.pdf)
- [Cryptography for Efficiency: New Directions in Authenticated Data Structures](https://user.eng.umd.edu/~cpap/published/theses/cpap-phd.pdf)
- [Transparency Logs via Append-Only Authenticated Dictionaries](https://eprint.iacr.org/2018/721.pdf)
- [Batching non-membership proofs and proving non-repetition with bilinear accumulators](https://eprint.iacr.org/2019/1147.pdf)

## Versioning

The solution described in this CIP does not require any specific versioning approach.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

