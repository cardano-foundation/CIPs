import { load } from "https://deno.land/std@0.208.0/dotenv/mod.ts";
import { writeFileSync } from "https://deno.land/std@0.110.0/node/fs.ts";

const env = await load({ allowEmptyValues: true });

export function getEnv(variable: string): string {
	const value = env[variable];
	if (!value) {
		throw Error(
			`Must set ${variable} is a required environment variable. Did you use 'pnpm run .env <task>'?`
		);
	}

	return value;
}

export function updateEnv(config = {}, eol = '\n'){
  const envContents = Object.entries({...env, ...config})
    .map(([key,val]) => `${key}=${val}`)
    .join(eol)
  writeFileSync('.env', envContents);
}