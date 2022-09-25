"""Reference Implementation of Domain Validation for Cardano Addresses.

Requirements can be installed with:
    pip install -r requirements.txt
(If globally, as user, or in a virutal environment is your choice.
Currently, it's only dnspython. So, you could also install that directly,
e.g., via system package management.)

This reference implementation should pass type checking with mypy and
linting with pycodestyle and pydocstyle. Moreover, it contains doctests.
Those can be executed with:
    $ mypy cardano-domain-validation.py
    $ pycodestyle cardano-domain-validation.py
    $ pydocstyle cardano-domain-validation.py
    $ python3 -m doctest cardano-domain-validation.py
(Observe that the doctests use the examples from the CIP and depend on the
example tokens and server configurations still being available.)

The script can simply be executed by:
    $ python3 cardano-domain-validation.py <domain or address>
"""
import json
import re
import sys
from urllib.request import urlopen
from urllib.error import HTTPError

import dns.resolver  # type: ignore

from typing import Any, Dict, List, Tuple


def get_domains(address: str) -> Dict[str, Tuple[Dict[str, Any], int]]:
    """Get domains for a given address.

    From CIP:
    * Find all domains related to it by `Domain` tokens as given below.
    * For all of these domains, find all addresses related to them by DNS
      and/or HTTP(S) as given below.
    * The result are all domains that point back to the given address.
    * Domains *not* pointing back to the given address *must* be ignored.

    Returns a dictionary from domains to pairs consisting of
    * a dictionary of additional metadata found for the given address at
      these domains (which may be empty) and
    * the rating between 1 and 3 for the security of the domain validation:
      - 1 point for DNS validation
      - 1 point for HTTP validation
      - 1 point for HTTPS validation

    >>> get_domains('addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6'
    ...             'wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5')
    {\
'bbraatz.eu': ({}, 3), \
'heptasean.de': ({'Comment': 'Main Wallet'}, 2)}
    >>> get_domains('addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0x'
    ...             'xllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q')
    {\
'heptasean.de': ({'Comment': 'Token Trading'}, 2)}
    >>> get_domains('addr1qyjwqxz8sry4ul522x5zfp4na2t5m4qkuxtpzw0tll99a8z'
    ...             'wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0yscp2j47')
    {}
    """
    result = {}
    domains = query_address(address)
    for domain in domains:
        addresses, rating = query_domain(domain)
        if address in addresses:
            result[domain] = addresses[address], rating
    return result


def get_addresses(domain: str) -> Dict[str, Tuple[Dict[str, Any], int]]:
    """Get addresses for a given domain.

    From CIP:
    * Find all addresses related to it by DNS and/or HTTP(S) as given
      below.
    * For all of these addresses, find all domains related to them by
      `Domain` tokens as given below.
    * The result are all addresses that point back to the given domain.
    * Addresses *not* pointing back to the given domain *must* be ignored.

    Returns a dictionary from addresses to pairs consisting of
    * a dictionary of additional metadata found for these addresses at the
      given domain (which may be empty) and
    * the rating between 1 and 3 for the security of the domain validation:
      - 1 point for DNS validation
      - 1 point for HTTP validation
      - 1 point for HTTPS validation

    >>> get_addresses('bbraatz.eu')
    {\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': ({}, 3)}
    >>> get_addresses('heptasean.de')
    {\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': \
({'Comment': 'Main Wallet'}, 2), \
'addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0x\
xllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q': \
({'Comment': 'Token Trading'}, 2)}
    >>> get_addresses('example.com')
    {}
    """
    result = {}
    addresses, rating = query_domain(domain)
    for address in addresses:
        domains = query_address(address)
        if domain in domains:
            result[address] = addresses[address], rating
    return result


