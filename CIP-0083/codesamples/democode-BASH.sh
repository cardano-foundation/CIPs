#!/bin/bash

# --------------------------------------------------------------------------------------------
# Demonstration implementation of CIP-0020 Transaction Messages Encryption/Decryption via BASH
# --------------------------------------------------------------------------------------------

#Setting default passphrase
passphrase="cardano"


#Unencrypted Metadata JSON
echo "Normal unencrpted messages metadata JSON:"
cat normal-message-metadata.json | jq
echo


#Encrypt the msg array from the JSON
encrText=$(jq -crM .\"674\".msg normal-message-metadata.json | openssl enc -e -aes-256-cbc -pbkdf2 -iter 10000 -a -k "${passphrase}")
echo "Encrypted Strings (base64 format):"
echo "${encrText}"
echo


#Compose it into a new JSON and add the 'enc' entry
echo "New encrypted messages metadata JSON:"
jq ".\"674\".msg = [ $(awk {'print "\""$1"\","'} <<< ${encrText} | sed '$ s/.$//') ]" <<< '{"674":{"enc":"basic"}}' | jq


echo
echo "----------------------"
echo


#Encrypted Metadata JSON
echo "Encrypted messages metadata JSON:"
cat encrypted-message-metadata.json | jq
echo


#Decrypt the msg array from the JSON
decrText=$(jq -crM ".\"674\".msg[]" encrypted-message-metadata.json | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -a -k "${passphrase}")
echo "Decrypted Content:"
echo "${decrText}"
echo


#Compose it into a new JSON in the standard message format
echo "New messages metadata JSON:"
jq ".\"674\".msg = ${decrText}" <<< "{}"
echo
