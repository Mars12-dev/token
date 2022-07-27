#include "../common/const.mligo"
#include "../common/interface.mligo"
#include "marketplace_errors.mligo"
#include "marketplace_interface.mligo"
#include "marketplace_functions.mligo"
// #include "../common/functions.mligo"


let add_to_marketplace (param : add_to_marketplace_param) (store : storage) : return =
  if store.paused then
    (failwith error_MARKETPLACE_IS_PAUSED : return)
  else if (not Set.mem param.token_origin store.collections) then
    (failwith(error_TOKEN_ORIGIN_NOT_LISTED) : return)
  else if (not param.is_multi_token) && (param.token_symbol <> "XTZ" && param.token_symbol <> "ATF") then
    (failwith(error_ONLY_XTZ_OR_ATF_CAN_BE_CHOSEN) : return)
  else if param.token_symbol <> "XTZ" && (Tezos.get_amount ()) <> 0tez then
    (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : return)
  else
    let token_key =
      {
        token_id = param.token_id;
        token_origin = param.token_origin;
      } in
    let swap_id =
      match Big_map.find_opt token_key store.tokens with
      | Some _swap_id -> (failwith(error_TOKEN_IS_ALREADY_ON_SALE) : swap_id)
      | None -> store.next_swap_id in
  if param.start_time >= param.end_time then
    (failwith(error_START_TIME_IS_LATER_THAN_END_TIME) : return)
  else
    let _ = Set.iter (fun (symbol : string) ->
      assert_with_code (Big_map.mem symbol store.allowed_tokens) error_TOKEN_LIST_INVALID ) param.accepted_tokens in
    let payment_token =
      match Big_map.find_opt param.token_symbol store.allowed_tokens with
      | None ->
        (failwith(error_TOKEN_SYMBOL_UNLISTED) : string)
      | Some t -> t.token_symbol in
    let (starting_price, duration, is_dutch) =
      match param.swap_type with
      | Regular -> (param.token_price, 0, false)
      | Dutch p ->
        if int p.duration > param.end_time - param.start_time then
          (failwith(error_DURATION_IS_LONGER_THAN_SWAP_DURATION) : (nat * int * bool))
        else
          (p.starting_price, int p.duration, true)
      in
    let (recipient, is_reserved) =
      match param.recipient with
      | Reserved p -> (p, true)
      | General -> ((Tezos.get_self_address ()), false)
      in
      let op =
      (
        token_transfer
          param.token_origin
          [
            {
              from_ = (Tezos.get_sender ());
              txs =
                [
                  {
                    to_ = (Tezos.get_self_address ());
                    token_id = param.token_id;
                    amount = 1n;
                  }
                ]
            }
          ]
      ) in
      let ops = [op] in
      let new_swaps =
          Big_map.update swap_id (Some {
          owner = (Tezos.get_sender ());
          token_id = param.token_id;
          token_origin = param.token_origin;
          is_dutch = is_dutch;
          is_reserved = is_reserved;
          starting_price = starting_price;
          token_price = param.token_price;
          start_time = param.start_time;
          duration = duration;
          end_time = param.end_time;
          recipient = recipient;
          ft_symbol = payment_token;
          accepted_tokens = if (not param.is_multi_token) then Set.literal [payment_token] else param.accepted_tokens;
          is_multi_token = param.is_multi_token;
          }) store.swaps in
      let new_tokens =
        Big_map.update token_key (Some swap_id) store.tokens in
      let new_store =
        {
          store with
          next_swap_id = store.next_swap_id + 1n;
          swaps = new_swaps;
          tokens = new_tokens;
        } in
      ops, new_store