def query_address(address: str) -> List[str]:
    """Query blockchain for Domain tokens.

    From CIP:
    * All tokens with an asset name of `Domain` (`446f6d61696e`) that are
      currently at an unspent transaction output (UTxO) of that address are
      searched.
    * For these tokens, the latest minting transaction with associated
      metadata is determined.
    * For these minting transactions, the respective domain in the metadata
      is added to the set of related domains.

    Returns a set of domains.

    >>> query_address('addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6'
    ...               'wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5')
    ['bbraatz.eu', 'example.com', 'heptasean.de']
    >>> query_address('addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0x'
    ...               'xllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q')
    ['heptasean.de']
    >>> query_address('addr1qyjwqxz8sry4ul522x5zfp4na2t5m4qkuxtpzw0tll99a8z'
    ...               'wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0yscp2j47')
    []
    """
    result = set()
    koios = "https://api.koios.rest/api/v0"
    query_url = (f"{koios}/address_assets?_address={address}"
                 "&asset_name=eq.446f6d61696e")
    with urlopen(query_url) as address_response:
        json_body = address_response.read().decode()
        address_assets = json.loads(json_body)
        for asset in address_assets:
            policy_id = asset['policy_id']
            query_url = (f"{koios}/asset_info?_asset_policy={policy_id}"
                         "&_asset_name=446f6d61696e"
                         "&select=minting_tx_metadata")
            with urlopen(query_url) as token_response:
                json_body = token_response.read().decode()
                asset_info = json.loads(json_body)
                for asset_object in asset_info:
                    for metadatum in asset_object['minting_tx_metadata']:
                        if metadatum['key'] == '53':
                            if (isinstance(metadatum['json'], str) and
                                    is_domain(metadatum['json'])):
                                result.add(metadatum['json'])
                            elif isinstance(metadatum['json'], list):
                                domain = ''
                                for part in metadatum['json']:
                                    if isinstance(part, str):
                                        domain += part
                                    else:
                                        domain = ''
                                        break
                                if domain and is_domain(domain):
                                    result.add(domain)
    return sorted(result)


