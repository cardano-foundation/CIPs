use aiken/list
use aiken/transaction.{Input, Output, ScriptContext, Spend, Transaction}
use aiken/transaction/credential.{Address, VerificationKeyCredential}
use aiken/transaction/value.{PolicyId}
use onchain_reference/common.{
  RoyaltyDatum, RoyaltyRecipient, get_data, royalty_tn,
}
use onchain_reference/test_utils.{recipients_to_input, recipients_to_output}

type ReduceRedeemer {
  policy_id: PolicyId,
}

validator {
  fn reduce(_d: Data, redeemer: ReduceRedeemer, context: ScriptContext) -> Bool {
    let tx = context.transaction

    // find output datum
    expect Some(royalty_output) =
      list.find(
        tx.outputs,
        fn(output) {
          value.quantity_of(output.value, redeemer.policy_id, royalty_tn) == 1
        },
      )

    expect out_royalty_info: RoyaltyDatum =
      get_data(tx.datums, royalty_output.datum)

    // find input datum
    expect Some(royalty_input) =
      list.find(
        tx.inputs,
        fn(input) {
          value.quantity_of(input.output.value, redeemer.policy_id, royalty_tn) == 1
        },
      )

    expect in_royalty_info: RoyaltyDatum =
      get_data(tx.datums, royalty_input.output.datum)

    // check that for each in recipient, there is a corresponding out recipient
    expect
      list.all(
        // for each in recipient
        in_royalty_info.recipients,
        fn(in_recipient) {
          // unwrap the vck
          expect VerificationKeyCredential(sig) =
            in_recipient.address.payment_credential
          list.any(
            // for each out recipient
            out_royalty_info.recipients,
            fn(out_recipient) {
              // find the corresponding out recipient
              if in_recipient.address == out_recipient.address {
                // the recipient has signed the transaction AND
                // the fee has not changed OR
                // the fee has decreased (encoding reverses this)
                list.has(tx.extra_signatories, sig) && in_recipient.fee > out_recipient.fee || in_recipient.fee == out_recipient.fee
              } else {
                False
              }
            },
          )
        },
      )
    True
  }
}

// ############### TESTS ###############
const mock_owner = "some_fake_address_hash"

const mock_policy_id = "some_fake_policy_id"

test should_reduce_recipient() {
  let redeemer = ReduceRedeemer { policy_id: mock_policy_id }

  let in_recipient =
    RoyaltyRecipient {
      address: Address {
        payment_credential: VerificationKeyCredential(mock_owner),
        stake_credential: None,
      },
      fee: 625, // 1.6%
      min_fee: None,
      max_fee: None,
    }

  let input = recipients_to_input([in_recipient], mock_policy_id)

  let outputs =
    [
      recipients_to_output(
        [RoyaltyRecipient { ..in_recipient, fee: 125 }], // 8%
        mock_policy_id,
      ),
    ]

  let ctx =
    ScriptContext {
      transaction: get_base_transaction([input], outputs),
      purpose: Spend(input.output_reference),
    }

  reduce([], redeemer, ctx)
}

test should_fail_increase_recipient() fail {
  let redeemer = ReduceRedeemer { policy_id: mock_policy_id }

  let in_recipient =
    RoyaltyRecipient {
      address: Address {
        payment_credential: VerificationKeyCredential(mock_owner),
        stake_credential: None,
      },
      fee: 125, // 8%
      min_fee: None,
      max_fee: None,
    }

  let input = recipients_to_input([in_recipient], mock_policy_id)

  let outputs =
    [
      recipients_to_output(
        [RoyaltyRecipient { ..in_recipient, fee: 625 }], // 1.6%
        mock_policy_id,
      ),
    ]

  let ctx =
    ScriptContext {
      transaction: get_base_transaction([input], outputs),
      purpose: Spend(input.output_reference),
    }

  reduce([], redeemer, ctx)
}

test should_fail_no_token() fail {
  let redeemer = ReduceRedeemer { policy_id: mock_policy_id }

  let in_recipient =
    RoyaltyRecipient {
      address: Address {
        payment_credential: VerificationKeyCredential(mock_owner),
        stake_credential: None,
      },
      fee: 125,
      min_fee: None,
      max_fee: None,
    }

  let input = recipients_to_input([in_recipient], mock_policy_id)
  let recipient_output =
    recipients_to_output(
      [RoyaltyRecipient { ..in_recipient, fee: 625 }],
      mock_policy_id,
    )

  let outputs =
    [Output { ..recipient_output, value: value.zero() }]

  let ctx =
    ScriptContext {
      transaction: get_base_transaction([input], outputs),
      purpose: Spend(input.output_reference),
    }

  reduce([], redeemer, ctx)
}

fn get_base_transaction(
  recipients_in: List<Input>,
  recipients_out: List<Output>,
) -> Transaction {
  Transaction {
    ..transaction.placeholder(),
    extra_signatories: [mock_owner],
    inputs: recipients_in,
    outputs: recipients_out,
  }
}
