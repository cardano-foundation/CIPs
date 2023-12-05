# Minting a CIP 102 compliant NFT with royalties

## Timelocked Minting Policy
- Checks
  - Owner has signed tx
  - Tx validity window is before MP deadline

## Validators

### Always Fails
- Checks nothing
- Returns false or throws error

### Reducible 
- Checks
	- tx is signed by recipient
	- amount sent to recipient is < previous amount
	- all other recipients remain the same
		- amount
		- address

## Offchain
- Constructs well formed CIP-68 & CIP-102 Datums
- Sends reference NFT & datum to arbitrary address
- Sends royalty NFT & datum to
	- arbitrary address
	- always-fails script
	- reducible validator

# Reading a CIP 102 NFT’s royalties off chain

- Querying the datum
	- Check if datum is required
	- Request datum
	- Fail depending on whether datum is required
- Parsing the datum


# Reading and validating against CIP 102 NFT royalties on chain

A simple listing contract which locks a CIP 102 NFT & a datum with a price & seller and must pay out royalties according to that price to be withdrawn.

## Onchain

- Royalty datum
	- If empty, check if royalty is required
		- Parse reference datum
		- Fail if royalty field > 1
	- If not, check if royalties are being paid correctly
		- Fail if not
- Listing datum
	- Confirm the amount is getting paid to the seller, minus royalties

## Offchain

- Find & read the requested listing datum
- Find & read the associated royalty datum using the approach above
- Calculate payments
- Construct & Submit tx