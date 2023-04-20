// -----------------------------------------------------------------------------------------------
// Democode for running a Decryption on the Web Frontend - Method BASIC
// -----------------------------------------------------------------------------------------------

// Library that is used for this codesample: https://www.npmjs.com/package/crypto-js
// Just import it before using this code

let encrypted = "U2FsdGVkX18IJMMB5MDfNmuvvlbu4m5ODGmCrHHtWfYKarTRT4/x790+uhsj7cgRxDFvjxU7dcSPqH5PAXvRtPcaRyqoYBaXOQbm3D78wQCY4wCiLF1/mFOvFHPfpQHeC9jykRfpaVC3rtlJdHCPTw=="
let encryptedWA = cryptoJS.enc.Base64.parse(encrypted);

// Split the encrypted data into the individual pieces
let prefixWA = cryptoJS.lib.WordArray.create(encryptedWA.words.slice(0, 8/4)); // Salted__ prefix
let saltWA = cryptoJS.lib.WordArray.create(encryptedWA.words.slice(8/4, 16/4)); // 8 bytes salt: 0x0123456789ABCDEF
let ciphertextWA = cryptoJS.lib.WordArray.create(encryptedWA.words.slice(16/4, encryptedWA.words.length)); // ciphertext        

// Determine key and IV using PBKDF2
let password = 'cardano'
let keyIvWA = cryptoJS.PBKDF2(
  password, 
  saltWA, 
    {
      keySize: (32+16)/4, // key and IV
      iterations: 10000,
      hasher: cryptoJS.algo.SHA256
    }
);
let keyWA = cryptoJS.lib.WordArray.create(keyIvWA.words.slice(0, 32/4));
let ivWA = cryptoJS.lib.WordArray.create(keyIvWA.words.slice(32/4, (32+16)/4));

// Decrypt the data
let decryptedWA = cryptoJS.AES.decrypt(
  {
    ciphertext: ciphertextWA}, 
                keyWA, 
                {iv: ivWA}
);
let decrypted = decryptedWA.toString(cryptoJS.enc.Utf8)

console.log(`Encrypted Data:`)
console.log(encrypted)
console.log(`Decrypted Data:`)
console.log(decrypted)
