alias ligo="docker run --rm -v "$PWD":"$PWD" -w "$PWD" ligolang/ligo:0.46.1"
ligo compile contract nft/nft.mligo --protocol jakarta > michelson/nft.tz
ligo compile contract marketplace/marketplace.mligo --protocol jakarta  > michelson/marketplace.tz
ligo compile contract update/update.mligo --protocol jakarta > michelson/update.tz

