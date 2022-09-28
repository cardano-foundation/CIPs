-- PlutusTx on-chain code (PlutusV2)
-- NOTE: The asset name labels are not finalized yet. This is only a proof of concept

type Metadata = Map BuiltinData BuiltinData
data DatumMetadata = DatumMetadata {
                        metadata    :: Metadata
                    ,   version     :: Integer
                    }

data Action = Mint | Burn

PlutusTx.makeLift ''Action
PlutusTx.makeIsDataIndexed ''Action [('Mint, 0), ('Burn, 1)]


txOutRef :: TxOutRef
txOutRef = TxOutRef "568ea530dfe90b2a0890b340eac46b3c58ce298eb67cee047e2463ea105f4cdd" 0 -- Example out ref (required to mint NFT)


-- | Minting policy (mints user token and reference NFT as pair). It is a one-shot policy.
-- Minting policy depends on reference validator 
{-# INLINEABLE mintValidatorControl #-}
mintingPolicy :: Address -> TxOutRef -> Action -> ScriptContext -> Bool
mintingPolicy refAddress oref action ctx = case action of
    Mint    -> checkMint
    Burn -> checkBurn
  where
    txInfo :: TxInfo
    txInfo = scriptContextTxInfo ctx

    txMint :: Value
    txMint = txInfoMint txInfo

    ownSymbol :: CurrencySymbol
    ownSymbol = ownCurrencySymbol ctx

    prefixLength :: Integer
    prefixLength = 5

    checkMint :: Bool
    checkMint =
            let
                [(_, refOutValue)] = scriptOutputsAtAddress refAddress txInfo
                [(refOutCs, TokenName refOutName,refOutAm)] = flattenValue (noAdaValue refOutValue)
                -- | Mint value (reference NFT and user token).
                [(userCs, TokenName userName, userAm), (refCs, TokenName refName, refAm)] = flattenValue txMint
            in
                -- | One shot policy
                spendsOutput txInfo (txOutRefId oref) (txOutRefIdx oref)                                            &&
                -- | Check if minted reference NFT is sent to reference address
                noAdaValue refOutValue == V.singleton refCs (TokenName refName) refAm                               &&
                -- | Check quantity and policy ids
                userAm == 1 && refAm == 1 && userCs == ownSymbol && refCs == ownSymbol                              &&
                -- | Check naming
                takeByteString prefixLength userName == "(222)" && takeByteString prefixLength refName == "(100)"   &&
                dropByteString prefixLength userName == dropByteString prefixLength refName

                

    checkBurn :: Bool
    checkBurn = all (\(_,_,am) -> am < 0) (flattenValue txMint)


-- | Reference validator (holds the reference NFT with metadata)
{-# INLINEABLE refValidator #-}
refValidator :: DatumMetadata -> () -> ScriptContext -> Bool
refValidator datumMetadata () ctx = checkBurn
  where
    txInfo :: TxInfo
    txInfo = scriptContextTxInfo ctx

    txMint :: Value
    txMint = txInfoMint txInfo

    ownValue :: Value
    ownValue =  let Just i = findOwnInput ctx
                    out = txInInfoResolved i
                in txOutValue out

    prefixLength :: Integer
    prefixLength = 5

    providesUserToken :: CurrencySymbol -> TokenName -> Integer -> Bool
    providesUserToken cs tn am = any (\(TxInInfo _ out) -> valueOf (txOutValue out) cs tn == am) (txInfoInputs txInfo)

    checkBurn :: Bool
    checkBurn = 
            let
                -- | Allow burning only one pair (reference NFT and user token) at once.
                [(userCs, TokenName userName, userAm), (refCs, TokenName refName, refAm)] = flattenValue txMint
                [(ownCs, TokenName ownName, _)] = flattenValue (noAdaValue ownValue)
            in
                -- | Matching policy ids and quantities.
                -1 == userAm && -1 == refAm &&
                ownCs == userCs && ownCs == refCs && 
                -- | Matching asset names.
                takeByteString prefixLength userName == "(222)" && takeByteString prefixLength refName == "(100)" &&
                dropByteString prefixLength userName == dropByteString prefixLength refName                       &&
                -- | Burned reference NFT needs to match the one in the own script UTxO
                ownName == refName



{-# INLINEABLE scriptOutputsAtAddress #-}
scriptOutputsAtAddress :: Address -> TxInfo -> [(OutputDatum, Value)]
scriptOutputsAtAddress address p =
    let flt TxOut{txOutDatum=d, txOutAddress=address', txOutValue} | address == address' = Just (d, txOutValue)
        flt _ = Nothing
    in mapMaybe flt (txInfoOutputs p)