let update_swap (param : update_swap_param) (store : storage) : return =
  if store.paused then
    (failwith error_MARKETPLACE_IS_PAUSED : return)
  else
    let swap =
      match Big_map.find_opt param.swap_id store.swaps with
      | None -> (failwith(error_SWAP_ID_DOES_NOT_EXIST) : swap_info)
      | Some swap -> swap in
    if (Tezos.get_sender ()) <> swap.owner then
      (failwith(error_ONLY_OWNER_CAN_CALL_THIS_ENTRYPOINT) : return)
    else match param.action with
    | Update_price price ->
    if swap.is_dutch && (Tezos.get_now ()) >= swap.start_time then
      (failwith(error_DUTCH_AUCTION_ACTIVE) : return)
    else
      let new_swaps = Big_map.update param.swap_id (Some {swap with token_price = price}) store.swaps in
      ([] : operation list), { store with swaps = new_swaps }
    | Update_times p ->
    if p.start_time >= p.end_time then
      (failwith(error_START_TIME_IS_LATER_THAN_END_TIME) : return)
    else if swap.is_dutch && (Tezos.get_now ()) >= swap.start_time then
      (failwith(error_DUTCH_AUCTION_ACTIVE) : return)
    else
      let new_swaps = Big_map.update param.swap_id (Some { swap with start_time = p.start_time; end_time = p.end_time }) store.swaps in
      ([] : operation list), { store with swaps = new_swaps }
    | Update_reserved_address p ->
    let new_swaps = Big_map.update param.swap_id (Some {swap with recipient = p; is_reserved = true}) store.swaps in
    ([] : operation list), { store with swaps = new_swaps }
    | Update_duration p ->
    if (not swap.is_dutch) || (swap.is_dutch && (Tezos.get_now ()) >= swap.start_time) then
      (failwith(error_CAN_NOT_UPDATE_DURATION_FOR_THIS_SWAP) : return)
    else
      let new_swaps = Big_map.update param.swap_id (Some { swap with duration = int p }) store.swaps in
      ([] : operation list), {store with swaps = new_swaps}
    | Update_starting_price p ->
    if (not swap.is_dutch) || (swap.is_dutch && (Tezos.get_now ()) >= swap.start_time) then
      (failwith(error_CAN_NOT_UPDATE_STARTING_PRICE_FOR_THIS_SWAP) : return)
    else
      let new_swaps = Big_map.update param.swap_id (Some { swap with starting_price = p }) store.swaps in
      ([] : operation list), {store with swaps = new_swaps}




let remove_from_marketplace (swap_id : remove_from_marketplace_param) (store : storage) : return =
    let swap =
      match Big_map.find_opt swap_id store.swaps with
      | None -> (failwith error_SWAP_ID_DOES_NOT_EXIST : swap_info)
      | Some swap_info -> swap_info in
    let token_key =
      {
        token_id = swap.token_id;
        token_origin = swap.token_origin;
      } in
    if (Tezos.get_sender ()) <> swap.owner then
      (failwith error_ONLY_OWNER_CAN_REMOVE_FROM_MARKETPLACE : return)
    else
      let token_id = swap.token_id in
      let op = token_transfer 
        swap.token_origin
        [
          { 
            from_ = (Tezos.get_self_address ()); 
            txs = 
              [
                { 
                    to_ = (Tezos.get_sender ()); 
                    token_id = token_id; 
                    amount = 1n 
                }
              ]
          }
        ] in
      let (new_swaps, new_tokens) =
          (Big_map.update swap_id (None : swap_info option) store.swaps,
          Big_map.update token_key (None : swap_id option) store.tokens) in
      let new_store = { store with swaps = new_swaps; tokens = new_tokens } in
      [op], new_store


