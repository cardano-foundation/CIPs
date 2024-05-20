use aiken/transaction.{InlineDatum, Input, Output, OutputReference}
use aiken/transaction/credential.{Address, VerificationKeyCredential}
use aiken/transaction/value.{PolicyId}
use onchain_reference/common.{RoyaltyDatum, RoyaltyRecipient, royalty_tn}

pub fn recipients_to_input(
  recipients: List<RoyaltyRecipient>,
  policy_id: PolicyId,
) -> Input {
  let mock_outref =
    OutputReference {
      transaction_id: transaction.placeholder().id,
      output_index: 0,
    }

  Input {
    output_reference: mock_outref,
    output: recipients_to_output(recipients, policy_id),
  }
}

pub fn recipients_to_output(
  recipients: List<RoyaltyRecipient>,
  policy_id: PolicyId,
) -> Output {
  let out_royalty_info = RoyaltyDatum { recipients, version: 1, extra: None }

  Output {
    address: Address {
      payment_credential: VerificationKeyCredential(""),
      stake_credential: None,
    },
    value: value.from_asset(policy_id, royalty_tn, 1),
    datum: InlineDatum(out_royalty_info),
    reference_script: None,
  }
}
