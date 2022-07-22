alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.46.1"
ligo compile contract fungible_token/atf.mligo --entry-point main > michelson/atf.tz
ligo compile contract fungible_token/action.mligo --entry-point main > michelson/action.tz
ligo compile contract fungible_token/swap.mligo --entry-point main > michelson/swap.tz
# ligo compile contract multisig/multisig.mligo --entry-point main > michelson/multisig.tz
