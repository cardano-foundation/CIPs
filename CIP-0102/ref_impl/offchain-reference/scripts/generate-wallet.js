import { Lucid } from 'https://deno.land/x/lucid@0.10.7/mod.ts';
import { getEnv, updateEnv } from './env.ts';

const network = getEnv('PUBLIC_CARDANO_NETWORK');
const lucid = await Lucid.new(undefined, network);

const privateKey = lucid.utils.generatePrivateKey();
const address = await lucid
	.selectWalletFromPrivateKey(privateKey)
	.wallet.address();
const envUpdate = {
  WALLET_ADDRESS: address,
  WALLET_PRIVATE_KEY: privateKey,
}
updateEnv(envUpdate);
