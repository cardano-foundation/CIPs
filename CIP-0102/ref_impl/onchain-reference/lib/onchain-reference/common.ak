use aiken/dict
use aiken/transaction.{Datum, DatumHash, InlineDatum, NoDatum, Transaction}
use aiken/transaction/credential.{Address}

pub const royalty_tn: ByteArray = "001f4d70526f79616c7479"

pub type RoyaltyDatum {
  recipients: List<RoyaltyRecipient>,
  version: Int,
  extra: Data,
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

pub fn get_data(tx: Transaction, datum: Datum) -> Data {
  when datum is {
    NoDatum -> fail
    DatumHash(h) -> {
      expect Some(d) = dict.get(tx.datums, h)
      d
    }
    InlineDatum(d) -> d
  }
}
