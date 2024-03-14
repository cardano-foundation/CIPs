export const CIP102_ROYALTY_TOKEN_NAME = '001f4d70526f79616c7479'; // (500)Royalty

// convert from percentage to onchain royalty value
export function toOnchainRoyalty(percentage: number): number {
	return Math.floor(1 / (percentage / 1000));
}

// convert from onchain royalty value to percentage
export function fromOnchainRoyalty(value: number): number {
	return Math.trunc((10 / value) * 1000) / 10;
}