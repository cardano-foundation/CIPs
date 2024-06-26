use aiken/builtin.{choose_data}
use aiken/bytearray
use aiken/dict.{Dict}
use aiken/hash.{Blake2b_224, Blake2b_256, Hash}
use aiken/int
use aiken/list
use aiken/option
use aiken/transaction.{Datum, DatumHash, InlineDatum, Input, NoDatum}
use aiken/transaction/credential.{Address, VerificationKey}
use aiken/transaction/value.{AssetName, PolicyId}

pub const royalty_tn: ByteArray = "001f4d70526f79616c7479"

// taken from the CIP 68 standard
pub const user_tn_prefix: ByteArray = "000de140"

pub const ref_tn_prefix: ByteArray = "000643b0"

pub type RoyaltyDatum {
  recipients: List<RoyaltyRecipient>,
  version: Int,
  extra: Data,
}

pub type Metadata =
  Pairs<ByteArray, Data>

pub type ChooseData {
  DConstr
  DMap
  DList
  DInt
  DByteArray
}

pub type RefDatumMetadata {
  metadata: Metadata,
  version: Int,
  extra: Metadata,
}

pub type RoyaltyRecipient {
  address: Address,
  // percentage (fraction)
  fee: Int,
  // fixed (absolute)
  min_fee: Option<Int>,
  // fixed (absolute)
  max_fee: Option<Int>,
}

pub type Asset {
  policy_id: PolicyId,
  asset_name: AssetName,
  quantity: Int,
}

pub type VerificationKeyHash =
  Hash<Blake2b_224, VerificationKey>

// converts between the encoded onchain fee & per mille to avoid dealing with decimals
// since integer division handles the truncation for us, it's as simple as dividing by 10000
// recall that n / (n / m) == m, so the same function handles both directions of conversion
pub fn to_from_per_mille_fee(in_fee: Int) -> Int {
  10_000 / in_fee
}

// take a CIP 68 user token asset name, and output the corresponding reference token asset name
pub fn get_ref_tn(asset_name: ByteArray) -> ByteArray {
  bytearray.concat(ref_tn_prefix, bytearray.drop(asset_name, 8))
}

// take a CIP 68 reference token asset name, and output the corresponding user token asset name
pub fn get_user_tn(asset_name: ByteArray) -> ByteArray {
  bytearray.concat(user_tn_prefix, bytearray.drop(asset_name, 8))
}

pub fn get_data(
  tx_datums: Dict<Hash<Blake2b_256, Data>, Data>,
  datum: Datum,
) -> Data {
  when datum is {
    NoDatum -> fail
    DatumHash(h) -> {
      expect Some(d) = dict.get(tx_datums, h)
      d
    }
    InlineDatum(d) -> d
  }
}

pub fn get_recipients(
  asset: Asset,
  reference_inputs: List<Input>,
  datums: Dict<Hash<Blake2b_256, Data>, Data>,
) -> List<RoyaltyRecipient> {
  // Get royalty input
  let royalty_input =
    list.find(
      reference_inputs,
      fn(input) {
        value.quantity_of(input.output.value, asset.policy_id, royalty_tn) == 1
      },
    )

  if option.is_some(royalty_input) {
    // Get Royalty Datum
    expect Some(found_royalty_input) = royalty_input
    expect royalty_info: RoyaltyDatum =
      get_data(datums, found_royalty_input.output.datum)
    // If found, get recipients
    royalty_info.recipients
  } else {
    // If not found, check if the asset is a CIP-68 user token
    if bytearray.take(asset.asset_name, 8) == user_tn_prefix {
      // if so, calculate reference token asset name
      let ref_tn = get_ref_tn(asset.asset_name)

      // look for an input with a reference token
      expect Some(ref_token_input) =
        list.find(
          reference_inputs,
          fn(input) {
            value.quantity_of(input.output.value, asset.policy_id, ref_tn) == 1
          },
        )
      // parse the reference datum
      expect reference_datum: RefDatumMetadata =
        get_data(datums, ref_token_input.output.datum)

      // Check for royalty flag 
      let has_flag = list.find(reference_datum.extra, fn(item) -> Bool { and {
              // maybe TODO: convert to hex
              item.1st == "royalty_included",
              // when constr, map, list, int, bytearray
              when
                choose_data(item.2nd, DConstr, DMap, DList, DInt, DByteArray)
              is {
                DInt -> {
                  expect parsed_int: Int = item.2nd
                  parsed_int >= 1
                }
                DByteArray -> {
                  expect parsed_ba: ByteArray = item.2nd
                  when int.from_utf8(parsed_ba) is {
                    None -> False
                    Some(parsed_int) -> parsed_int >= 1
                  }
                }
                _ -> False
              },
            } })

      when has_flag is {
        Some(_) ->
          // throw error if it exists and is > 0
          fail
        // return empty list if it doesn't exist or is 0
        None ->
          []
      }
    } else {
      // if the asset is not a CIP 68 NFT, return an empty list
      []
    }
  }
}

test test_to_per_mille() {
  and {
    to_from_per_mille_fee(125) == 80,
    to_from_per_mille_fee(625) == 16,
  }
}
