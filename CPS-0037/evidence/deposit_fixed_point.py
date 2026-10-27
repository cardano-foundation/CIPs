#!/usr/bin/env python3
"""Reproduce the CPS's size-dependent funding examples with the Python stdlib.

The split form models an experimental output, not the deployed Babbage/Conway
format: {0: address, 1: applicationAda, 4: deposit}. It preserves total ADA while
moving funds between the last two fields. All integers use shortest CBOR widths.

This self-contained encoding reconstruction is not a compiled Ledger integration
test.

Run from the repository root:
    python3 'CPS-0037/evidence/deposit_fixed_point.py'
"""


def encode_uint(value):
    """CBOR major type 0, using its shortest encoding (RFC 8949)."""
    if not 0 <= value < 2**64:
        raise ValueError("Expected an unsigned 64-bit integer")
    if value < 24:
        return bytes([value])
    for marker, width in ((24, 1), (25, 2), (26, 4), (27, 8)):
        if value < 1 << (8 * width):
            return bytes([marker]) + value.to_bytes(width, "big")
    raise AssertionError("Unreachable")


# Synthetic base address: mainnet header, two 28-byte key hashes. Its contents
# are immaterial to sizing. The CBOR byte-string prefix is 0x58 0x39 (57 bytes).
ADDRESS = b"\x01" + bytes(56)
ENCODED_ADDRESS = b"\x58\x39" + ADDRESS


def merged_output(coin):
    """A Babbage map-form ADA-only output, with no datum or reference script."""
    return b"\xa2\x00" + ENCODED_ADDRESS + b"\x01" + encode_uint(coin)


def split_output(total, deposit):
    """Experimental three-field map with fixed total application ADA + deposit."""
    if not 0 <= deposit <= total:
        raise ValueError("Deposit must be funded from the fixed total")
    return (
        b"\xa3\x00" + ENCODED_ADDRESS
        + b"\x01" + encode_uint(total - deposit)
        + b"\x04" + encode_uint(deposit)
    )


def requirement(encoded_output, price):
    return price * (160 + len(encoded_output))


def main():
    price = 4310
    first = requirement(merged_output(0), price)
    fixed = requirement(merged_output(first), price)
    assert (first, fixed) == (961130, 978370)
    assert requirement(merged_output(fixed), price) == fixed
    print(f"Merged output: 0 -> {first} -> {fixed} -> {fixed} lovelace")

    total = 1061146
    expected_rows = (
        (995610, 65536, 73, 1004230),
        (1004230, 56916, 71, 995610),
        (995611, 65535, 71, 995610),
    )
    print("Split output: deposit | application ADA | bytes | requirement")
    for deposit, application, size, cost in expected_rows:
        encoded = split_output(total, deposit)
        assert (total - deposit, len(encoded), requirement(encoded, price)) == (
            application, size, cost
        )
        print(f"{deposit} | {application} | {size} | {cost}")

    exact = []
    first_sufficient = None
    possible_costs = set()
    for deposit in range(total + 1):
        cost = requirement(split_output(total, deposit), price)
        possible_costs.add(cost)
        if deposit == cost:
            exact.append(deposit)
        if deposit >= cost and first_sufficient is None:
            first_sufficient = deposit
    assert exact == []
    assert first_sufficient == 995611
    assert possible_costs == {986990, 991300, 995610, 1004230}
    print(f"Exhaustively checked {total + 1:,} allocations: no exact solution")
    print(f"Smallest sufficient deposit: {first_sufficient} lovelace")


if __name__ == "__main__":
    main()
