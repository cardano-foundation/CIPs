use aiken/bytearray
use aiken/list
use aiken/math
use aiken/option
use aiken/string
use aiken/transaction.{
  InlineDatum, Input, NoDatum, Output, OutputReference, ScriptContext, Spend,
  Transaction,
}
use aiken/transaction/credential.{
  Address, ScriptCredential, VerificationKeyCredential,
}
use aiken/transaction/value.{quantity_of}
use onchain_reference/common.{
  Asset, RoyaltyRecipient, VerificationKeyHash, get_recipients,
  to_from_per_mille_fee, user_tn_prefix,
}
use onchain_reference/listing_utils.{Payout}
use onchain_reference/test_utils.{
  output_to_string, payout_to_string, placeholder_oref, placeholder_recipient,
  recipients_to_input,
}

type ListingDatum {
  // to further prevent circumvention, lot could be detected from consumed the Listing output
  lot: Asset,
  seller: VerificationKeyHash,
  // in lovelace
  price: Int,
}

/// A user can either buy a token
/// or cancel/update the listing.
type ListingRedeemer {
  /// Make a purchase.
  Buy
  /// Cancel or update a listing.
  WithdrawOrUpdate
}

validator {
  /// Validate that the signer is the owner or that payouts
  /// are present as outputs and that the tag is correct.
  fn spend(
    datum: ListingDatum,
    redeemer: ListingRedeemer,
    ctx: ScriptContext,
  ) -> Bool {
    let ScriptContext { transaction, purpose } = ctx

    let Transaction { outputs, extra_signatories, reference_inputs, datums, .. } =
      transaction

    // Match on the action.
    when redeemer is {
      Buy -> {
        expect Spend(_out_ref) = purpose

        let royalty_recipients: List<RoyaltyRecipient> =
          get_recipients(datum.lot, reference_inputs, datums)

        // ensure royalty amount is paid to the royalty address
        let payouts: List<Payout> =
          get_payouts(datum.seller, royalty_recipients, datum.price)

        trace list.foldl(
          outputs,
          @"",
          fn(output, current_str) {
            string.concat(current_str, output_to_string(output))
          },
        )

        trace list.foldl(
          payouts,
          @"",
          fn(payout, current_str) {
            string.concat(current_str, payout_to_string(payout))
          },
        )

        // check that the payouts are represented in the outputs and that enough are 
        datum.price <= check_payouts(outputs, payouts)
      }

      // There's not much to do here. An asset
      // owner can cancel or update their listing
      // at any time.
      WithdrawOrUpdate -> list.has(extra_signatories, datum.seller)
    }
  }
}

fn get_payouts(
  seller: VerificationKeyHash,
  royalty_recipients: List<RoyaltyRecipient>,
  price: Int,
) -> List<Payout> {
  // for each recipient
  // DO THIS WORK? TEST IT

  let (payouts, paid_out) =
    list.foldl(
      royalty_recipients,
      ([], 0),
      fn(recipient: RoyaltyRecipient, out: (List<Payout>, Int)) -> (
        List<Payout>,
        Int,
      ) {
        // get the estimated amount based on the price
        let amount = to_from_per_mille_fee(recipient.fee) * price / 1000

        // adjust based on min fee
        let amount =
          if option.is_some(recipient.min_fee) {
            expect Some(min) = recipient.min_fee
            math.max(amount, math.min(price - out.2nd, min))
          } else {
            amount
          }

        // adjust based on max fee
        let amount =
          if option.is_some(recipient.max_fee) {
            expect Some(max) = recipient.max_fee
            math.min(amount, max)
          } else {
            amount
          }
        let already_paid_out = out.2nd + amount
        // output payout
        (
          list.concat(
            out.1st,
            [Payout { recipient: recipient.address, amount }],
          ),
          already_paid_out,
        )
      },
    )

  let seller_payout =
    Payout {
      recipient: Address {
        payment_credential: VerificationKeyCredential(seller),
        stake_credential: None,
      },
      amount: price - paid_out,
    }

  // output seller payout with remainder of price
  list.push(payouts, seller_payout)
}