let collect (param : collect_marketplace_param) (store : storage) : return =
  if store.paused then
    (failwith error_MARKETPLACE_IS_PAUSED : return)
    (* payment token was specified as token other than XTZ, but XTZ amount was sent *)
  else if param.token_symbol <> "XTZ" && (Tezos.get_amount ()) <> 0tez then
    (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : return)
  else
    let swap =
      match Big_map.find_opt param.swap_id store.swaps with
      | None -> (failwith error_SWAP_ID_DOES_NOT_EXIST : swap_info)
      | Some swap_info -> swap_info in
    let token_key =
      {
        token_id = swap.token_id;
        token_origin = swap.token_origin;
      } in
    let buyer =
      if swap.is_reserved && (param.to_) <> swap.recipient then
        (failwith(error_ONLY_RECIPIENT_CAN_COLLECT) : address)
      else
        (param.to_) in
    if (Tezos.get_now ()) < swap.start_time then
        (failwith error_SALE_IS_NOT_STARTED_YET : return)
      else if (Tezos.get_now ()) > swap.end_time then
        (failwith error_SALE_IS_FINISHED : return)
      else
    (* token price set to zero by the seller.
    only token is transferred *)
    if swap.token_price = 0n then
      let op = token_transfer 
        swap.token_origin
        [
          { 
            from_ = (Tezos.get_self_address ()); 
            txs = 
              [
                { 
                  to_ = buyer; 
                  token_id = swap.token_id; 
                  amount = 1n; 
                }
              ]
          }
        ] in
      let (new_swaps, new_tokens) =
          (Big_map.update param.swap_id (None : swap_info option) store.swaps,
          Big_map.update token_key (None : swap_id option) store.tokens) in
      [op], { store with swaps = new_swaps; tokens = new_tokens }
    else
    (* non-zero price. *)
        (* set the amount of fungible tokens to be sent from buyer (in buyer currency) *)
        let transfer_amount =
          let price =
            if swap.is_dutch then
              calculate_price (swap.start_time, swap.duration, swap.starting_price, swap.token_price)
            else
              swap.token_price in
          let buyer_amount_nat =
          (* check that the payment token is one permitted by the seller *)
            let _ = (assert_with_code (Set.mem param.token_symbol swap.accepted_tokens) error_TOKEN_NOT_PERMITTED_BY_SELLER) in
          (* considers the case of XTZ transfer, convert the amount type to nat *)
            if param.token_symbol = "XTZ" then
              mutez_to_natural (Tezos.get_amount ())
            else
              param.amount_ft in
          (* convert and check equality of amounts *)
          let converted_price =
            if (not swap.is_multi_token) then
            (* no conversion needed *)
              price
            else
              convert_tokens swap.ft_symbol price param.token_symbol store in
          let _ = (assert_with_code (converted_price <= buyer_amount_nat) error_AMOUNT_IS_NOT_EQUAL_TO_PRICE) in
          (* transfer_amount = converted_price *)
          converted_price in

        let management_fee =
          transfer_amount * store.management_fee_rate / const_FEE_DENOM in
        let royalties = store.royalties_rate * transfer_amount / const_FEE_DENOM in
        let seller_value =
          match is_nat (transfer_amount - (management_fee + royalties)) with
          | None -> (failwith error_FEE_GREATER_THAN_AMOUNT : nat)
          | Some n -> n in
        (* operation assignment *)
        let ops = ([] : operation list) in
        (* seller payment operation *)
        let ops = payment_transfer ops seller_value param.token_symbol (Tezos.get_sender ()) swap.owner store in
        (* royalties payment operation *)
        let ops = payment_transfer ops royalties param.token_symbol (Tezos.get_sender ()) store.royalties_address store in
        (* management payment operation *)
        let ops = payment_transfer ops management_fee param.token_symbol (Tezos.get_sender ()) store.treasury store in
        (* buyer token operation *)
        let ops =
          token_transfer
          swap.token_origin
          [{
              from_ = (Tezos.get_self_address ());
              txs =
              [{
                to_ = buyer;
                token_id = swap.token_id;
                amount = 1n;
              }]
            }] :: ops in
        (* remove swap and token from storage *)
        let (new_swaps, new_tokens) =
            (Big_map.update param.swap_id (None : swap_info option) store.swaps,
            Big_map.update token_key (None : swap_id option) store.tokens) in
        let new_store = { store with swaps = new_swaps; tokens = new_tokens; } in
        (ops, new_store)


let send_offer (param : offer_param) (store : storage) : return =
  if store.paused then
    (failwith(error_MARKETPLACE_IS_PAUSED) : return)
  else if (not Set.mem param.token_origin store.collections) then
    (failwith(error_TOKEN_ORIGIN_NOT_LISTED) : return)
  else if param.start_time > param.end_time then
    (failwith(error_START_TIME_IS_LATER_THAN_END_TIME) : return)
  else if param.token_symbol <> "XTZ" && (Tezos.get_amount ()) <> 0tez then
    (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : return)
  else
    let offer_id = 
      {
        buyer = (Tezos.get_sender ());
        token_id = param.token_id;
        token_origin = param.token_origin;
      } in
    match Big_map.find_opt offer_id store.offers with
    | Some _ -> (failwith(error_OFFER_ALREADY_PLACED) : return)
    | None ->
      let ft_amount =
        if param.token_symbol = "XTZ" then
          if param.ft_amount <> mutez_to_natural (Tezos.get_amount ()) then
            (failwith(error_OFFER_VALUE_IS_NOT_EQUAL_TO_XTZ_AMOUNT) : nat)
          else
            mutez_to_natural (Tezos.get_amount ())
        else param.ft_amount in
      let new_offer = {
        value = ft_amount;
        start_time = param.start_time;
        end_time = param.end_time;
        token_symbol = param.token_symbol;
        } in
      let new_offers = Big_map.update offer_id (Some new_offer) store.offers in
      let ops = ([] : operation list) in
      (* incoming operation *)
      let ops =
        if param.token_symbol = "XTZ" then
          ops
        else
          match Big_map.find_opt param.token_symbol store.allowed_tokens with
          | None -> (failwith(error_TOKEN_SYMBOL_UNLISTED) : operation list)
          | Some fun_token -> fa12_transfer fun_token.fa_address (Tezos.get_sender ()) (Tezos.get_self_address ()) ft_amount :: ops in
      ops, {store with offers = new_offers}


