use aiken/transaction/credential.{Address}

pub type Payout {
  recipient: Address,
  // in lovelace
  amount: Int,
}
