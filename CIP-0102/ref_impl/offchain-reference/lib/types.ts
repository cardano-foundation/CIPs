import { Constr, Data, Address } from "https://deno.land/x/lucid@0.10.7/mod.ts";

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
export const NFTDatumMetadata = NFTDatumMetadataSchema as unknown as NFTDatumMetadata;

// Royalty Metadata Schema

export const RoyaltyMetadataSchema = Data.Array(Data.Map(Data.Bytes(), Data.Any()));
export type RoyaltyMetadata = Data.Static<typeof RoyaltyMetadataSchema>;
export const RoyaltyMetadata = RoyaltyMetadataSchema as unknown as RoyaltyMetadata;

export const RoyaltyDatumMetadataSchema = Data.Object({
  metadata: RoyaltyMetadataSchema,
  version: Data.Integer({ minimum: 1, maximum: 1 }),
  extra: Data.Any(),
});
export type RoyaltyDatumMetadata = Data.Static<typeof RoyaltyDatumMetadataSchema>;
export const RoyaltyDatumMetadata = RoyaltyDatumMetadataSchema as unknown as RoyaltyDatumMetadata;

// Royalty Flag Schema

export const RoyaltyFlagSchema = Data.Object({ royalty_included: Data.Integer() })
export type RoyaltyFlag = Data.Static<typeof RoyaltyFlagSchema>;
export const RoyaltyFlag = RoyaltyFlagSchema as unknown as RoyaltyFlag;

export type RoyaltyRecipient = {
	address: Address;
	fee: number;  // in percentage
	maxFee?: number;
	minFee?: number;
}

export type RoyaltyConstr = Constr<
	Map<string, string | bigint> | Map<string, string | bigint>[]
>;

// NOTE: these are ripped from `lucid-cardano` and modified
export type MediaAsset = {
  name: string
  image: string | string[]
  mediaType?: string
  description?: string | string[]
  files?: MediaAssetFile[]
  [key: string]: unknown
}

declare type MediaAssetFile = {
  name?: string
  mediaType: string
  src: string | string[]
}

export type MediaAssets = {
	[key: string]: MediaAsset;
};

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
  