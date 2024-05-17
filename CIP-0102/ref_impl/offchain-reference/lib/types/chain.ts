import { Data, Address, getAddressDetails } from "https://deno.land/x/lucid@0.10.7/mod.ts";

// NFT Metadata Schema

export const NFTMetadataSchema = Data.Map(Data.Bytes(), Data.Any());
export type NFTMetadata = Data.Static<typeof NFTMetadataSchema>;
export const NFTMetadata = NFTMetadataSchema as unknown as NFTMetadata;

export const NFTDatumMetadataSchema = Data.Object({
  metadata: NFTMetadataSchema,
  version: Data.Integer({ minimum: 1, maximum: 1 }),
  extra: Data.Any(),
});
export type NFTDatumMetadata = Data.Static<typeof NFTDatumMetadataSchema>;
export const NFTDatumMetadata = NFTDatumMetadataSchema as unknown as NFTDatumMetadata

// Address Schema

export const ChainCredentialSchema = Data.Enum([
  Data.Object({
    VerificationKeyCredential: Data.Tuple([Data.Bytes({ minLength: 28, maxLength: 28 })]),
  }),
  Data.Object({
    ScriptCredential: Data.Tuple([Data.Bytes({ minLength: 28, maxLength: 28 })]),
  }),
]);

export const ChainAddressSchema = Data.Object({
  paymentCredential: ChainCredentialSchema,
  stakeCredential: Data.Nullable(
    Data.Enum([
      Data.Object({ Inline: Data.Tuple([ChainCredentialSchema]) }),
      Data.Object({
        Pointer: Data.Object({
          slotNumber: Data.Integer(),
          transactionIndex: Data.Integer(),
          certificateIndex: Data.Integer(),
        }),
      }),
    ])
  ),
});

export type ChainAddress = Data.Static<typeof ChainAddressSchema>;
export const ChainAddress = ChainAddressSchema as unknown as ChainAddress;

/// Converts a Bech32 address to the aiken representation of a chain address
export function asChainAddress(address: Address): ChainAddress {
  const { paymentCredential, stakeCredential } = getAddressDetails(address);

  if (!paymentCredential) throw new Error('Not a valid payment address.');

  return {
    paymentCredential:
      paymentCredential?.type === 'Key'
        ? {
            VerificationKeyCredential: [paymentCredential.hash],
          }
        : { ScriptCredential: [paymentCredential.hash] },
    stakeCredential: stakeCredential
      ? {
          Inline: [
            stakeCredential.type === 'Key'
              ? {
                  VerificationKeyCredential: [stakeCredential.hash],
                }
              : { ScriptCredential: [stakeCredential.hash] },
          ],
        }
      : null,
  };
}

// based on Blockfrost's openAPI
export type asset_transactions = Array<{
  /**
   * Hash of the transaction
   */
  tx_hash: string;
  /**
   * Transaction index within the block
   */
  tx_index: number;
  /**
   * Block height
   */
  block_height: number;
  /**
   * Block creation time in UNIX time
   */
  block_time: number;
  }>;
  
  export type output = {
    /**
     * Output address
     */
    address: string;
    amount: Array<{
    /**
     * The unit of the value
     */
    unit: string;
    /**
     * The quantity of the unit
     */
    quantity: string;
    }>;
    /**
     * UTXO index in the transaction
     */
    output_index: number;
    /**
     * The hash of the transaction output datum
     */
    data_hash: string | null;
    /**
     * CBOR encoded inline datum
     */
    inline_datum: string | null;
    /**
     * Whether the output is a collateral output
     */
    collateral: boolean;
    /**
     * The hash of the reference script of the output
     */
    reference_script_hash: string | null;
    };
  