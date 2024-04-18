use aiken/list
use aiken/transaction.{Input, Output, ScriptContext, Transaction}
use aiken/transaction/credential.{Address, VerificationKeyCredential}
use aiken/transaction/value.{PolicyId}
use onchain_reference/common.{
  RoyaltyInfo, RoyaltyRecipient, get_data, royalty_tn,
}

type ReduceRedeemer {
  policy_id: PolicyId,
}

validator {
  fn spend(_d: Data, redeemer: ReduceRedeemer, context: ScriptContext) -> Bool {
    let tx = context.transaction

    // find output datum
    expect Some(royalty_output) =
      list.find(
        tx.outputs,
        fn(output) {
          value.quantity_of(output.value, redeemer.policy_id, royalty_tn) >= 1
        },
      )

    expect out_royalty_info: RoyaltyInfo = get_data(tx, royalty_output.datum)

    // find input datum
    expect Some(royalty_input) =
      list.find(
        tx.inputs,
        fn(input) {
          value.quantity_of(input.output.value, redeemer.policy_id, royalty_tn) >= 1
        },
      )

    expect in_royalty_info: RoyaltyInfo =
      get_data(tx, royalty_input.output.datum)

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
                // the fee has not changed OR
                in_recipient.fee == out_recipient.fee || // the fee has decreased (encoding reverses this) AND
                in_recipient.fee < out_recipient.fee && // the recipient has signed the transaction
                list.has(tx.extra_signatories, sig)
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

  let in_royalty_info =
    RoyaltyInfo {
      recipients: [
        RoyaltyRecipient {
          address: Address {
            payment_credential: VerificationKeyCredential(mock_owner),
            stake_credential: None,
          },
          fee: 125,
          min_fee: None,
          max_fee: None,
        },
      ],
      version: 1,
      extra: None,
    }

  True
}
// fn get_base_transaction(recipients_in: List<Input>, recipients_out: List<Output>) -> Transaction {
//   Transaction {
//     ..transaction.placeholder()
//     extra_signatories: [],
//     inputs: [
//       Output {
//         value: value.new(
//           value.new_map([
//             (mock_policy_id, value.new_integer(1))
//           ]),
//           royalty_tn
//         ),
//         datum: 0
//       }
//     ]
//   }
// }