def query_domain(domain: str) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Query DNS and HTTP(S) for Cardano addresses and combine results.

    From CIP:
    * If both, HTTP(S)-related addresses and DNS-related addresses are
      found, only their intersection is the set of related addresses.
      If one of the sets is found, it is the set of related addresses.
      If none is found, the set of related addresses is empty.

    Returns a pair consisting of
    * a dictionary from addresses to dictionaries of additional metadata
      found for these addresses at the given domain (which may be empty)
      and
    * the rating between 0 and 3 for the security of the domain validation:
      - 1 point for DNS validation
      - 1 point for HTTP validation
      - 1 point for HTTPS validation

    >>> query_domain('bbraatz.eu')
    ({\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': {}}, 3)
    >>> query_domain('heptasean.de')
    ({\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': \
{'Comment': 'Main Wallet'}, \
'addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0x\
xllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q': \
{'Comment': 'Token Trading'}, \
'addr1qyjwqxz8sry4ul522x5zfp4na2t5m4qkuxtpzw0tll99a8z\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0yscp2j47': \
{'Comment': 'No Domain token'}}, 2)
    >>> query_domain('example.com')
    ({}, 0)
    """
    result = {}
    dns_addresses, dns_rating = query_dns(domain)
    https_addresses, https_rating = query_https(domain)
    if dns_rating:
        if https_rating:
            for address in https_addresses:
                if address in dns_addresses:
                    result[address] = https_addresses[address]
        else:
            for address in dns_addresses:
                result[address] = {}
    else:
        for address in https_addresses:
            result[address] = https_addresses[address]
    return result, dns_rating + https_rating


def query_dns(domain: str) -> Tuple[List[str], int]:
    """Query DNS for Cardano addresses.

    From CIP:
    * A DNS query for TXT records at the subdomain `_addresses._cardano` of
      the given domain is made.
      If TXT records are found, all addresses in these records are
      considered DNS-related addresses.

    Returns a pair consisting of
    * a set of addresses and
    * the rating – 0 for no records found, 1 for records found.

    If records are found, but they are not valid domains, an empty set with
    a rating of 1 is returned.

    >>> query_dns('bbraatz.eu')
    ([\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5', \
'addr1q9wvykt8vpvgrqjr9lgm8d9dstgl3h2wesdrqlxa4gqdv62\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysv6v74x'], 1)
    >>> query_dns('heptasean.de')
    ([], 0)
    >>> query_dns('example.com')
    ([], 0)
    """
    result = set()
    rating = 0
    answers = []
    try:
        answers = dns.resolver.resolve('_addresses._cardano.' + domain,
                                       'TXT')
    except dns.resolver.NXDOMAIN:
        pass
    for answer in answers:
        rating = 1
        address = str(answer).strip('"')
        if is_address(address):
            result.add(address)
    return sorted(result), rating


def query_https(domain: str) -> Tuple[Dict[str, Dict[str, Any]], int]:
    """Query HTTP(S) for Cardano addresses.

    From CIP:
    * A HTTP(S) request is made to the path
      `/.well-known/cardano/addresses.json` at the given domain.
      If a JSON file is obtained, all addresses given in this JSON file are
      considered HTTP(S)-related addresses.

    Returns a pair consisting of
    * a dictionary from addresses to dictionaries of additional metadata
      found for these addresses at the given domain (which may be empty)
      and
    * the rating – 0 for no JSON found, 1 for found over HTTP, 2 for found
      over HTTPS.

    If a JSON is found, but does not contain valid address information, an
    empty dictionary with a rating of 1 or 2 is returned.

    >>> query_https('bbraatz.eu')
    ({\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': {}, \
'addr1q8fe7mx9xdpr063tkp8k5r65psy9p469az04rh86epcaxz2\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ys3ufz2q': {}}, 2)
    >>> query_https('heptasean.de')
    ({\
'addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5': \
{'Comment': 'Main Wallet'}, \
'addr1qyh72hvvrurjvddx4gq37jd2fzyef8scz9cwcyc90dffq0x\
xllh3nc5r82ujj36fy9zh0gryqvqy7r3ejd2h2kgsvryswhjr9q': \
{'Comment': 'Token Trading'}, \
'addr1qyjwqxz8sry4ul522x5zfp4na2t5m4qkuxtpzw0tll99a8z\
wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0yscp2j47': \
{'Comment': 'No Domain token'}}, 2)
    >>> query_https('example.com')
    ({}, 0)
    """
    path = ".well-known/cardano/addresses.json"
    result = {}
    rating = 0
    json_body = ""
    try:
        with urlopen(f"https://{domain}/{path}") as response:
            rating = 2
            json_body = response.read().decode()
    except HTTPError:
        try:
            with urlopen(f"http://{domain}/{path}") as response:
                rating = 1
                json_body = response.read().decode()
        except HTTPError:
            pass
    address_list = []
    try:
        address_list = json.loads(json_body)
    except json.decoder.JSONDecodeError:
        pass
    if isinstance(address_list, list):
        for address in address_list:
            if (isinstance(address, dict) and
                    'address' in address and
                    is_address(address['address'])):
                result[address['address']] = {key: address[key]
                                              for key in address
                                              if key != 'address'}
    return result, rating


def is_address(address: str) -> bool:
    """Check if given string is Cardano address.

    Uses a simple regular expression that only checks if prefix is 'addr',
    all characters are from the BECH32 character set and there are at least
    the 6 characters required for the checksum.

    >>> is_address('addr1q8fgal6mmwdllxdvft28xy6x3wjgc3v6nj450smmhtdama6'
    ...            'wlu8vnqcstwtxa4l3yuckm8gttva66skvfzrmruead0ysjatmn5')
    True
    >>> is_address('addr1q8fga')
    False
    >>> is_address('wrong1q8fgal6mmwdllxdvft28xy6x')
    False
    >>> is_address('totally wrong')
    False
    """
    if re.match(r'^addr1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{6,}$', address):
        return True
    return False


def is_domain(domain: str) -> bool:
    """Check if given string is a DNS domain.

    Uses a medium complex regular expression to check for domain validity.

    >>> is_domain('com')
    False
    >>> is_domain('heptasean.de')
    True
    >>> is_domain('123.com')
    False
    >>> is_domain('Counting-1-2-3.COM')
    True
    """
    if re.match(r'^([a-zA-Z]'           # Start: letter
                r'([-a-zA-Z0-9]{0,61}'  # Interior: letter, digit, hyphen
                r'[a-zA-Z0-9])?\.)+'    # End: letter, digit
                                        # One or more of these labels
                r'[a-zA-Z]{2,63}$',     # Top-level domain: only letter
                domain):
        return True
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Domain or Cardano address has to be given as argument!")
        exit(1)
    if len(sys.argv) > 2:
        print("Only one argument (domain or Cardano address) is allowed!")
        exit(1)
    given = sys.argv[1]
    result = {}
    if is_address(given):
        result = get_domains(given)
    elif is_domain(given):
        result = get_addresses(given)
    else:
        print(f"'{given}' is neither a domain nor a Cardano address!")
        exit(1)
    for key in result:
        metadata, rating = result[key]
        rating_string = "★" * rating + "☆" * (3 - rating)
        print(f"{rating_string} {key}")
        for key in metadata:
            print(f"    {key}: {metadata[key]}")