let update_offer (param : offer_param) (store : storage) : return =
  if store.paused then
    (failwith(error_MARKETPLACE_IS_PAUSED) : return)
  else if param.token_symbol <> "XTZ" && (Tezos.get_amount ()) <> 0tez then
    (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : return)
  else if param.start_time > param.end_time then
    (failwith(error_START_TIME_IS_LATER_THAN_END_TIME) : return)
  else 
    let () = match Big_map.find_opt param.token_symbol store.allowed_tokens with
    | None -> (failwith(error_TOKEN_SYMBOL_UNLISTED) : unit)
    | Some _ -> () in
    let offer_id =
      {
        token_id = param.token_id;
        buyer = (Tezos.get_sender ());
        token_origin = param.token_origin;
      } in
    match Big_map.find_opt offer_id store.offers with
    | None -> (failwith(error_NO_OFFER_PLACED) : return)
    | Some offer ->
      let new_offer = {offer with
            value = param.ft_amount;
            start_time = param.start_time;
            end_time = param.end_time;
            token_symbol = param.token_symbol;
            } in

      (* we have to take care of different cases and subcases:
    1: incoming token_symbol is the same as the former token_symbol.
    1.1: if token_symbol is "XTZ": we return the former value.
    1.2: other token_symbol (requires fa12 transfer)
    1.2.1: if the new offer is higher: incoming_amount will be sent, no outgoing_amount.
    1.2.2: if the new offer is lower: no incoming_amount, outgoing_amount will be sent.
    2: incoming token_symbol is not the same as outgoing token_symbol.
    2.1: incoming_symbol is "XTZ": no incoming_amount, outgoing_amount will be sent.
    2.2: outgoing_symbol is "XTZ": incoming_amount will be sent, outgoing_amount will be sent.
    2.3: both symbols are not "XTZ": incoming amount will be sent, outgoing_amount will be sent.
    (2.2 and 2.3 are the same, but need to be treated differently at transfers) *)
      let ops = ([] : operation list) in
      let ops =
        (* 1 *)
        if param.token_symbol = offer.token_symbol then
          (* 1.1 *)
          if param.token_symbol = "XTZ" then
            (* check that values are valid *)
            if mutez_to_natural (Tezos.get_amount ()) <> param.ft_amount then
              (failwith(error_OFFER_VALUE_IS_NOT_EQUAL_TO_XTZ_AMOUNT) : operation list)
            else
              xtz_transfer (Tezos.get_sender ()) (natural_to_mutez offer.value) :: ops
          else
            (* 1.2 *)
            match is_nat (param.ft_amount - offer.value) with
            | None -> 
              fa_transfer ops (abs (offer.value - param.ft_amount)) param.token_symbol (Tezos.get_self_address ()) (Tezos.get_sender ()) store
            | Some n -> 
              if n <> 0n then 
                fa_transfer ops n param.token_symbol (Tezos.get_sender ()) (Tezos.get_self_address ()) store
              else 
                ops
        else
          (* 2.1 *)
          if param.token_symbol = "XTZ" then
            fa_transfer ops offer.value offer.token_symbol (Tezos.get_self_address ()) (Tezos.get_sender ()) store
          else if offer.token_symbol = "XTZ" then
            let ops = fa_transfer ops param.ft_amount param.token_symbol (Tezos.get_sender ()) (Tezos.get_self_address ()) store in
            let ops = xtz_transfer (Tezos.get_sender ()) (natural_to_mutez offer.value) :: ops in
            ops
          else
            let ops = fa_transfer ops param.ft_amount param.token_symbol (Tezos.get_sender ()) (Tezos.get_self_address ()) store in
            let ops = fa_transfer ops offer.value offer.token_symbol (Tezos.get_self_address ()) (Tezos.get_sender ()) store in
            (* 2.2 and 2.3 *)
            ops in
      let new_offers = Big_map.update offer_id (Some new_offer) store.offers in
      ops, {store with offers = new_offers}