/// Credit to JPG.Store's v3 open source contracts. Thank you for helping push the ecosystem forward!
/// Check that payouts and payout outputs
/// are correct. Payouts are stored in the datum
/// when assets are listed. On buy a transaction
/// with matching payout outputs needs to be constructed.
/// We also require that outputs are in the same order as the
/// payouts in the datum. Returns the sum of the payout amounts.
fn check_payouts(outputs: List<Output>, payouts: List<Payout>) -> Int {
  expect [first_output, ..rest_outputs] = outputs

  let Output { address: output_address, value, .. } = first_output
  expect [payout, ..rest_payouts] = payouts

  let Payout { recipient: payout_address, amount: amount_lovelace } = payout

  // The `Output` address must match
  // the address specified in the corresponding
  // payout from the datum.
  expect payout_address == output_address

  // The quantity in the output must equal
  // the amount specified in the corresponding
  // payout from the datum.
  let quantity = quantity_of(value, "", "")
  expect quantity >= amount_lovelace && amount_lovelace > 0
  let rest_payouts_amount =
    when rest_payouts is {
      // the base case
      [] ->
        // if rest is empty we are done
        0
      _ ->
        // continue with remaining outputs and payouts
        check_payouts(rest_outputs, rest_payouts)
    }

  amount_lovelace + rest_payouts_amount
}

// ############### ENDPOINT TESTS ###############
const mock_owner: VerificationKeyHash = "some_fake_address_hash"

const mock_policy_id = "fake_lot_policy_id"

const mock_buyer: VerificationKeyHash = "some_other_fake_address_hash"

test one_recipient_cip68_buy() {
  let redeemer = Buy

  let lot =
    Asset {
      policy_id: mock_policy_id,
      asset_name: bytearray.concat(user_tn_prefix, "fake_lot_tn"),
      quantity: 1,
    }

  // Price: 1000 Ada
  let listing_datum =
    ListingDatum { lot, seller: mock_owner, price: 1_000_000_000 }

  let royalty_recipients =
    [placeholder_recipient(80, mock_owner)]

  let ctx =
    ScriptContext {
      transaction: get_base_transaction(listing_datum, royalty_recipients),
      purpose: Spend(OutputReference { ..placeholder_oref(), output_index: 1 }),
    }

  // 0 is the royalty input
  spend(listing_datum, redeemer, ctx)
}

test multi_recipient_cip68_buy() {
  let redeemer = Buy

  let lot =
    Asset {
      policy_id: mock_policy_id,
      asset_name: bytearray.concat(user_tn_prefix, "fake_lot_tn"),
      quantity: 1,
    }

  // Price: 1000 Ada
  let listing_datum =
    ListingDatum { lot, seller: mock_owner, price: 1_000_000_000 }

  let royalty_recipients =
    [
      placeholder_recipient(80, mock_owner),
      placeholder_recipient(15, "other_mock_owner"),
      placeholder_recipient(50, "other_other_mock_owner"),
      placeholder_recipient(20, "yet_another_mock_owner"),
      placeholder_recipient(200, "so_many_mock_owners"),
    ]

  let ctx =
    ScriptContext {
      transaction: get_base_transaction(listing_datum, royalty_recipients),
      purpose: Spend(OutputReference { ..placeholder_oref(), output_index: 1 }),
    }

  // 0 is the royalty input
  spend(listing_datum, redeemer, ctx)
}

test no_royalty_paid() fail {
  let redeemer = Buy

  let lot =
    Asset {
      policy_id: mock_policy_id,
      asset_name: bytearray.concat(user_tn_prefix, "fake_lot_tn"),
      quantity: 1,
    }

  // Price: 1000 Ada
  let listing_datum =
    ListingDatum { lot, seller: mock_owner, price: 1_000_000_000 }

  let royalty_recipients =
    [placeholder_recipient(80, mock_owner)]

  // constructing tx with no outputs to recipients
  let tx =
    Transaction {
      ..get_base_transaction(listing_datum, royalty_recipients),
      outputs: get_base_transaction(listing_datum, []).outputs,
    }

  let ctx =
    ScriptContext {
      transaction: tx,
      purpose: Spend(OutputReference { ..placeholder_oref(), output_index: 1 }),
    }

  // 0 is the royalty input
  spend(listing_datum, redeemer, ctx)
}

