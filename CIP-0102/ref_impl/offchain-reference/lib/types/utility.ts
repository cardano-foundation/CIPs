import { TxComplete } from 'https://deno.land/x/lucid@0.10.7/mod.ts'

// Tx Builder Output
export type TxBuild = {
  error: string;
  tx?: undefined;
  policyId?: undefined;
} | {
  tx: TxComplete;
  policyId: string;
  error?: undefined;
}

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