let make_counter_offer (param : counter_offer_param) (store : storage) : return =
  if store.paused then
    (failwith(error_MARKETPLACE_IS_PAUSED) : return)
  else if (not Set.mem param.token_origin store.collections) then
    (failwith(error_TOKEN_ORIGIN_NOT_LISTED) : return)
  else if param.start_time >= param.end_time then
    (failwith(error_START_TIME_IS_LATER_THAN_END_TIME) : return)
  else 
    let () = match Big_map.find_opt param.token_symbol store.allowed_tokens with
    | None -> (failwith(error_TOKEN_SYMBOL_UNLISTED) : unit)
    | Some _ -> () in
    let counter_offer_id =
    {
      token_id = param.token_id;
      token_origin = param.token_origin;
      buyer = param.buyer;
      seller = (Tezos.get_sender ());
    } in
    let token_key =
      {
        token_id = param.token_id;
        token_origin = param.token_origin;
      } in
    let counter_offer =
      match Big_map.find_opt counter_offer_id store.counter_offers with
      | Some _ -> (failwith(error_COUNTER_OFFER_ALREADY_EXISTS) : counter_offer)
      | None -> 
        {
          start_time = param.start_time;
          end_time = param.end_time;
          token_symbol = param.token_symbol;
          ft_amount = param.ft_amount;
          seller = (Tezos.get_sender ());
        } in
      let (tokens, swaps, ops) = 
        match Big_map.find_opt token_key store.tokens with
        | None -> 
          store.tokens, 
          store.swaps,
          [
          token_transfer
            param.token_origin
            [
              {
                from_ = (Tezos.get_sender ());
                txs =
                  [
                    {
                      to_ = (Tezos.get_self_address ());
                      token_id = param.token_id;
                      amount = 1n;
                    }
                  ]
              }
            ]
        ]
        | Some swap_id -> 
          let _swap =
            match Big_map.find_opt swap_id store.swaps with
            | Some swap -> 
              if (Tezos.get_sender ()) <> swap.owner then
                (failwith error_SENDER_DOES_NOT_OWN_THE_TOKEN : swap_info)
              else swap
            | None -> (failwith "not possible" : swap_info) in
          Big_map.update token_key (None : swap_id option) store.tokens,
          Big_map.update swap_id (None : swap_info option) store.swaps,
          ([] : operation list) in
      let new_counter_offers = Big_map.update counter_offer_id (Some counter_offer) store.counter_offers in
      let new_store = { store with counter_offers = new_counter_offers; tokens = tokens; swaps = swaps } in
      ops, new_store

