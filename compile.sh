alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.37.0"
ligo compile contract fungible_token/atf.mligo --entry-point main > michelson/atf.tz
ligo compile contract multisig/multisig.mligo --entry-point main > michelson/multisig.tz
