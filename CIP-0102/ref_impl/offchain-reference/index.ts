import { getAssetsTransactions } from "./query.ts"
import { getRoyaltyPolicy } from "./read.ts";

// const response = await getAssetsTransactions("2b29ff2309668a2e58d96da26bd0e1c0dd4013e5853e96df2be27e42001f4d70526f79616c7479")

const response = await getRoyaltyPolicy("60a75923cfc6e241b5da7fd6328d8846275ce94c15fcfc903538e012")

console.log(response)