let accept_counter_offer (param : accept_counter_offer_param) (store : storage) : return =
  if store.paused then
    (failwith(error_MARKETPLACE_IS_PAUSED) : return)
  else
    let offer_id =
      {
        token_id = param.token_id;
        buyer = (Tezos.get_sender ());
        token_origin = param.token_origin;
      } in
    let counter_offer_id =
      {
        token_id = param.token_id;
        buyer = (Tezos.get_sender ());
        seller = param.seller;
        token_origin = param.token_origin;
      } in
    let token_key =
      {
        token_id = param.token_id;
        token_origin = param.token_origin;
      } in
    let (offer, new_offers) = 
      match Big_map.find_opt offer_id store.offers with
      | None -> (failwith(error_NO_OFFER_PLACED) : offer_info * (offer_id, offer_info) big_map)
      | Some offer -> offer, Big_map.update offer_id (None : offer_info option) store.offers in
    let (counter_offer, new_counter_offers) =
      match Big_map.find_opt counter_offer_id store.counter_offers with
      | None -> (failwith(error_NO_COUNTER_OFFER) : counter_offer * (counter_offer_id, counter_offer) big_map)
      | Some counter_offer -> counter_offer, Big_map.update counter_offer_id (None : counter_offer option) store.counter_offers in
    if (Tezos.get_now ()) < counter_offer.start_time then
      (failwith(error_COUNTER_OFFER_NOT_ACTIVE_YET) : return)
    else if (not (counter_offer.token_symbol = "XTZ")) && (Tezos.get_amount ()) <> 0tez then
      (failwith(error_NO_XTZ_AMOUNT_TO_BE_SENT) : return)
    else if (Tezos.get_now ()) > counter_offer.end_time then
      (failwith(error_COUNTER_OFFER_NOT_ACTIVE_ANYMORE) : return)
    else if counter_offer.token_symbol = "XTZ" && mutez_to_natural (Tezos.get_amount ()) <> counter_offer.ft_amount then
      (failwith(error_AMOUNT_IS_NOT_EQUAL_TO_PRICE) : return)
    else 
    // return original offer to buyer
    // get transaction details
      let management_fee = counter_offer.ft_amount * store.management_fee_rate / const_FEE_DENOM in
    let royalties = store.royalties_rate * counter_offer.ft_amount / const_FEE_DENOM in
      let seller_value =
        match is_nat (counter_offer.ft_amount - (management_fee + royalties)) with
        | None -> (failwith error_FEE_GREATER_THAN_AMOUNT : nat)
        | Some n -> n in
      (* operation assignment *)
      let ops = ([] : operation list) in
      (* token transfer *)
      let ops = 
        token_transfer 
          param.token_origin
          [
            {
              from_ = (Tezos.get_self_address ()); 
              txs = 
                [
                  { 
                    to_ = (Tezos.get_sender ()); 
                    token_id = param.token_id; 
                    amount = 1n;
                  }
                ]
            }
          ] :: ops in
      (* payment transfers *)
      (* return original offer to buyer *)
      let ops = payment_transfer ops offer.value offer.token_symbol (Tezos.get_self_address ()) (Tezos.get_sender ()) store in
      (* seller payment operation *)
      let ops = payment_transfer ops seller_value counter_offer.token_symbol (Tezos.get_sender ()) param.seller store in
      (* royalties payment operation *)
      let ops = payment_transfer ops royalties counter_offer.token_symbol (Tezos.get_sender ()) store.royalties_address store in
      (* management fee payment operation *)
      let ops = payment_transfer ops management_fee counter_offer.token_symbol (Tezos.get_sender ()) store.treasury store in
      let new_tokens = 
        match Big_map.find_opt token_key store.tokens with
        | None -> store.tokens
        | Some _swap_id ->
          Big_map.update token_key (None : swap_id option) store.tokens in
      let new_store =
        { store with
          offers = new_offers;
          counter_offers = new_counter_offers;
          tokens = new_tokens
        } in
      (ops, new_store)


let withdraw_offer (param : withdraw_offer_param) (store : storage) : return =
    let offer_id =
        {
          token_id = param.token_id;
          token_origin = param.token_origin;
          buyer = (Tezos.get_sender ());
        } in
    match Big_map.find_opt offer_id store.offers with
    | None -> (failwith(error_NO_OFFER_PLACED) : return)
    | Some offer ->
      let ops = ([] : operation list) in
      let ops = payment_transfer ops offer.value offer.token_symbol (Tezos.get_self_address ()) (Tezos.get_sender ()) store in
      let new_offers = Big_map.update offer_id (None : offer_info option) store.offers in
      let new_store = { store with offers = new_offers } in
      ops, new_store

let withdraw_counter_offer (param : withdraw_counter_offer_param) (store : storage) : return =
    let counter_offer_id =
      {
        token_id = param.token_id;
        buyer = param.buyer;
        seller = (Tezos.get_sender ());
        token_origin = param.token_origin;
      } in
    if (not Big_map.mem counter_offer_id store.counter_offers) then
      (failwith(error_NO_COUNTER_OFFER) : return)
    else
      let ops =
        [token_transfer 
            param.token_origin
            [
              {
                from_ = (Tezos.get_self_address ()); 
                txs = 
                  [
                    { 
                      to_ = (Tezos.get_sender ()); 
                      token_id = param.token_id; 
                      amount = 1n;
                    }
                  ]
              }
            ]]
        in
        let new_counter_offers = Big_map.update counter_offer_id (None : counter_offer option) store.counter_offers in
        ops, { store with counter_offers = new_counter_offers }
    


