import { Constr, Data } from "https://deno.land/x/lucid@0.10.7/mod.ts";

export const MetadataSchema = Data.Map(Data.Bytes(), Data.Any());
export type Metadata = Data.Static<typeof MetadataSchema>;
export const Metadata = MetadataSchema as unknown as Metadata;

export const DatumMetadataSchema = Data.Object({
  metadata: MetadataSchema,
  version: Data.Integer({ minimum: 1, maximum: 1 }),
  extra: Data.Any(),
});
export type DatumMetadata = Data.Static<typeof DatumMetadataSchema>;
export const DatumMetadata = DatumMetadataSchema as unknown as DatumMetadata;

export const RoyaltyFlagSchema = Data.Object({ royalty_included: Data.Integer() })
export type RoyaltyFlag = Data.Static<typeof RoyaltyFlagSchema>;
export const RoyaltyFlag = RoyaltyFlagSchema as unknown as RoyaltyFlag;

export type RoyaltyRecipient = {
	address: string;
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
  