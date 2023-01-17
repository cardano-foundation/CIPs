// -----------------------------------------------------------------------------------------------
// Demonstration implementation of CIP-0020 Transaction Messages Encryption/Decryption via NODE-JS
// -----------------------------------------------------------------------------------------------

const crypto = require('crypto');

//
// Calculate the KeyIV via the PasswordBasedKeyDerivedFormat2 pbkdf2 method, 10000 iterations, 48 bytes long, sha256
//
function calc_KeyIV(passphrase, salt) { //passphrase as utf8 string, salt as hexstring
	const key_IV = crypto.pbkdf2Sync(Buffer.from(passphrase,'utf8'), Buffer.from(salt,'hex'), 10000, 48, 'sha256').toString('hex')
	console.log(`              keyIV: ${key_IV}`);
	return key_IV;  //hex-string
}

//
// Encryption Function
//
function encryptCardanoMessage(decrypted_msg, passphrase = 'cardano') { //decrypted_msg as utf8 string, passphrase as utf8 string(defaults to cardano)
	//Encrypted Message (salted) looks like 'Salted__' + 8 bytes salt + cyphertext
	//Build up the encrypted Message as hex string
	var encrypted_hex = Buffer.from('Salted__','utf8').toString('hex');
	//Generate the random salt
	var salt = crypto.randomBytes(8).toString('hex');
	encrypted_hex += salt; //append the salt
	console.log(`               salt: ${salt}`);
	//Calculate the Key+IV
	var keyIV = calc_KeyIV(passphrase, salt)
	//The key itself is the first 32 Bytes (char 0-64 in hex string)
	var key = keyIV.substring(0,64);
	//The IV (initialization vector) is 16 Bytes and follows the key
	var iv = keyIV.substring(64);
	console.log(`                key: ${key}`);
	console.log(`                 iv: ${iv}`);
	//Encrypt the message
  	const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key,'hex'), Buffer.from(iv,'hex'));
	try {
		var cyphertext = cipher.update(decrypted_msg, 'utf8', 'hex') + cipher.final('hex');
	} catch (error) { console.error(`Could not encrypt the message\n${error}`); process.exit(1); }
	console.log(`         cyphertext: ${cyphertext}`);
	encrypted_hex += cyphertext; //append the cyphertext
	console.log(`   Enc-Message(hex): ${encrypted_hex}`);
	return Buffer.from(encrypted_hex,'hex').toString('base64'); //base64 string
}


//
// Decryption Function
//
function decryptCardanoMessage(encrypted_msg, passphrase = 'cardano') { //encrypted_msg as base64 string, passphrase as utf8 string(defaults to cardano)
	//Encrypted Message is base64 encoded, convert it to hex
	const encrypted_hex = Buffer.from(encrypted_msg, 'base64').toString('hex');
	console.log(`   Enc-Message(hex): ${encrypted_hex}`);
	//Encrypted Message (salted) looks like 'Salted__' + 8 bytes salt + cyphertext
	//Salt is byte 9-16 in the Encrypted Message (char 16-32 in a hex string)
	var salt = encrypted_hex.substring(16,32);
	console.log(`               salt: ${salt}`);
	//Cyphertext is all the rest after the salt (starting with char 32 in a hex string)
	var cyphertext = encrypted_hex.substring(32);
	console.log(`         cyphertext: ${cyphertext}`);
	//Calculate the Key+IV
	var keyIV = calc_KeyIV(passphrase, salt)
	//The key itself is the first 32 Bytes (char 0-64 in hex string)
	var key = keyIV.substring(0,64);
	//The IV (initialization vector) is 16 Bytes and follows the key
	var iv = keyIV.substring(64);
	console.log(`                key: ${key}`);
	console.log(`                 iv: ${iv}`);
	//Decrypt the cyphertext with the key and the iv
	const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key,'hex'), Buffer.from(iv,'hex'));
	try {
		var decr_msg = decipher.update(cyphertext, 'hex').toString('utf8') + decipher.final('utf8');
	} catch (error) { console.error(`Could not decrypt the message\n${error}`); process.exit(1); }
	return decr_msg; //utf8
}

//-------------------------
// DEMO Encrypt and Decrypt
//-------------------------

const passphrase = 'cardano'; //Using default passphrase 'cardano'

// Encryption
console.log(`--- Encryption ---`);
var decrypted_msg = 'Hi, this is a test-message. Best regards, Martin';
console.log(`  Dec-Message(utf8): ${decrypted_msg}`)
var encrypted_msg = encryptCardanoMessage(decrypted_msg, passphrase);
console.log(`Enc-Message(base64): ${encrypted_msg}`);
console.log(`\n\n`);

// Decryption
console.log(`--- Decryption ---`);
var encrypted_msg = 'U2FsdGVkX18UshV/vpKWoYtutcS2efoloN+okKMY+pYdvUnqi88znUhHPxSSX8t4';
console.log(`Enc-Message(base64): ${encrypted_msg}`);
var decrypted_msg = decryptCardanoMessage(encrypted_msg, passphrase);
console.log(`  Dec-Message(utf8): ${decrypted_msg}`)
console.log(`\n\n`);
