use aiken/collection/list.{filter, find, has}
use aiken/primitive/bytearray.{length}
use cardano/address.{Address, Script}
use cardano/assets.{PolicyId, quantity_of}
use cardano/transaction.{
  InlineDatum, Input, Output, OutputReference, Transaction,
}

pub type AffirmationDatum {
  owner: ByteArray,
}

pub type RichAffirmationDatum {
  owner: ByteArray,
  class: Int,
  payload: ByteArray,
}

validator v1 {
  mint(_redeemer: Data, own_policy: PolicyId, tx: Transaction) {
    let Transaction { extra_signatories, outputs, mint, .. } = tx
    expect [mint_triplet] = mint |> assets.flatten
    let (mint_policy, mint_name, mint_quantity) = mint_triplet
    expect mint_policy == own_policy
    if mint_quantity == 1 {
      expect [Output { datum: InlineDatum(output_datum), .. }] =
        filter(
          outputs,
          fn(output) { output.address.payment_credential == Script(own_policy) },
        )
      if output_datum is AffirmationDatum {
        let check_datum = output_datum
        expect has(extra_signatories, check_datum.owner) == True
      } else if output_datum is RichAffirmationDatum {
        let check_datum: RichAffirmationDatum = output_datum
        expect has(extra_signatories, check_datum.owner) == True
      } else {
        fail
      }
    } else {
      expect has(extra_signatories, mint_name) == True
    }

    when mint_quantity is {
      1 -> True
      -1 -> True
      _ -> False
    }
  }

  spend(
    datum: Option<Data>,
    _redeemer: Data,
    own_ref: OutputReference,
    tx: Transaction,
  ) {
    let Transaction { extra_signatories, inputs, mint, .. } = tx
    expect [mint_triplet] = mint |> assets.flatten

    let (mint_policy, mint_name, mint_quantity) = mint_triplet
    expect mint_quantity == -1
    expect Some(datum) = datum
    expect Some(own_input) =
      find(inputs, fn(input) { input.output_reference == own_ref })
    expect own_input.output.address.payment_credential == Script(mint_policy)

    if datum is AffirmationDatum {
      let AffirmationDatum { owner } = datum
      expect owner == mint_name

      expect quantity_of(own_input.output.value, mint_policy, owner) == 1
      expect has(extra_signatories, owner) == True
    } else if datum is RichAffirmationDatum {
      let RichAffirmationDatum { owner, class, payload } = datum
      expect owner == mint_name
      expect class > -1
      expect length(payload) > 0
      expect quantity_of(own_input.output.value, mint_policy, owner) == 1
      expect has(extra_signatories, owner) == True
    } else {
      fail
    }
    True
  }

  else(_) {
    fail
  }
}
