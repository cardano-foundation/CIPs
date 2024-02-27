import { getAssetsTransactions } from "./query.ts"

const response = await getAssetsTransactions("2b29ff2309668a2e58d96da26bd0e1c0dd4013e5853e96df2be27e42001f4d70526f79616c7479")

console.log(response)