fn get_base_transaction(
  listing_datum: ListingDatum,
  royalty_recipients: List<RoyaltyRecipient>,
) -> Transaction {
  let lot_input = lot_to_input(listing_datum)
  let royalty_policy_ref_input =
    recipients_to_input(royalty_recipients, mock_policy_id)

  let buyer_address =
    Address {
      payment_credential: VerificationKeyCredential(mock_buyer),
      stake_credential: None,
    }

  let buyer_input_output =
    Output {
      address: buyer_address,
      // add 1 ada for fees
      value: value.from_lovelace(listing_datum.price + 1_000_000),
      datum: NoDatum,
      reference_script: None,
    }

  let buyer_input =
    Input {
      output: buyer_input_output,
      output_reference: OutputReference {
        ..placeholder_oref(),
        output_index: 2,
      },
    }

  // 0 is royalty input, 1 is lot
  let buyer_output =
    Output {
      address: buyer_address,
      value: value.from_lovelace(listing_datum.price),
      datum: NoDatum,
      reference_script: None,
    }

  let amount_to_royalties =
    math.clamp(
      list.foldl(
        royalty_recipients,
        0,
        fn(recipient, total) {
          to_from_per_mille_fee(recipient.fee) * listing_datum.price / 1000 + total
        },
      ),
      0,
      listing_datum.price,
    )

  trace string.from_int(amount_to_royalties)

  let royalty_outputs: List<Output> =
    list.map(
      royalty_recipients,
      fn(recipient) {
        Output {
          address: recipient.address,
          value: value.from_lovelace(
            to_from_per_mille_fee(recipient.fee) * listing_datum.price / 1000,
          ),
          datum: NoDatum,
          reference_script: None,
        }
      },
    )

  let seller_output =
    Output {
      address: Address {
        payment_credential: VerificationKeyCredential(mock_owner),
        stake_credential: None,
      },
      value: value.from_lovelace(listing_datum.price - amount_to_royalties),
      datum: NoDatum,
      reference_script: None,
    }

  Transaction {
    ..transaction.placeholder(),
    extra_signatories: [mock_buyer],
    inputs: [lot_input, buyer_input],
    reference_inputs: [royalty_policy_ref_input],
    outputs: list.concat([seller_output, ..royalty_outputs], [buyer_output]),
  }
}

fn lot_to_input(datum: ListingDatum) -> Input {
  let lot = datum.lot
  Input {
    output: Output {
      address: Address {
        payment_credential: ScriptCredential(""),
        stake_credential: None,
      },
      value: value.from_asset(lot.policy_id, lot.asset_name, lot.quantity),
      datum: InlineDatum(datum),
      reference_script: None,
    },
    output_reference: OutputReference { ..placeholder_oref(), output_index: 1 },
  }
  // 0 is the royalty input
}

// ############### FUNCTION TESTS ###############

/// This test makes sure the `check_payouts` returns true
/// when give the correct inputs. It is safe to have trailing outputs
/// in the transaction as long as the payouts are correct.
test check_payouts_with_trailing_outputs() {
  let test_royalty_addr =
    Address {
      payment_credential: VerificationKeyCredential(
        #"80f60f3b5ea7153e0acc7a803e4401d44b8ed1bae1c7baaad1a62a81",
      ),
      stake_credential: None,
    }

  let test_seller_addr =
    Address {
      payment_credential: VerificationKeyCredential(
        #"90f60f3b5ea7153e0acc7a803e4401d44b8ed1bae1c7baaad1a62a81",
      ),
      stake_credential: None,
    }

  let test_random_addr =
    Address {
      payment_credential: VerificationKeyCredential(
        #"fff60f3b5ea7153e0acc7a803e4401d44b8ed1bae1c7baaad1a62a81",
      ),
      stake_credential: None,
    }

  let test_royalty_payouts =
    [
      Payout { recipient: test_royalty_addr, amount: 3000000 },
      Payout { recipient: test_seller_addr, amount: 95000000 },
    ]

  let out_1 =
    Output {
      address: test_royalty_addr,
      value: value.from_lovelace(3100000),
      datum: NoDatum,
      reference_script: None,
    }

  let out_2 =
    Output {
      address: test_seller_addr,
      value: value.from_lovelace(95000000),
      datum: NoDatum,
      reference_script: None,
    }

  let out_random =
    Output {
      address: test_random_addr,
      value: value.from_lovelace(1000000),
      datum: NoDatum,
      reference_script: None,
    }

  let outputs = list.concat([out_1, out_2], list.repeat(out_random, 100))

  98000000 == check_payouts(outputs, test_royalty_payouts)
}
