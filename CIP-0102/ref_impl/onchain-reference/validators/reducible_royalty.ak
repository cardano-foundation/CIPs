use aiken/list
use aiken/transaction.{Output, ScriptContext, Transaction}
use aiken/transaction/credential.{VerificationKeyCredential}
use aiken/transaction/value.{PolicyId}
use onchain_reference/common.{RoyaltyInfo, get_data, royalty_tn}

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
                // the fee has not changed OR the fee has decreased AND the recipient has signed the transaction
                in_recipient.fee == out_recipient.fee || in_recipient.fee > out_recipient.fee && list.has(
                  context.transaction.extra_signatories,
                  sig,
                )
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