let accept_offer (param : accept_offer_param) (store : storage) : return =
  if store.paused then
    (failwith(error_MARKETPLACE_IS_PAUSED) : return)
  else
    let (owner, buyer, token_id) = ((Tezos.get_sender ()), param.buyer, param.token_id) in
    let offer_id = 
      {
          token_id = token_id;
          buyer = buyer;
          token_origin = param.token_origin;
        } in
    let token_key = 
      {
        token_id = param.token_id;
        token_origin = param.token_origin;
      } in
    let offer =
      match Big_map.find_opt offer_id store.offers with
      | None -> (failwith(error_OFFER_DOES_NOT_EXIST) : offer_info)
      | Some offer -> offer in
    if (Tezos.get_now ()) < offer.start_time then
      (failwith error_ACCEPTING_OFFER_IS_TOO_EARLY : return)
    else
    if (Tezos.get_now ()) > offer.end_time then
      (failwith error_ACCEPTING_OFFER_IS_TOO_LATE : return)
    else
      let management_fee = offer.value * store.management_fee_rate / const_FEE_DENOM in
      let royalties = store.royalties_rate * offer.value / const_FEE_DENOM in
      let seller_value =
        match is_nat (offer.value - (management_fee + royalties)) with
        | None -> (failwith error_FEE_GREATER_THAN_AMOUNT : nat)
        | Some n -> n in
      (* transfer tokens either from marketplace or from nft ledger. *)
      let (txs, swaps, tokens) =
        match Big_map.find_opt token_key store.tokens with
        | None ->
          ([{from_ = owner; txs = [{ to_ = buyer; token_id = token_id; amount = 1n }]}], store.swaps, store.tokens)
        | Some swap_id -> 
          let swap = match Big_map.find_opt swap_id store.swaps with
          | None -> (failwith(error_SWAP_ID_DOES_NOT_EXIST) : swap_info)
          | Some swap -> swap in
          if owner <> swap.owner then
            (failwith(error_CALLER_NOT_PERMITTED_TO_ACCEPT_OFFER) : (transfer list * (swap_id, swap_info) big_map * (token_key, swap_id) big_map))
          else
            [{from_ = (Tezos.get_self_address ()); txs = [{ to_ = buyer; token_id = token_id; amount = 1n }]}],
            Big_map.update swap_id (None : swap_info option) store.swaps,
            Big_map.update token_key (None : swap_id option) store.tokens in 
      (* operation assignment *)
      let ops = ([] : operation list) in
      let ops = token_transfer param.token_origin txs :: ops in
      (* payment transfers *)
      (* seller payment operation *)
      let ops = payment_transfer ops seller_value offer.token_symbol (Tezos.get_self_address ()) owner store in
      (* royalties payment operation *)
      let ops = payment_transfer ops royalties offer.token_symbol (Tezos.get_self_address ()) store.royalties_address store in
      (* management fee payment operation *)
      let ops = payment_transfer ops management_fee offer.token_symbol (Tezos.get_self_address ()) store.treasury store in
      let new_offers = Big_map.update offer_id (None : offer_info option) store.offers in
      let new_store =
        { store with
          offers = new_offers;
          swaps = swaps;
          tokens = tokens
        } in
      (ops, new_store)

let update_admin (param : address) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.admin then
    (failwith("not admin") : return)
  else
    ([] : operation list), {store with admin = param}


let main (action, store : parameter * storage) : return =
 match action with
 | SetPause p -> set_pause p store
 | AddCollection p -> add_collection p store
 | RemoveCollection p -> remove_collection p store
 | UpdateRoyaltiesAddress p -> update_royalties_address p store
 | UpdateTreasuryAddress p -> update_treasury_address p store
 | UpdateFee p -> update_fee p store
 | UpdateOracleAddress p -> update_oracle_address p store
 | UpdateRoyalties p -> update_royalties p store
 | UpdateAllowedTokens p -> update_allowed_tokens p store
 | SetOracleTolerance p -> set_oracle_tolerance p store
 | UpdateAdmin p -> update_admin p store
//  | UpdateMultisig p -> update_multisig p store
 | AddToMarketplace p -> add_to_marketplace p store
 | RemoveFromMarketplace p -> remove_from_marketplace p store
 | Collect p ->  collect p store
 | SendOffer p -> send_offer p store
 | UpdateOffer p -> update_offer p store
 | WithdrawOffer p -> withdraw_offer p store
 | MakeCounterOffer p -> make_counter_offer p store
 | WithdrawCounterOffer p -> withdraw_counter_offer p store
 | AcceptCounterOffer p -> accept_counter_offer p store
 | AcceptOffer p -> accept_offer p store
 | UpdateSwap p -> update_swap p store
