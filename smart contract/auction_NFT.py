##
## ## Introduction
##
## See the FA2 standard definition:
## <https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-12/>
##
## See more examples/documentation at
## <https://gitlab.com/smondet/fa2-smartpy/> and
## <https://assets.tqtezos.com/docs/token-contracts/fa2/1-fa2-smartpy/>.
##
import smartpy as sp
##
## ## Meta-Programming Configuration
##
## The `FA2_config` class holds the meta-programming configuration.
##
class FA2_config:
    def __init__(self,
                 debug_mode                         = False,
                 single_asset                       = False,
                 non_fungible                       = False,
                 add_mutez_transfer                 = False,
                 readable                           = True,
                 force_layouts                      = True,
                 support_operator                   = True,
                 assume_consecutive_token_ids       = True,
                 store_total_supply                 = True,
                 lazy_entry_points                  = False,
                 allow_self_transfer                = False,
                 use_token_metadata_offchain_view   = False
                 ):

        if debug_mode:
            self.my_map = sp.map
        else:
            self.my_map = sp.big_map
        # The option `debug_mode` makes the code generation use
        # regular maps instead of big-maps, hence it makes inspection
        # of the state of the contract easier.

        self.use_token_metadata_offchain_view = use_token_metadata_offchain_view
        # Include offchain view for accessing the token metadata (requires TZIP-016 contract metadata)

        self.single_asset = single_asset
        # This makes the contract save some gas and storage by
        # working only for the token-id `0`.

        self.non_fungible = non_fungible
        # Enforce the non-fungibility of the tokens, i.e. the fact
        # that total supply has to be 1.

        self.readable = readable
        # The `readable` option is a legacy setting that we keep around
        # only for benchmarking purposes.
        #
        # User-accounts are kept in a big-map:
        # `(user-address * token-id) -> ownership-info`.
        #
        # For the Babylon protocol, one had to use `readable = False`
        # in order to use `PACK` on the keys of the big-map.

        self.force_layouts = force_layouts
        # The specification requires all interface-fronting records
        # and variants to be *right-combs;* we keep
        # this parameter to be able to compare performance & code-size.

        self.support_operator = support_operator
        # The operator entry-points always have to be there, but there is
        # definitely a use-case for having them completely empty (saving
        # storage and gas when `support_operator` is `False).

        self.assume_consecutive_token_ids = assume_consecutive_token_ids
        # For a previous version of the TZIP specification, it was
        # necessary to keep track of the set of all tokens in the contract.
        #
        # The set of tokens is for now still available; this parameter
        # guides how to implement it:
        # If `true` we don't need a real set of token ids, just to know how
        # many there are.

        self.store_total_supply = store_total_supply
        # Whether to store the total-supply for each token (next to
        # the token-metadata).

        self.add_mutez_transfer = add_mutez_transfer
        # Add an entry point for the administrator to transfer tez potentially
        # in the contract's balance.

        self.lazy_entry_points = lazy_entry_points
        #
        # Those are “compilation” options of SmartPy into Michelson.
        #

        self.allow_self_transfer = allow_self_transfer
        # Authorize call of `transfer` entry_point from self
        name = "FA2"
        if debug_mode:
            name += "-debug"
        if single_asset:
            name += "-single_asset"
        if non_fungible:
            name += "-nft"
        if add_mutez_transfer:
            name += "-mutez"
        if not readable:
            name += "-no_readable"
        if not force_layouts:
            name += "-no_layout"
        if not support_operator:
            name += "-no_ops"
        if not assume_consecutive_token_ids:
            name += "-no_toknat"
        if not store_total_supply:
            name += "-no_totsup"
        if lazy_entry_points:
            name += "-lep"
        if allow_self_transfer:
            name += "-self_transfer"
        self.name = name

## ## Auxiliary Classes and Values
##
## The definitions below implement SmartML-types and functions for various
## important types.
##
token_id_type = sp.TNat

class Error_message:
    def __init__(self, config):
        self.config = config
        self.prefix = "FA2_"
        
    def make(self, s): return (self.prefix + s)
    def token_undefined(self):       return self.make("TOKEN_UNDEFINED")
    def insufficient_balance(self):  return self.make("INSUFFICIENT_BALANCE")
    def not_operator(self):          return self.make("NOT_OPERATOR")
    def not_owner(self):             return self.make("NOT_OWNER")
    def operators_unsupported(self): return self.make("OPERATORS_UNSUPPORTED")
    def not_admin(self):             return self.make("NOT_ADMIN")
    def not_admin_or_operator(self): return self.make("NOT_ADMIN_OR_OPERATOR")
    def paused(self):                return self.make("PAUSED")

## The current type for a batched transfer in the specification is as
## follows:
##
## ```ocaml
## type transfer = {
##   from_ : address;
##   txs: {
##     to_ : address;
##     token_id : token_id;
##     amount : nat;
##   } list
## } list
## ```
##
## This class provides helpers to create and force the type of such elements.
## It uses the `FA2_config` to decide whether to set the right-comb layouts.
class Batch_transfer:
    def __init__(self, config):
        self.config = config
    def get_transfer_type(self):
        tx_type = sp.TRecord(to_ = sp.TAddress,
                             token_id = token_id_type,
                             amount = sp.TNat)
        if self.config.force_layouts:
            tx_type = tx_type.layout(
                ("to_", ("token_id", "amount"))
            )
        transfer_type = sp.TRecord(from_ = sp.TAddress,
                                   txs = sp.TList(tx_type)).layout(
                                       ("from_", "txs"))
        return transfer_type
    def get_type(self):
        return sp.TList(self.get_transfer_type())
    def item(self, from_, txs):
        v = sp.record(from_ = from_, txs = txs)
        return sp.set_type_expr(v, self.get_transfer_type())
##
## `Operator_param` defines type types for the `%update_operators` entry-point.
class Operator_param:
    def __init__(self, config):
        self.config = config
    def get_type(self):
        t = sp.TRecord(
            owner = sp.TAddress,
            operator = sp.TAddress,
            token_id = token_id_type)
        if self.config.force_layouts:
            t = t.layout(("owner", ("operator", "token_id")))
        return t
    def make(self, owner, operator, token_id):
        r = sp.record(owner = owner,
                      operator = operator,
                      token_id = token_id)
        return sp.set_type_expr(r, self.get_type())

## The class `Ledger_key` defines the key type for the main ledger (big-)map:
##
## - In *“Babylon mode”* we also have to call `sp.pack`.
## - In *“single-asset mode”* we can just use the user's address.
class Ledger_key:
    def __init__(self, config):
        self.config = config
    def make(self, user, token):
        user = sp.set_type_expr(user, sp.TAddress)
        token = sp.set_type_expr(token, token_id_type)
        if self.config.single_asset:
            result = user
        else:
            result = sp.pair(user, token)
        if self.config.readable:
            return result
        else:
            return sp.pack(result)

## For now a value in the ledger is just the user's balance. Previous
## versions of the specification required more information; potential
## extensions may require other fields.
class Ledger_value:
    def get_type():
        return sp.TRecord(balance = sp.TNat)
    def make(balance):
        return sp.record(balance = balance)

## The link between operators and the addresses they operate is kept
## in a *lazy set* of `(owner × operator × token-id)` values.
##
## A lazy set is a big-map whose keys are the elements of the set and
## values are all `Unit`.
class Operator_set:
    def __init__(self, config):
        self.config = config
    def inner_type(self):
        return sp.TRecord(owner = sp.TAddress,
                          operator = sp.TAddress,
                          token_id = token_id_type
                          ).layout(("owner", ("operator", "token_id")))
    def key_type(self):
        if self.config.readable:
            return self.inner_type()
        else:
            return sp.TBytes
    def make(self):
        return self.config.my_map(tkey = self.key_type(), tvalue = sp.TUnit)
    def make_key(self, owner, operator, token_id):
        metakey = sp.record(owner = owner,
                            operator = operator,
                            token_id = token_id)
        metakey = sp.set_type_expr(metakey, self.inner_type())
        if self.config.readable:
            return metakey
        else:
            return sp.pack(metakey)
    def add(self, set, owner, operator, token_id):
        set[self.make_key(owner, operator, token_id)] = sp.unit
    def remove(self, set, owner, operator, token_id):
        del set[self.make_key(owner, operator, token_id)]
    def is_member(self, set, owner, operator, token_id):
        return set.contains(self.make_key(owner, operator, token_id))

class Balance_of:
    def request_type():
        return sp.TRecord(
            owner = sp.TAddress,
            token_id = token_id_type).layout(("owner", "token_id"))
    def response_type():
        return sp.TList(
            sp.TRecord(
                request = Balance_of.request_type(),
                balance = sp.TNat).layout(("request", "balance")))
    def entry_point_type():
        return sp.TRecord(
            callback = sp.TContract(Balance_of.response_type()),
            requests = sp.TList(Balance_of.request_type())
        ).layout(("requests", "callback"))

class Token_meta_data:
    def __init__(self, config):
        self.config = config

    def get_type(self):
        return sp.TRecord(token_id = sp.TNat, token_info = sp.TMap(sp.TString, sp.TBytes))

    def set_type_and_layout(self, expr):
        sp.set_type(expr, self.get_type())

## The set of all tokens is represented by a `nat` if we assume that token-ids
## are consecutive, or by an actual `(set nat)` if not.
##
## - Knowing the set of tokens is useful for throwing accurate error messages.
## - Previous versions of the specification required this set for functional
##   behavior (operators interface had to deal with “all tokens”).
class Token_id_set:
    def __init__(self, config):
        self.config = config
    def empty(self):
        if self.config.assume_consecutive_token_ids:
            # The "set" is its cardinal.
            return sp.nat(0)
        else:
            return sp.set(t = token_id_type)
    def add(self, metaset, v):
        if self.config.assume_consecutive_token_ids:
            sp.verify(metaset == v, message = "Token-IDs should be consecutive")
            metaset.set(sp.max(metaset, v + 1))
        else:
            metaset.add(v)
    def contains(self, metaset, v):
        if self.config.assume_consecutive_token_ids:
            return (v < metaset)
        else:
            return metaset.contains(v)
    def cardinal(self, metaset):
        if self.config.assume_consecutive_token_ids:
            return metaset
        else:
            return sp.len(metaset)

##
## ## Implementation of the Contract
##
## `mutez_transfer` is an optional entry-point, hence we define it “outside” the
## class:
def mutez_transfer(contract, params):
    sp.verify(sp.sender == contract.data.administrator)
    sp.set_type(params.destination, sp.TAddress)
    sp.set_type(params.amount, sp.TMutez)
    sp.send(params.destination, params.amount)
##
## The `FA2` class builds a contract according to an `FA2_config` and an
## administrator address.
## It is inheriting from `FA2_core` which implements the strict
## standard and a few other classes to add other common features.
##
## - We see the use of
##   [`sp.entry_point`](https://www.smartpy.io/dev/reference.html#_entry_points)
##   as a function instead of using annotations in order to allow
##   optional entry points.
## - The storage field `metadata_string` is a placeholder, the build
##   system replaces the field annotation with a specific version-string, such
##   as `"version_20200602_tzip_b916f32"`: the version of FA2-smartpy and
##   the git commit in the TZIP [repository](https://gitlab.com/tzip/tzip) that
##   the contract should obey.
class FA2_core(sp.Contract):
    def __init__(self, config, metadata, **extra_storage):
        self.config = config
        self.error_message = Error_message(self.config)
        self.operator_set = Operator_set(self.config)
        self.operator_param = Operator_param(self.config)
        self.token_id_set = Token_id_set(self.config)
        self.ledger_key = Ledger_key(self.config)
        self.token_meta_data = Token_meta_data(self.config)
        self.batch_transfer    = Batch_transfer(self.config)
        if  self.config.add_mutez_transfer:
            self.transfer_mutez = sp.entry_point(mutez_transfer)
        if config.lazy_entry_points:
            self.add_flag("lazy-entry-points")
        self.add_flag("initial-cast")
        self.exception_optimization_level = "default-line"
        self.init(
            ledger = self.config.my_map(tvalue = Ledger_value.get_type()),
            token_metadata = self.config.my_map(tkey = sp.TNat, tvalue = self.token_meta_data.get_type()),
            total_supply = self.config.my_map(tkey = sp.TNat, tvalue = sp.TNat),
            operators = self.operator_set.make(),
            all_tokens = self.token_id_set.empty(),
            metadata = metadata,
            recording_right=config.my_map(tkey=sp.TNat, tvalue=sp.TAddress),
            propagating_right=config.my_map(tkey=sp.TNat, tvalue=sp.TAddress),
            other_rights=config.my_map(tkey=sp.TNat, tvalue=sp.TAddress),
            **extra_storage
        )

    @sp.entry_point
    def transfer(self, params):
        sp.verify( ~self.is_paused(), message = self.error_message.paused() )
        sp.set_type(params, self.batch_transfer.get_type())
        sp.for transfer in params:
           current_from = transfer.from_
           sp.for tx in transfer.txs:
                if self.config.single_asset:
                    sp.verify(tx.token_id == 0, message = "single-asset: token-id <> 0")

                sender_verify = ((self.is_administrator(sp.sender)) |
                                (current_from == sp.sender))
                message = self.error_message.not_owner()
                if self.config.support_operator:
                    message = self.error_message.not_operator()
                    sender_verify |= (self.operator_set.is_member(self.data.operators,
                                                                  current_from,
                                                                  sp.sender,
                                                                  tx.token_id))
                if self.config.allow_self_transfer:
                    sender_verify |= (sp.sender == sp.self_address)
                sp.verify(sender_verify, message = message)
                sp.verify(
                    self.data.token_metadata.contains(tx.token_id),
                    message = self.error_message.token_undefined()
                )
                # If amount is 0 we do nothing now:
                sp.if (tx.amount > 0):
                    from_user = self.ledger_key.make(current_from, tx.token_id)
                    sp.verify(
                        (self.data.ledger[from_user].balance >= tx.amount),
                        message = self.error_message.insufficient_balance())
                    to_user = self.ledger_key.make(tx.to_, tx.token_id)
                    self.data.ledger[from_user].balance = sp.as_nat(
                        self.data.ledger[from_user].balance - tx.amount)
                    sp.if self.data.ledger.contains(to_user):
                        self.data.ledger[to_user].balance += tx.amount
                    sp.else:
                         self.data.ledger[to_user] = Ledger_value.make(tx.amount)
                sp.else:
                    pass

    @sp.entry_point
    def balance_of(self, params):
        # paused may mean that balances are meaningless:
        sp.verify( ~self.is_paused(), message = self.error_message.paused())
        sp.set_type(params, Balance_of.entry_point_type())
        def f_process_request(req):
            user = self.ledger_key.make(req.owner, req.token_id)
            sp.verify(self.data.token_metadata.contains(req.token_id), message = self.error_message.token_undefined())
            sp.if self.data.ledger.contains(user):
                balance = self.data.ledger[user].balance
                sp.result(
                    sp.record(
                        request = sp.record(
                            owner = sp.set_type_expr(req.owner, sp.TAddress),
                            token_id = sp.set_type_expr(req.token_id, sp.TNat)),
                        balance = balance))
            sp.else:
                sp.result(
                    sp.record(
                        request = sp.record(
                            owner = sp.set_type_expr(req.owner, sp.TAddress),
                            token_id = sp.set_type_expr(req.token_id, sp.TNat)),
                        balance = 0))
        res = sp.local("responses", params.requests.map(f_process_request))
        destination = sp.set_type_expr(params.callback, sp.TContract(Balance_of.response_type()))
        sp.transfer(res.value, sp.mutez(0), destination)

    @sp.offchain_view(pure = True)
    def get_balance(self, req):
        """This is the `get_balance` view defined in TZIP-12."""
        sp.set_type(
            req, sp.TRecord(
                owner = sp.TAddress,
                token_id = sp.TNat
            ).layout(("owner", "token_id")))
        user = self.ledger_key.make(req.owner, req.token_id)
        sp.verify(self.data.token_metadata.contains(req.token_id), message = self.error_message.token_undefined())
        sp.result(self.data.ledger[user].balance)


    @sp.entry_point
    def update_operators(self, params):
        sp.set_type(params, sp.TList(
            sp.TVariant(
                add_operator = self.operator_param.get_type(),
                remove_operator = self.operator_param.get_type()
            )
        ))
        if self.config.support_operator:
            sp.for update in params:
                with update.match_cases() as arg:
                    with arg.match("add_operator") as upd:
                        sp.verify(
                            (upd.owner == sp.sender) | self.is_administrator(sp.sender),
                            message = self.error_message.not_admin_or_operator()
                        )
                        self.operator_set.add(self.data.operators,
                                              upd.owner,
                                              upd.operator,
                                              upd.token_id)
                    with arg.match("remove_operator") as upd:
                        sp.verify(
                            (upd.owner == sp.sender) | self.is_administrator(sp.sender),
                            message = self.error_message.not_admin_or_operator()
                        )
                        self.operator_set.remove(self.data.operators,
                                                 upd.owner,
                                                 upd.operator,
                                                 upd.token_id)
        else:
            sp.failwith(self.error_message.operators_unsupported())

    # this is not part of the standard but can be supported through inheritance.
    def is_paused(self):
        return sp.bool(False)

    # this is not part of the standard but can be supported through inheritance.
    def is_administrator(self, sender):
        return sp.bool(False)

class FA2_administrator(FA2_core):
    def is_administrator(self, sender):
        return sender == self.data.administrator

    @sp.entry_point
    def set_administrator(self, params):
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        self.data.administrator = params

class FA2_pause(FA2_core):
    def is_paused(self):
        return self.data.paused

    @sp.entry_point
    def set_pause(self, params):
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        self.data.paused = params

class FA2_change_metadata(FA2_core):
    @sp.entry_point
    def set_metadata(self, k, v):
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        self.data.metadata[k] = v

class FA2_mint(FA2_core):
    @sp.entry_point
    def mint(self, params):
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        # We don't check for pauseness because we're the admin.
        if self.config.single_asset:
            sp.verify(params.token_id == 0, message = "single-asset: token-id <> 0")
        if self.config.non_fungible:
            sp.verify(params.amount == 1, message = "NFT-asset: amount <> 1")
            sp.verify(
                ~ self.token_id_set.contains(self.data.all_tokens, params.token_id),
                message = "NFT-asset: cannot mint twice same token"
            )
        user = self.ledger_key.make(params.address, params.token_id)
        self.token_id_set.add(self.data.all_tokens, params.token_id)
        sp.if self.data.ledger.contains(user):
            self.data.ledger[user].balance += params.amount
        sp.else:
            self.data.ledger[user] = Ledger_value.make(params.amount)
        sp.if self.data.token_metadata.contains(params.token_id):
            pass
        sp.else:
            self.data.token_metadata[params.token_id] = sp.record(
                token_id    = params.token_id,
                token_info  = params.metadata
            )
            self.data.total_supply[params.token_id] = params.amount
        # approve all right   
        self.data.recording_right[params.token_id] = params.address
        self.data.propagating_right[params.token_id] = params.address
        self.data.other_rights[params.token_id] = params.address


class FA2_token_metadata(FA2_core):
    def set_token_metadata_view(self):
        def token_metadata(self, tok):
            """
            Return the token-metadata URI for the given token.

            For a reference implementation, dynamic-views seem to be the
            most flexible choice.
            """
            sp.set_type(tok, sp.TNat)
            sp.result(self.data.token_metadata[tok])

        self.token_metadata = sp.offchain_view(pure = True, doc = "Get Token Metadata")(token_metadata)

    def make_metadata(symbol, name, decimals):
        "Helper function to build metadata JSON bytes values."
        return (sp.map(l = {
            # Remember that michelson wants map already in ordered
            "decimals" : sp.utils.bytes_of_string("%d" % decimals),
            "name" : sp.utils.bytes_of_string(name),
            "symbol" : sp.utils.bytes_of_string(symbol)
        }))

    @sp.entry_point
    def set_token_metadata(self, token_id, metadata):
        # set type 
        sp.set_type(token_id, sp.TNat)

        # only administrator can change token metatdata, check first
        sp.verify(self.is_administrator(sp.sender), message = self.error_message.not_admin())
        
        # check the toke_id does exist!
        sp.verify(self.data.token_metadata.contains(token_id), "the toke_id does not exist!")

        # locate the token_id record,then replace it.
        sp.if token_id == self.data.token_metadata[token_id].token_id :
            self.data.token_metadata[token_id] = sp.record(
                token_id    = token_id,
                token_info  = metadata ) 
            return

class FA2_right(FA2_core):
    @sp.entry_point
    def transfer(self, params):
        sp.verify( ~self.is_paused(), message = self.error_message.paused() )
        sp.set_type(params, self.batch_transfer.get_type())
        sp.for transfer in params:
           current_from = transfer.from_
           sp.for tx in transfer.txs:
                if self.config.single_asset:
                    sp.verify(tx.token_id == 0, message = "single-asset: token-id <> 0")

                sender_verify = ((self.is_administrator(sp.sender)) |
                                (current_from == sp.sender))
                message = self.error_message.not_owner()
                if self.config.support_operator:
                    message = self.error_message.not_operator()
                    sender_verify |= (self.operator_set.is_member(self.data.operators,
                                                                  current_from,
                                                                  sp.sender,
                                                                  tx.token_id))
                if self.config.allow_self_transfer:
                    sender_verify |= (sp.sender == sp.self_address)
                sp.verify(sender_verify, message = message)
                sp.verify(
                    self.data.token_metadata.contains(tx.token_id),
                    message = self.error_message.token_undefined()
                )
                # If amount is 0 we do nothing now:
                sp.if (tx.amount > 0):
                    from_user = self.ledger_key.make(current_from, tx.token_id)
                    sp.verify(
                        (self.data.ledger[from_user].balance >= tx.amount),
                        message = self.error_message.insufficient_balance())
                    to_user = self.ledger_key.make(tx.to_, tx.token_id)
                    self.data.ledger[from_user].balance = sp.as_nat(
                        self.data.ledger[from_user].balance - tx.amount)
                    sp.if self.data.ledger.contains(to_user):
                        self.data.ledger[to_user].balance += tx.amount
                    sp.else:
                         self.data.ledger[to_user] = Ledger_value.make(tx.amount)
                     # approve all right
                    sp.verify((self.data.recording_right[tx.token_id] == current_from) &
                            (self.data.propagating_right[tx.token_id] == current_from) &
                            (self.data.other_rights[tx.token_id] == current_from), message="NO ALL RIGHT")
                    self.data.recording_right[tx.token_id] = tx.to_
                    self.data.propagating_right[tx.token_id] = tx.to_
                    self.data.other_rights[tx.token_id] = tx.to_
                sp.else:
                    pass

    @sp.entry_point
    def transferRecordingRight(self, params):
        # only administrator can change or owner token metatdata, check first
        sp.verify((sp.sender == self.data.administrator) | (self.data.recording_right[params.token_id] == sp.sender),
                  message=self.error_message.not_admin_or_operator())
        self.data.recording_right[params.token_id] = params.address


    @sp.entry_point
    def transferPropagatingRight(self, params):
        # only administrator can change or owner token metatdata, check first
        user = self.ledger_key.make(sp.sender, params.token_id)
        isOwner = False
        sp.if self.data.ledger.contains(user):
             isOwner = self.data.ledger[user].balance > 0

        sp.verify((sp.sender == self.data.administrator) | (self.data.propagating_right[params.token_id] == sp.sender) | isOwner,
                  message=self.error_message.not_admin_or_operator())
        self.data.propagating_right[params.token_id] = params.address


    @sp.entry_point
    def transferOtherRightsRight(self, params):
        # only administrator can change or owner token metatdata, check first
        user = self.ledger_key.make(sp.sender, params.token_id)
        isOwner = False
        sp.if self.data.ledger.contains(user):
            isOwner = self.data.ledger[user].balance > 0

        sp.verify((sp.sender == self.data.administrator) | (self.data.other_rights[params.token_id] == sp.sender) | isOwner,
                  message=self.error_message.not_admin_or_operator())
        self.data.other_rights[params.token_id] = params.address


    @sp.entry_point
    def transferAllRight(self, params):
        # only administrator can change or owner token metatdata, check first
        user = self.ledger_key.make(sp.sender, params.token_id)
        isOwner = False
        sp.if self.data.ledger.contains(user):
            isOwner = self.data.ledger[user].balance > 0

        sp.verify((sp.sender == self.data.administrator) | isOwner,
                  message=self.error_message.not_admin_or_operator())

        self.data.recording_right[params.token_id] = params.recordingRightAddress
        self.data.propagating_right[params.token_id] = params.propagatingRightAddress
        self.data.other_rights[params.token_id] = params.otherRightsAddress


    def getRecordingRight(self, params):
        # sp.verify(~self.is_administrator(sp.sender) & self.data.recording_right.set[params.token_id] != sp.sender,
        #           message=self.error_message.not_admin_or_operator())
        sp.result(self.data.recording_right[params.token_id])


    def getPropagatingRight(self, params):
        # sp.verify(~self.is_administrator(sp.sender) & self.data.recording_right.set[params.token_id] != sp.sender,
        #           message=self.error_message.not_admin_or_operator())
        sp.result(self.data.propagating_right[params.token_id])


    def getRightsRight(self, params):
        # sp.verify(~self.is_administrator(sp.sender) & self.data.recording_right.set[params.token_id] != sp.sender,
        #           message=self.error_message.not_admin_or_operator())
        sp.result(self.data.other_rights[params.token_id])



class FA2(FA2_change_metadata, FA2_token_metadata, FA2_mint, FA2_administrator, FA2_pause, FA2_right, FA2_core):

    @sp.offchain_view(pure = True)
    def count_tokens(self):
        """Get how many tokens are in this FA2 contract.
        """
        sp.result(self.token_id_set.cardinal(self.data.all_tokens))

    @sp.offchain_view(pure = True)
    def does_token_exist(self, tok):
        "Ask whether a token ID is exists."
        sp.set_type(tok, sp.TNat)
        sp.result(self.data.token_metadata.contains(tok))

    @sp.offchain_view(pure = True)
    def all_tokens(self):
        if self.config.assume_consecutive_token_ids:
            sp.result(sp.range(0, self.data.all_tokens))
        else:
            sp.result(self.data.all_tokens.elements())

    @sp.offchain_view(pure = True)
    def total_supply(self, tok):
        if self.config.store_total_supply:
            sp.result(self.data.total_supply[tok])
        else:
            sp.set_type(tok, sp.TNat)
            sp.result("total-supply not supported")

    @sp.offchain_view(pure = True)
    def is_operator(self, query):
        sp.set_type(query,
                    sp.TRecord(token_id = sp.TNat,
                               owner = sp.TAddress,
                               operator = sp.TAddress).layout(
                                   ("owner", ("operator", "token_id"))))
        sp.result(
            self.operator_set.is_member(self.data.operators,
                                        query.owner,
                                        query.operator,
                                        query.token_id)
        )

    def __init__(self, config, metadata, admin):
        # Let's show off some meta-programming:
        if config.assume_consecutive_token_ids:
            self.all_tokens.doc = """
            This view is specified (but optional) in the standard.

            This contract is built with assume_consecutive_token_ids =
            True, so we return a list constructed from the number of tokens.
            """
        else:
            self.all_tokens.doc = """
            This view is specified (but optional) in the standard.

            This contract is built with assume_consecutive_token_ids =
            False, so we convert the set of tokens from the storage to a list
            to fit the expected type of TZIP-16.
            """
        list_of_views = [
            self.get_balance
            , self.does_token_exist
            , self.count_tokens
            , self.all_tokens
            , self.is_operator
        ]

        if config.store_total_supply:
            list_of_views = list_of_views + [self.total_supply]
        if config.use_token_metadata_offchain_view:
            self.set_token_metadata_view()
            list_of_views = list_of_views + [self.token_metadata]

        metadata_base = {
            "version": config.name # will be changed if using fatoo.
            , "description" : (
                "This is a didactic reference implementation of FA2,"
                + " a.k.a. TZIP-012, using SmartPy.\n\n"
                + "This particular contract uses the configuration named: "
                + config.name + "."
            )
            , "interfaces": ["TZIP-012", "TZIP-016"]
            , "authors": [
                "Seb Mondet <https://seb.mondet.org>"
            ]
            , "homepage": "https://gitlab.com/smondet/fa2-smartpy"
            , "views": list_of_views
            , "source": {
                "tools": ["SmartPy"]
                , "location": "https://gitlab.com/smondet/fa2-smartpy.git"
            }
            , "permissions": {
                "operator":
                "owner-or-operator-transfer" if config.support_operator else "owner-transfer"
                , "receiver": "owner-no-hook"
                , "sender": "owner-no-hook"
            }
            , "fa2-smartpy": {
                "configuration" :
                dict([(k, getattr(config, k)) for k in dir(config) if "__" not in k and k != 'my_map'])
            }
        }
        self.init_metadata("metadata_base", metadata_base)
        FA2_core.__init__(self, config, metadata, paused = False, administrator = admin)

## ## 
##
## ### NftAuctionMarket Contract
##
## The NftAuctionMarket contract is used to exchange NFT.FA2 token to XTZ with auction.
## according to the seller's setting.
## param _admin:the market administrator address
## param _nftAddress: the _FA2.NFT contract address
## 
class  NftAuctionMarket(sp.Contract):

    ## __init__: constructor function
    def __init__(self, _admin,_nftAddress):
        # Define the contract storage data types for clarity
        self.init_type(sp.TRecord(
            ## contract management
            administrator = sp.TAddress,
            nftContractAddress = sp.TAddress,

            ## authorMap
            ## the author's related works can be found from goodsStoreMap.
            authorMap = sp.TMap(sp.TNat, sp.TRecord(
                    name =  sp.TString,
                    account =  sp.TString,
                    headPortrait =  sp.TString,
                    email =  sp.TString,
                    phone = sp.TString,
                    description = sp.TString,
                    address = sp.TAddress) ),

            ## goods management for which NFT to sale
            goodsStoreMap = sp.TMap(sp.TNat, sp.TRecord(
                ### the author 
                authorID = sp.TNat,
                ### the auction information
                sellerAddress =  sp.TAddress,
                #auctionType = sp.TBounded(["theEnglishAuction", "theDutchAuction"]),
                auctionTypeEnglish = sp.TBool,
                startTime = sp.TTimestamp,
                stopTime = sp.TTimestamp,
                startPrice = sp.TMutez,
                minStep = sp.TMutez,
                ### the dynamic bidding information
                currentBidder = sp.TOption(sp.TAddress),
                currentPrice = sp.TMutez,
                currentRSAPublicKey = sp.TString,
                EncryptedSrcUrl  = sp.TString,
                #status = sp.TBounded(["Initial", "Bidding", "Ended"])
                status = sp.TVariant(status = sp.TString)                
            ) ),

            ## fans donation records
            #key variable：recordNO, authorID, tokenID, sponsorAddr,endTime - donation end time, 
            # donationValue - donation total value record, withdrawableValue - the amount which the author can withdraw.
            # Map(donatorNo. [donatorAddr, donatorValue, donatorTime, donationID]) - any one can donate more can one time.
            # donationID的规则：TEZOS-recordNO-authorID-tokenID-donatorAddr-donatorValue-donatorTime     
            donationRecordsMap = sp.TMap(sp.TNat, sp.TRecord(     
                    authorID = sp.TNat,
                    tokenID = sp.TNat,
                    sponsorAddr = sp.TAddress,
                    endTime = sp.TTimestamp,
                    donationValue = sp.TMutez,
                    withdrawableValue = sp.TMutez,
                    donatorMap =  sp.TMap(sp.TNat, sp.TRecord(
                            donatorAddr = sp.TAddress,
                            donatorValue = sp.TMutez,
                            donatorTime = sp.TTimestamp,
                            donationID = sp.TString
                    ) ),
            ) ),

            ## Fans participation for voting records
            ## voteMap key valuable: recordNO, authorID, tokenID, totalNum, Map(voterAddr,voteNum)
            voteRecordsMap = sp.TMap(sp.TNat, sp.TRecord(    
                        authorID = sp.TNat,
                        tokenID = sp.TNat,
                        beginTime = sp.TTimestamp,
                        endTime = sp.TTimestamp,
                        totalNum  = sp.TNat,
                        votersMap =  sp.TMap(sp.TAddress,sp.TNat)
            ) ),

            ## Ranking and selection mechanism
            # rankingMap key valuable: tokenID, volume, 
            # sellers(address, num) - be seller times, buyers(address, bool) - be buyer times
            rankingMaps = sp.TMap(sp.TNat, sp.TRecord(    
                    volume =  sp.TMutez,
                    sellers = sp.TMap(sp.TAddress,sp.TNat),
                    buyers = sp.TMap(sp.TAddress,sp.TNat)
            ) ),

            ## IP assets protection
            #  IP assets protection as DCI certification: tokenID, DCI, registerID, worksName, worksType, authorName, 
            # finishedDate, firstPublishedDate, registeredDate
            ipAssetsCert = sp.TMap(sp.TNat, sp.TRecord(    
                    DCI =   sp.TString,
                    registerID = sp.TString,
                    worksName = sp.TString,
                    worksType = sp.TString,
                    authorName = sp.TString,
                    finishedDate = sp.TString,
                    firstPublishedDate = sp.TString,
                    registeredDate = sp.TString
            ) ),   

        ) )

        # Initialize the contract storage
        self.init(
            administrator = _admin,
            nftContractAddress = _nftAddress,
            goodsStoreMap = sp.map(),
            authorMap = sp.map(),
            donationRecordsMap = sp.map(),
            voteRecordsMap = sp.map(),
            rankingMaps = sp.map(),
            ipAssetsCert= sp.map()
        )

    ##
    ## ## withdrawContractXTZ
    ##
    ## administrater can withdraw the balance of XTZ from the contract in some exceptional condition.
    ## 
    @sp.entry_point     
    def withdrawContractXTZ(self, _destination, _amount):
        # 1. Initial the input parameters.
        sp.set_type(_destination, sp.TAddress)
        sp.set_type(_amount, sp.TMutez)

        # 2. only administrator can withdraw XTZ in  TMutez amount
        sp.verify(sp.sender == self.data.administrator,"only administrator can withdraw XTZ from the contract!")  

        # 3. withdraw XTZ
        sp.send(_destination, _amount)  

    ##
    ## ## updateManagementParameters
    ##
    ## administrater can update the management parameters.
    ## 
    @sp.entry_point     
    def updateManagementParameters(self, _admin,_nftAddress):
        '"UpdateParameters"'
        
        # 1. Initial the input parameter types
        sp.set_type(_admin, sp.TOption(sp.TAddress))
        sp.set_type(_nftAddress, sp.TOption(sp.TAddress))

        # 2. check the sender is the administrator 
        sp.verify(sp.sender == self.data.administrator,"only administrator can update the management parameters!")  

        # 3. update the parameter
        sp.if _admin.is_some() :
            self.data.administrator = _admin.open_some(message = "the inputed admin is none")

        sp.if _nftAddress.is_some() :
            self.data.nftContractAddress = _nftAddress.open_some(message = "the inputed _NftAddress is none")



    ##
    ## ## addAuthor
    ##
    ## administrater can add author to the authorMap.
    ## 
    @sp.entry_point     
    def addAuthor(self, _param):
        # 1. Initial the input parameter types
        sp.set_type(_param, sp.TRecord(
                                name =  sp.TString,
                                account =  sp.TString,
                                headPortrait =  sp.TString,
                                email =  sp.TString,
                                phone = sp.TString,
                                description = sp.TString,
                                address = sp.TAddress) )

        # 2.only administrator can add an author 
        sp.verify(sp.sender == self.data.administrator,"only administrator can add an author!")  

        # 3. add a new author
        self.data.authorMap[sp.len(self.data.authorMap)] = _param
        

    ##
    ## ## updateAuthor
    ##
    ## administrater can update author information which is in the authorMap.
    ## 
    @sp.entry_point     
    def  updateAuthor(self, _authorID, _param):
        # 1. Initial the input parameter types
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_param, sp.TRecord(
                                name =  sp.TOption(sp.TString),
                                account =  sp.TOption(sp.TString),
                                headPortrait =  sp.TOption(sp.TString),
                                email =  sp.TOption(sp.TString),
                                phone = sp.TOption(sp.TString),
                                description = sp.TOption(sp.TString),
                                address = sp.TOption(sp.TAddress)  ) 
                    )

        # 2.only administrator can add an author 
        sp.verify(sp.sender == self.data.administrator,"only administrator can update an author!")  

        # 3. check the author does exist!
        sp.verify(self.data.authorMap.contains(_authorID), "the author id does not exist!")

        # 4. update some valid input parameters.
        authorInformation = self.data.authorMap[_authorID] 

        sp.if _param.name.is_some() :
            authorInformation.name = _param.name.open_some(message = "the input name is none")    

        sp.if _param.account.is_some() :
            authorInformation.account = _param.account.open_some(message = "the input account is none")    

        sp.if _param.headPortrait.is_some() :
            authorInformation.headPortrait = _param.headPortrait.open_some(message = "the input headPortrait is none")    

        sp.if _param.email.is_some() :
            authorInformation.email = _param.email.open_some(message = "the input email is none")    

        sp.if _param.phone.is_some() :
            authorInformation.phone = _param.phone.open_some(message = "the input phone is none")    

        sp.if _param.description.is_some() :
            authorInformation.description = _param.description.open_some(message = "the input description is none")    

        sp.if _param.address.is_some() :
            authorInformation.address = _param.address.open_some(message = "the input address is none")    



    ##
    ## ## fa2Transfer
    ##
    ## transfer token 
    ## 
    def fa2Transfer(self, fa2, from_, to_, objkt_id, objkt_amount):
        c = sp.contract(sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), fa2, entry_point='transfer').open_some()
        sp.transfer(sp.list([sp.record(from_=from_, txs=sp.list([sp.record(amount=objkt_amount, to_=to_, token_id=objkt_id)]))]), sp.mutez(0), c)
         

    ##
    ## ## openAuction
    ##
    ## administrater can update author information which is in the authorMap.
    ## 
    @sp.entry_point     
    def openAuction(self, _param):  

        # 1. Initial the input parameter types
        sp.set_type(_param, sp.TRecord(
                                token_id = sp.TNat,
                                authorID =  sp.TNat,
                                sellerAddress =  sp.TAddress,
                                auctionTypeEnglish =  sp.TBool,
                                startTime =  sp.TTimestamp,
                                stopTime = sp.TTimestamp,
                                startPrice = sp.TMutez,
                                minStep = sp.TMutez) )      

        # 2. check the inputted parameters
        ## stopTime should >= startTime
        sp.verify( _param.stopTime >= _param.startTime, "the stop time should greater than or equal to the start time!")
        ## the sender which must be an acccount is the sellerAddress
        sp.verify( sp.sender ==  _param.sellerAddress, "the sender of the transaction must be the seller!")
        ## the authorID should exist!
        sp.verify(self.data.authorMap.contains(_param.authorID), "the author id does not exist!")


        # 3. transfer the token to the auciton contarct. this can check whether the sender has the transfer right.
        self.fa2Transfer(self.data.nftContractAddress, _param.sellerAddress, sp.self_address, _param.token_id, 1)


        # 4.1 if the token is in goodsStoreMap 
        goodsInfo = sp.record(
                            # set the auction information
                            authorID = _param.authorID,
                            sellerAddress = _param.sellerAddress,
                            auctionTypeEnglish = _param.auctionTypeEnglish,
                            startTime = _param.startTime,
                            stopTime =  _param.stopTime,
                            startPrice = _param.startPrice, 
                            minStep = _param.minStep,
                            # initial the dynamic bidding information
                            currentBidder = sp.none,
                            currentPrice = sp.mutez(0),
                            currentRSAPublicKey = '',
                            EncryptedSrcUrl = '',
                            # sp.TBounded(["Initial", "Bidding", "Ended"])
                            status = sp.variant('status', "Initial")
                        )


        # 6. update the goods in goodsStoreMap
        ## 6.1 the token is in goodsStore
        sp.if self.data.goodsStoreMap.contains(_param.token_id) :
            (previousGoodsInfo, newGoodsStoreMap) = sp.get_and_update(self.data.goodsStoreMap, _param.token_id, sp.some(goodsInfo))
            sp.verify( previousGoodsInfo.is_some(), "previousGoodsInfo should not be sp.none!")
            ### only the good in Ended state which can begin a new auction!
            sp.verify( (previousGoodsInfo.open_some().status.open_variant("status") == "Ended"), "the previous goods status must be ended if need to begin a new auction!")

        ## 6.2 the token is not in goodsStore
        sp.else :
            self.data.goodsStoreMap[_param.token_id] = goodsInfo

        
    ##
    ## ## englishBidding
    ##
    ## any one bidding the goods with the english auction style
    ## note: if the buyer send the valid currentRSAPublicKey, the seller will delivery 
    ## the source file with encrypted url.
    ##
    @sp.entry_point     
    def englishBidding(self, _token_id, _currentRsaPublicKey):  
        # set type, 
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(_currentRsaPublicKey, sp.TString)
     
        # 1. check whether the token id is in goodsStore     
        sp.verify(self.data.goodsStoreMap.contains(_token_id), "the token id is not in goodsStore !") 
        goodsInfo = self.data.goodsStoreMap[_token_id]

        # 2. check the sender is not the seller
        sp.verify(sp.sender  != goodsInfo.sellerAddress, "the buyer can not be the seller!")

        # 3. check now is between startingTime and stoppingTime
        sp.verify( (sp.now >= goodsInfo.startTime) & (sp.now <= goodsInfo.stopTime), "the bidding time should be between startTime and stoppTime!")

        # 4. judge the goods state
        ## sp.TBounded(["Initial", "Bidding", "Ended"])
        #currentStatus = goodsInfo.status.open_variant("status", message = "status has no status value!")
        currentStatus = sp.local("currentStatus", goodsInfo.status.open_variant("status", message = "status has no status value!"))
      
        ## check the currentStatus can only be Initial or Bidding state for bidding
        sp.verify( (currentStatus.value ==  "Initial") | (currentStatus.value ==  "Bidding"),
                    "the goods status can only be Initial or Bidding state for bidding")

        # 4.1 Initial
        sp.if (currentStatus.value ==  "Initial") :
            # 4.1.1 check this transaction amout is equal to or bigger than the startingPrice
            sp.verify( (sp.amount >= goodsInfo.startPrice), "this transaction amout is equal to or bigger than the startingPrice")

            ## 4.1.2 check the difference between the  transaction amout and startingPrice is multiple of minStep
            sp.verify( ( (sp.utils.mutez_to_nat(sp.amount) %  sp.utils.mutez_to_nat(goodsInfo.minStep)) == 0),
                       "the difference between the  transaction amout and startingPrice is multiple of minStep")
            
            # 4.1.3 check wether the current bidder address and the current price is zero
            sp.verify( sp.mutez(0) == goodsInfo.currentPrice, "the current price should be 0 when initial" )

            sp.verify( ~goodsInfo.currentBidder.is_some(), 
                        "make sure the current bidder address and the current price are initial")
            
            ## 4.1.4 update the current bidder information,status to "Bidding"
            goodsInfo.currentBidder = sp.some(sp.sender)
            goodsInfo.currentPrice = sp.amount
            goodsInfo.currentRSAPublicKey = _currentRsaPublicKey
            #status = sp.TBounded(["Initial", "Bidding", "Ended"])
            goodsInfo.status = sp.variant('status', "Bidding")

            # update to storage.goodsInfo is not local variant, no need to update once more
            #self.data.goodsStoreMap[_token_id] = goodsInfo


        # 4.2 Bidding
        sp.else :
            # 4.2.1 this transaction amout is bigger than the current price
            sp.verify( (sp.amount > goodsInfo.currentPrice), 
                        "this new buyer should bid a new price which must bigger than the previous one!")

            ## 4.2.2 the difference between the  transaction amout and the current price is multiple of minStep
            sp.verify( ( (sp.utils.mutez_to_nat(sp.amount - goodsInfo.currentPrice) % sp.utils.mutez_to_nat(goodsInfo.minStep)) == 0),
                        "the difference between the  transaction amout and the previous price is multiple of minStep")
            
            # ## 4.2.3 check wether the current bidder address is not the previous bidder?
            sp.verify( (sp.sender != goodsInfo.currentBidder.open_some(message = "this is exception when the previous bidder is none here")), 
                        " the current bidder must not be the previous bidder!")

            # ## 4.2.4 make sure that the balance of the contract must be equal to or bigger than the previous bidding price
            sp.verify( (sp.balance >= goodsInfo.currentPrice), "the balance of the contract must be equal to or bigger than the previous bidding price")
            
            # ## 4.2.5 return  previous amount to the previous bidder
            sp.send(goodsInfo.currentBidder.open_some(), goodsInfo.currentPrice, message = "returning  previous amount to the previous bidder results failed!")

            # ## 4.2.6 update the current bidder infomation,status to "Bidding"
            goodsInfo.currentBidder = sp.some(sp.sender)
            goodsInfo.currentPrice = sp.amount
            goodsInfo.currentRSAPublicKey = _currentRsaPublicKey
            # status == sp.TBounded(["Initial", "Bidding", "Ended"])
            goodsInfo.status =  sp.variant('status', "Bidding")

            # update to storage. goodsInfo is not local variant, no need to update once more
            #self.data.goodsStoreMap[_token_id] = goodsInfo

    ##
    ## ## resetGoodsAuctionInfo
    ##
    ## change the goods status to Ended 
    ## reserved EncryptedSrcUrl for the buyer to get
    ## reset some key parameters.
    ##
    def resetGoodsAuctionInfo(self, _token_id):  
        # set type, 
        sp.set_type(_token_id, sp.TNat)

        # 1. check whether the token is in goodsStore
        sp.verify(self.data.goodsStoreMap.contains(_token_id), "the token id is not in goodsStore !") 
        goodsInfo = self.data.goodsStoreMap[_token_id]   

        goodsInfo.startTime = sp.timestamp(0)
        goodsInfo.stopTime = sp.timestamp(0)
        goodsInfo.startPrice = sp.mutez(0)
        goodsInfo.minStep = sp.mutez(0)
        goodsInfo.currentBidder = sp.none
        ## currentRSAPublicKey,EncryptedSrcUrl reserved for the buyer to check
        goodsInfo.status = sp.variant('status', "Ended")


    ##
    ## ## updateSaleRankingMap
    ##
    ## update sale ranking map when closeAuctionWithDelivery
    ## 
    def updateSaleRankingMap(self, _token_id, volume, seller, buyer):
        # set type, 
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(volume, sp.TMutez)
        sp.set_type(seller, sp.TAddress)
        sp.set_type(buyer, sp.TAddress)   


        #record sale information
        ## if rankingMap of the token id exists
        sp.if self.data.rankingMaps.contains(_token_id) :
            self.data.rankingMaps[_token_id].volume += volume

            ## set the seller count 
            sp.if self.data.rankingMaps[_token_id].sellers.contains(seller) :
                self.data.rankingMaps[_token_id].sellers[seller] += 1
            sp.else :
                self.data.rankingMaps[_token_id].sellers[seller] = 1


            ## set the buyer count
            sp.if self.data.rankingMaps[_token_id].buyers.contains(buyer) :
                self.data.rankingMaps[_token_id].buyers[buyer] += 1
            sp.else :
                self.data.rankingMaps[_token_id].buyers[buyer] = 1            


        ## if rankingMap of the token id does not exist
        sp.else :
            # construct the record
            rankingMap = sp.record(
                            # set the auction information
                            volume = volume,
                            sellers = sp.map(l = {seller : 1}, tkey = sp.TAddress, tvalue = sp.TNat),
                            buyers = sp.map(l = {buyer : 1}, tkey = sp.TAddress, tvalue = sp.TNat),
            ) 
            ## set the map
            self.data.rankingMaps[_token_id] = rankingMap


    ## ## closeAuctionWithDelivery
    ##
    ## After the stop time, the seller delivery the token and the source file to the latest bidder, and get the xtz
    ## If no bidder,just close the auciton.
    ## 
    ##
    @sp.entry_point   
    def closeAuctionWithDelivery(self, _token_id, _EncryptedSrcUrl):  
        # set type, 
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(_EncryptedSrcUrl, sp.TString)

        # 1. check whether the token is in goodsStore
        sp.verify(self.data.goodsStoreMap.contains(_token_id), "the token id is not in goodsStore !") 
        goodsInfo = self.data.goodsStoreMap[_token_id]        

        # 2. check the sender is the seller
        sp.verify(sp.sender  == goodsInfo.sellerAddress, "the sender must be the seller!")        

        # 3. check now is bigger than the stop time
        sp.verify( (sp.now > goodsInfo.stopTime), "the seller can only end the auction after the stop time!")

        # 4. check whether there is any bidder
        ## 4.2 has bidder
        sp.if (goodsInfo.currentBidder.is_some()):
            ## 4.2.1 transfer the NFT token to the last bidder
            self.fa2Transfer(self.data.nftContractAddress, sp.self_address, goodsInfo.currentBidder.open_some(),  _token_id, 1)

            ## 4.2.2 transfer the tezos to the seller
            ## verify the balance of the contract is equal to or bigger than the bidding price
            sp.verify( (sp.balance >= goodsInfo.currentPrice), "the balance of the contract must be equal to or bigger than the previous bidding price")
            ## send
            sp.send(goodsInfo.sellerAddress, goodsInfo.currentPrice, message = "It's failed to send the bidding XTZ to the seller!")


            ## 4.2.3 set EncryptedSrcUrl
            goodsInfo.EncryptedSrcUrl = _EncryptedSrcUrl

            ## 4.2.4 update sale ranking map
            self.updateSaleRankingMap(_token_id, goodsInfo.currentPrice, goodsInfo.sellerAddress, goodsInfo.currentBidder.open_some())

            ## 4.2.5 should not delete the goods,because the buyer will get the EncryptedSrcUrl later.
            self.resetGoodsAuctionInfo(_token_id)




        ## 4.1 no bidder
        sp.else :
            ## 4.2.1 withdraw the NFT token
            self.fa2Transfer(self.data.nftContractAddress, sp.self_address, goodsInfo.sellerAddress,  _token_id, 1)
            
            ## 4.2.2 delete the goods
            del self.data.goodsStoreMap[_token_id]

    ## ## cancelAuction
    ##
    ## cancel auction in some exception condition by the admin only.
    ## the seller can close the auction after the stop time with closeAuctionWithDelivery function
    ## 
    ##
    @sp.entry_point   
    def cancelAuction(self, _token_id):  
        # set type, 
        sp.set_type(_token_id, sp.TNat)

        # 1. check whether the token id is in goodsStore     
        sp.verify(self.data.goodsStoreMap.contains(_token_id), "the token id is not in goodsStore !") 
        goodsInfo = self.data.goodsStoreMap[_token_id]

        # 2. check the sender is the administrator.
        sp.verify(sp.sender  == self.data.administrator, "the sender must be the administrator!")        

        #3. check the goods status is not Ended, because this seems the auction is ended.
        currentStatus = goodsInfo.status.open_variant("status", message = "status has no status value!")
        #currentStatus = sp.local("currentStatus", goodsInfo.status.open_variant("status", message = "status has no status value!"))
      
        #status = sp.TBounded(["Initial", "Bidding", "Ended"])
        sp.verify(  currentStatus != "Ended","the goods status is not Ended, because this seems the auction is ended.")
              

        # 4.if there has a bidding, the status must be "Bidding"
        sp.if (currentStatus == "Bidding") & (goodsInfo.currentBidder.is_some()) :
            ## 4.1 verify the balance of contract is enough for return
            sp.verify( (sp.balance >= goodsInfo.currentPrice), "the balance of the contract must be equal to or bigger than the previous bidding price")
            ### 4.2 return  previous amount to the previous bidder
            sp.send(goodsInfo.currentBidder.open_some(), goodsInfo.currentPrice, message = "returning  previous amount to the previous bidder failed!")


        # 5.return the NFT token to the seller
        self.fa2Transfer(self.data.nftContractAddress, sp.self_address, goodsInfo.sellerAddress,  _token_id, 1)

        # 6. delete the goods
        del self.data.goodsStoreMap[_token_id]  


    ##
    ## ## string_of_nat
    ##
    ## change nat to string
    ## 
    def string_of_nat(self, params):
        c   = sp.map({x : str(x) for x in range(0, 10)})
        x   = sp.local('x', params)
        res = sp.local('res', [])
        sp.if x.value == 0:
            res.value.push('0')
        sp.while 0 < x.value:
            res.value.push(c[x.value % 10])
            x.value //= 10
        return sp.concat(res.value)
    

    ##
    ## ## sponsorDonation
    ##
    ## any one can sponsor a donation when the author is registered in the market.
    ## 
    @sp.entry_point     
    def sponsorDonation(self, _token_id,_authorID, _endTime):
        # 1. Initial the input parameters.
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_endTime, sp.TTimestamp)

        # 2. judge the _authorID is in the authorMap
        sp.verify(self.data.authorMap.contains(_authorID), "the author id does not exist!")
        # judge _endTime is bigger than now
        sp.verify(_endTime > sp.now, "the end time should be bigger than now!")
        # _token_id 

        # 4. save parameters.
        ## construct donation record map
        donationRecordMap = sp.record(
                    authorID = _authorID,
                    tokenID = _token_id,
                    sponsorAddr = sp.sender,
                    endTime = _endTime, 
                    donationValue = sp.mutez(0),      
                    withdrawableValue = sp.mutez(0),
                    donatorMap = sp.map()     
        )

        # sp.len(self.data.donationRecordsMap) is the record no. of the filling record
        self.data.donationRecordsMap[sp.len(self.data.donationRecordsMap)] = donationRecordMap


    ##
    ## ## donate
    ##
    ## any one can donate tezos to the sponsor who can be the author or others.
    ## 
    @sp.entry_point     
    def donate(self, _recordNO, _authorID, _token_id):
        # 1. Initial the input parameters.
        sp.set_type(_recordNO, sp.TNat)
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_token_id, sp.TNat)

        # 2. judge _recordNO is exist
        sp.verify(self.data.donationRecordsMap.contains(_recordNO), "the donation _recordNO does not exist!")

        # 3. judge _authorID,_token_id are same as the sponsor filled.
        sp.verify(self.data.donationRecordsMap[_recordNO].authorID == _authorID,  "the _authorID is wrong, please make sure and try again!")
        sp.verify(self.data.donationRecordsMap[_recordNO].tokenID == _token_id,  "the _token_id is wrong, please make sure and try again!")

        # 4. judge now is smaller than or equal to the endtime.
        sp.verify(sp.now <= self.data.donationRecordsMap[_recordNO].endTime, "now should be smaller than or equal to the end time!")

        # 5. judge the donation value with this transation is bigger than 0.
        sp.verify(sp.amount > sp.mutez(0), "the donation value should be bigger than 0!")

        # 6. record the donator address, amount, produce the certification ID
        donatorRecord = sp.record(
                    donatorAddr = sp.sender,
                    donatorValue = sp.amount,
                    donatorTime = sp.now,
                    # donationID：TEZOS-recordNO-authorID-tokenID-donatorAddr-donatorValue-donatorTime     
                    # donationID = "TEZOS-"+self.string_of_nat(_recordNO)+"-"+self.string_of_nat(_authorID)+"-" \
                    #              +self.string_of_nat(_token_id)+"-"+self.string_of_nat(sp.sender)+"-"+self.string_of_nat(sp.amount) \
                    #              +"-"+self.string_of_nat(sp.level) 
                    donationID = ""
                    )

        self.data.donationRecordsMap[_recordNO].donatorMap[sp.len(self.data.donationRecordsMap[_recordNO].donatorMap)] \
            = donatorRecord

        # 7. update the works' donationValue 
        self.data.donationRecordsMap[_recordNO].donationValue += sp.amount
        self.data.donationRecordsMap[_recordNO].withdrawableValue += sp.amount




    ##
    ## ## withdrawDonation
    ##
    ## the sponsor can withdraw the donation.
    ## 
    @sp.entry_point     
    def withdrawDonation(self, _recordNO, _authorID, _token_id):
        # 1. Initial the input parameters.
        sp.set_type(_recordNO, sp.TNat)
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_token_id, sp.TNat)

        # 2. judge _recordNO is exist
        sp.verify(self.data.donationRecordsMap.contains(_recordNO), "the donation _recordNO does not exist!")

        # 3. judge _authorID,_token_id are same as the sponsor filled.
        sp.verify(self.data.donationRecordsMap[_recordNO].authorID == _authorID,  "the _authorID is wrong, please make sure and try again!")
        sp.verify(self.data.donationRecordsMap[_recordNO].tokenID == _token_id,  "the _token_id is wrong, please make sure and try again!")
       
        # 4. judge now is smaller than or equal to the endtime.
        sp.verify(sp.now > self.data.donationRecordsMap[_recordNO].endTime, "now should be bigger than the end time when withdraw!")

        # 5. judge the sender is the sponor
        sp.verify(sp.sender == self.data.donationRecordsMap[_recordNO].sponsorAddr, "the sender must be the sponor!")
        
        # 6. judge the donation value with this transation is bigger than 0.
        sp.verify(self.data.donationRecordsMap[_recordNO].withdrawableValue > sp.mutez(0), "the donation value should be bigger than 0 when withdraw!")

        # 7. judge the balance of the contract must be bigger than or equal to the withdrawableValue.
        sp.verify(sp.balance >= self.data.donationRecordsMap[_recordNO].withdrawableValue, 
                    "the balance of the contract must be bigger than or equal to the withdrawableValue!")

        # 8. transfer tezos to the sponsor
        sp.send(sp.sender, self.data.donationRecordsMap[_recordNO].withdrawableValue)          

        # 9. set withdrawableValue to 0.        
        self.data.donationRecordsMap[_recordNO].withdrawableValue = sp.mutez(0)            


    ##
    ## ## sponsorVoting
    ##
    ## any one can sponsor a voting in the future between [_beginTime:_endTime].
    ## 
    @sp.entry_point     
    def sponsorVoting(self, _token_id,_authorID, _beginTime, _endTime):
        # 1. Initial the input parameters.
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_beginTime, sp.TTimestamp)        
        sp.set_type(_endTime, sp.TTimestamp)

        # 2. judge the _authorID is in the authorMap
        sp.verify(self.data.authorMap.contains(_authorID), "the author id does not exist!")

        # 3.judge _beginTime < _endTime        
        sp.verify(_beginTime < _endTime, "the voting can only be sponsored in the future between [_beginTime:_endTime]!")        
        # judge _beginTime is <= now 
        sp.verify(_beginTime <= sp.now, "the voting can only be valid from now on!")        

        # 4. record this voting parameters.
        recordNO = sp.len(self.data.voteRecordsMap)
        ## construct vote record map of the token
        voteRecordsMap = sp.record(
                        authorID = _authorID,
                        tokenID = _token_id,
                        beginTime = _beginTime,
                        endTime = _endTime,
                        totalNum  = 0,
                        votersMap =  sp.map() 
        )

        #set the map
        self.data.voteRecordsMap[recordNO] = voteRecordsMap

    ##
    ## ## vote
    ##
    ## any one can sponsor a voting in the future between [_beginTime:_endTime].
    ## 
    @sp.entry_point     
    def vote(self, _recordNO, _authorID, _token_id):
        # 1. Initial the input parameters.
        sp.set_type(_recordNO, sp.TNat)
        sp.set_type(_authorID, sp.TNat)
        sp.set_type(_token_id, sp.TNat)

        # 2. judge _recordNO is exist
        sp.verify(self.data.voteRecordsMap.contains(_recordNO), "the donation _recordNO does not exist!")

        # 3. judge _authorID,_token_id are same as the sponsor filled.
        sp.verify(self.data.voteRecordsMap[_recordNO].authorID == _authorID,  "the _authorID is wrong, please make sure and try again!")
        sp.verify(self.data.voteRecordsMap[_recordNO].tokenID == _token_id,  "the _token_id is wrong, please make sure and try again!")

        # 4. judge now is between [_beginTime:_endTime].
        sp.verify(sp.now >= self.data.voteRecordsMap[_recordNO].beginTime, "now should be bigger than or equal to the begin time!")
        sp.verify(sp.now <= self.data.voteRecordsMap[_recordNO].endTime, "now should be smaller than or equal to the end time!")

        # 5. update totalNum and the voter information
        self.data.voteRecordsMap[_recordNO].totalNum += 1

        # 6. judge the voter map is empty or not
        sp.if self.data.voteRecordsMap[_recordNO].votersMap.contains(sp.sender) :
            self.data.voteRecordsMap[_recordNO].votersMap[sp.sender] += 1
        sp.else :
            self.data.voteRecordsMap[_recordNO].votersMap[sp.sender] = 1


    ##
    ## ## updateIPAssetsCert
    ##
    ## administrater can update DCI certification to NFT 
    ## 
    @sp.entry_point     
    def updateIPAssetsCert(self, _token_id, _params):
        # 1. Initial the input parameter types
        sp.set_type(_token_id, sp.TNat)
        sp.set_type(_params, sp.TRecord(
                        DCI =   sp.TString,
                        registerID = sp.TString,
                        worksName = sp.TString,
                        worksType = sp.TString,
                        authorName = sp.TString,
                        finishedDate = sp.TString,
                        firstPublishedDate = sp.TString,
                        registeredDate = sp.TString) )

        # 2.only administrator can update DCI certification to NFT
        sp.verify(sp.sender == self.data.administrator,"update DCI certification to NFT !")  

        # 3. update
        self.data.ipAssetsCert[_token_id] = _params

## ## 
##
## ### Viewer Contract
##
## To get sp.result of view sp.utils.view(...)
## 
class Viewer(sp.Contract):
    def __init__(self, t):
        self.init(last = sp.none)
        self.init_type(sp.TRecord(last = sp.TOption(t)))

    @sp.entry_point
    def target(self, params):
        self.data.last = sp.some(params)

      
 
## ## Tests
##
## ### Auxiliary Consumer Contract
##
## This contract is used by the tests to be on the receiver side of
## callback-based entry-points.
## It stores facts about the results in order to use `scenario.verify(...)`
## (cf.
##  [documentation](https://www.smartpy.io/dev/reference.html#_in_a_test_scenario_)).
class View_consumer(sp.Contract):
    def __init__(self, contract):
        self.contract = contract
        self.init(last_sum = 0,
                  operator_support =  not contract.config.support_operator)

    @sp.entry_point
    def reinit(self):
        self.data.last_sum = 0
        # It's also nice to make this contract have more than one entry point.

    @sp.entry_point
    def receive_balances(self, params):
        sp.set_type(params, Balance_of.response_type())
        self.data.last_sum = 0
        sp.for resp in params:
            self.data.last_sum += resp.balance

## ### Generation of Test Scenarios
##
## Tests are also parametrized by the `FA2_config` object.
## The best way to visualize them is to use the online IDE
## (<https://www.smartpy.io/dev/>).
def add_test(config, is_default = True):
    @sp.add_test(name = config.name, is_default = is_default)
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Begin FA2 Contract: " + config.name)
        scenario.table_of_contents()
        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("administrator")
        alice = sp.test_account("alice")
        bob   = sp.test_account("bob")        
        duncan = sp.test_account("duncan")    


        # Let's display the accounts:
        scenario.h2("Accounts")
        scenario.show([admin, alice, bob, duncan])

        fake_ft_token = sp.test_account("ft_token")
        fake_nft_token = sp.test_account("nft_token")
        fake_exchange_addr = sp.test_account("exchange")
  


        if config.non_fungible:
            # TODO
            scenario.h2("Initial MOZ.FT annd minting to alice")

            # default is  FT config
            ftConfig = FA2_config()

            ftContract = FA2(ftConfig,
                    metadata = sp.utils.metadata_of_url("ipfs://Qmf6tjsd7kwHESMJhCLYNHF7j6AdGNmtnBrcVC4aS87YwL"),
                    admin = admin.address)
            scenario += ftContract        

            # 1. mint 100 MOZ FT to alice and duncan
            scenario.p("The administrator mints 200 MOZ to Alice, then transfer 100 to duncan")
            mozFTMeta = FA2.make_metadata(
                name = "The MOZIK Fungible Token Zero",
                decimals = 0,
                symbol= "MOZ" )
            ftContract.mint(address = alice.address,
                        amount = 200,
                        metadata = mozFTMeta,
                        token_id = 0).run(sender = admin)

            ftContract.transfer([ftContract.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = duncan.address,
                                                  amount = 100,
                                                  token_id = 0)])
            ]).run(sender = alice)      



            # 2. mint 200 MOS FT to bob and transfer 100 to duncan
            scenario.p("The administrator mints 200 MOS to bob and  transfer 100 to duncan.")
            mosFTMeta = FA2.make_metadata(
                name = "The MOZIK Fungible Token 1",
                decimals = 0,
                symbol= "MOS" )
            ftContract.mint(address = bob.address,
                        amount = 200,
                        metadata = mosFTMeta,
                        token_id = 1).run(sender = admin)      

            ftContract.transfer([ftContract.batch_transfer.item(from_ = bob.address,
                                    txs = [
                                        sp.record(to_ = duncan.address,
                                                  amount = 100,
                                                  token_id = 1)])
            ]).run(sender = bob)          

            scenario.h2("Begin callback of  FA2 balance.")
            scenario.h3("Consumer Contract for Callback Calls.")
            consumer = View_consumer(ftContract)
            scenario += consumer
            scenario.p("Consumer virtual address: "
                    + consumer.address.export())

            def arguments_for_balance_of(receiver, reqs):
                return (sp.record(
                    callback = sp.contract(
                        Balance_of.response_type(),
                        receiver.address,
                        entry_point = "receive_balances").open_some(),
                    requests = reqs))
            ftContract.balance_of(arguments_for_balance_of(consumer, [
                        sp.record(owner = alice.address, token_id = 0),
                        sp.record(owner = duncan.address, token_id = 0),
                        sp.record(owner = bob.address, token_id = 1),
                        sp.record(owner = duncan.address, token_id = 1)
            ]))
            scenario.verify(consumer.data.last_sum == 400)  

            scenario.h3("Consumer Contract for Callback Calls on explorer")
            #ftContract = sp.contract(sp.TList(sp.TRecord(from_=sp.TAddress, txs=sp.TList(sp.TRecord(amount=sp.TNat, to_=sp.TAddress, token_id=sp.TNat).layout(("to_", ("token_id", "amount")))))), fa2, entry_point='transfer').open_some()



            scenario.h2("Initial MOZ.NFT and minting to bob")
            # 2. mint NFT bob
            nftContract = FA2(config = config,
                    metadata = sp.utils.metadata_of_url("ipfs://Qmf6tjsd7kwHESMJhCLYNHF7j6AdGNmtnBrcVC4aS87YwL"),
                    admin = admin.address)
            scenario += nftContract        

            scenario.h3("The administrator mints 0/1/2/3 MOZ@NFT TOKEN  to bob.")
            mozNFTMeta = FA2.make_metadata(
                name = "The MOZIK Non-Fungible Token 1",
                decimals = 0,
                symbol= "MOZ@NFT" )
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 0).run(sender = admin)
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 1).run(sender = admin)     
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 2).run(sender = admin)    
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 3).run(sender = admin)  

            # transfer token id 3 from bob to duncan
            scenario.h3("transfer token 3 from bob to duncan")
            transferParam = sp.list([ sp.record(from_ =  bob.address, 
                                      txs = sp.list([sp.record(to_ = duncan.address, token_id = 3, amount = 1) ])  
                                               )   
                                    ])                                         
            nftContract.transfer( transferParam ).run(sender = bob)

            # approve Right
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 4).run(sender = admin) 
            nftContract.mint(address = bob.address,
                                amount = 1,
                                metadata = mozNFTMeta,
                                token_id = 5).run(sender = admin)
                                
            scenario.h3("approve token id 4 Recording Right to  alice with other user")
            nftContract.transferRecordingRight(token_id = 4 , address = alice.address).run(sender = alice, valid = False)

            scenario.h3("approve token id 4 Recording Right to  alice")
            nftContract.transferRecordingRight(token_id = 4 , address = alice.address).run(sender = bob)


            scenario.h3("approve token id 4 Propagating Right to  duncan")
            nftContract.transferPropagatingRight(token_id = 4 , address = duncan.address).run(sender = admin)
            
            scenario.h3("approve token id 4 Other Right to  duncan")
            nftContract.transferOtherRightsRight(token_id = 4 , address = duncan.address).run(sender = bob)

            scenario.h3("approve token id 5 All Right to  alice")
            nftContract.transferAllRight(token_id = 5 , recordingRightAddress = alice.address, propagatingRightAddress = alice.address, otherRightsAddress = alice.address).run(sender = bob)

            scenario.h3("transfer token 5 from bob to duncan without all right")
            transferParam = sp.list([ sp.record(from_ =  bob.address, 
                                      txs = sp.list([sp.record(to_ = duncan.address, token_id = 5, amount = 1) ])  
                                               )   
                                    ])                                         
            nftContract.transfer( transferParam ).run(sender = bob, valid = False)

            scenario.h3("approve token id 5 All Right to  bob")
            nftContract.transferAllRight(token_id = 5 , recordingRightAddress = bob.address, propagatingRightAddress = bob.address, otherRightsAddress = bob.address).run(sender = bob)
            
            scenario.h3("transfer token 5 from bob to duncan with all rights")
            transferParam = sp.list([ sp.record(from_ =  bob.address, 
                                      txs = sp.list([sp.record(to_ = duncan.address, token_id = 5, amount = 1) ])  
                                               )   
                                    ])                                         
            nftContract.transfer( transferParam ).run(sender = bob)


            scenario.h2("Change token metadata")    
            mozTestMeta = FA2.make_metadata(
                name = "test The MOZIK Non-Fungible Token ",
                decimals = 1,
                symbol= "test MOZ@NFT" )

            # expected valid
            nftContract.set_token_metadata( token_id = 0,
                                metadata = mozTestMeta).run(sender = admin)  

            # expect invalid because of the sender is not the admin
            nftContract.set_token_metadata( token_id = 1,
                    metadata = mozTestMeta).run(sender = alice, valid = False)                                
            # expect invalid because of token_id not exist
            nftContract.set_token_metadata( token_id = 100,
                    metadata = mozTestMeta).run(sender = admin, valid = False)   

   

            # begin Author Management with NftAuctionMarket contract
            scenario.h1("Begin Author Management")   
            nftAuctionContract = NftAuctionMarket(admin.address, nftContract.address)
            scenario += nftAuctionContract    

            # add author
            scenario.h2("add author")
            param = sp.record(  name =  'Joseph Wooten',
                                account =  'xin22xin23@gmail.com',
                                headPortrait =  "https://gateway.pinata.cloud/ipfs/QmSMGrLZr6sTnt6EqpT4TAp165GEF5KjdtwRRwLCDkEcLR",
                                email =  "Wooten@gmail.com",
                                phone = "+8618621519286",
                                description = "Joseph Wootenis an American keyboardist, singer, songwriter, author and philanthropist. Since 1993 he has been a member of the Steve Miller Band.",
                                address = sp.address("tz1dfmLJ1RRodNx9NSQy6YzgW2nJMiA3R5eq") 
                            )
            ## addAuthor success
            nftAuctionContract.addAuthor(param).run(sender = admin)

            ## addAuthor fail
            nftAuctionContract.addAuthor(param).run(sender = alice, valid = False)

            ## update the author information
            scenario.h2("update author information")            
            authorID = 0
            param = sp.record(  name =  sp.none,
                                account =  sp.none,
                                headPortrait =  sp.none,
                                email =  sp.some("test@gmail.com"),
                                phone =sp.none,
                                description = sp.none,
                                address = sp.none )
            
            ### update success
            nftAuctionContract.updateAuthor(_authorID = authorID, _param = param).run(sender = admin)

            ### update failed
            nftAuctionContract.updateAuthor(_authorID = authorID, _param = param).run(sender = alice, valid = False)


            ### update failed
            authorID = 100
            nftAuctionContract.updateAuthor(_authorID = authorID, _param = param).run(sender = admin, valid = False)
            
            # begin IP assets Register
            scenario.h1("Begin IP assets Register")   

            # update IP Assets certification succ
            scenario.h2("Begin IP assets Register 0/1/2/3, SUCC")   
            params = sp.record(DCI  = "C20190000000000000085961800106805",
                              registerID = "国作登字-2019-I-A0106805",
                              worksName = "Concert and VIP Experience & Pre-release song: Everything’s Gon Be Alright",
                              worksType = "类似摄制电影的方法创作作品",
                              authorName = "Joseph Wooten",
                              finishedDate = "2019-4-16",
                              firstPublishedDate = "2019-4-17",
                              registeredDate = "2019-4-18")
            nftAuctionContract.updateIPAssetsCert(_token_id = 0, _params=params).run(sender = admin, valid = True)
            nftAuctionContract.updateIPAssetsCert(_token_id = 1, _params=params).run(sender = admin, valid = True)
            nftAuctionContract.updateIPAssetsCert(_token_id = 2, _params=params).run(sender = admin, valid = True)
            nftAuctionContract.updateIPAssetsCert(_token_id = 3, _params=params).run(sender = admin, valid = True)
            # update IP Assets certification FAIL
            scenario.h2("Begin IP assets Register, FAIL")  
            nftAuctionContract.updateIPAssetsCert(_token_id = 0, _params=params).run(sender = alice, valid = False)

            # Vote for token 1
            scenario.h1("Begin Vote for token")   

            # sponsor voting for token 1 which owned by bob"
            scenario.h2("Begin sponsor voting for token 1 which owned by bob")   
            nftAuctionContract.sponsorVoting(_token_id = 1, _authorID = 0, _beginTime = sp.now, _endTime = sp.now.add_seconds(60)).run(sender = admin)
            # alice votes for token 1 twice which owned by bob"
            scenario.h2("Alice votes twice for token 1 ")   
            nftAuctionContract.vote(_recordNO = 0, _authorID = 0, _token_id = 1).run(sender = alice)
            nftAuctionContract.vote(_recordNO = 0, _authorID = 0, _token_id = 1).run(sender = alice)
            scenario.h2("admin votes once  for token 1 ")               
            nftAuctionContract.vote(_recordNO = 0, _authorID = 0, _token_id = 1).run(sender = duncan)
            scenario.verify(nftAuctionContract.data.voteRecordsMap[0].totalNum == 3)
            scenario.verify(nftAuctionContract.data.voteRecordsMap[0].votersMap[alice.address] == 2)
            
            # Vote for token 1
            scenario.h1("Begin Donation for token")   
            scenario.h2("Bob sponsor a donation for token 0")   
            nftAuctionContract.sponsorDonation( _token_id = 0,_authorID = 0, _endTime = sp.now.add_seconds(60)).run(sender = bob)
            scenario.h2("Bob donates 1 xtz for token 0")   
            nftAuctionContract.donate(_recordNO = 0, _authorID = 0, _token_id = 0).run(sender = duncan,amount = sp.mutez(1000000))
            scenario.h2("alice donates 1 xtz for token 0")   
            nftAuctionContract.donate(_recordNO = 0, _authorID = 0, _token_id = 0).run(sender = alice,amount = sp.mutez(1000000))
            scenario.h2("duncan donates 1 xtz for token 0")   
            nftAuctionContract.donate(_recordNO = 0, _authorID = 0, _token_id = 0).run(sender = duncan,amount = sp.mutez(1000000))
            scenario.h2("alice donates 1 xtz for token 0 once more")   
            nftAuctionContract.donate(_recordNO = 0, _authorID = 0, _token_id = 0).run(sender = alice,amount = sp.mutez(1000000))     
            scenario.verify(nftAuctionContract.data.donationRecordsMap[0].withdrawableValue == sp.mutez(4000000))       

            scenario.h2("bob withdraw the docation for token 0")   
            nftAuctionContract.withdrawDonation(_recordNO = 0, _authorID = 0, _token_id = 0).run(sender = bob,now = sp.now.add_seconds(120))



            # begin auction Management with NftAuctionMarket contract
            scenario.h1("Begin auction Management")   
            #  begin openAuction 
            scenario.h2("Begin openAuction token 0")  

            ## approve bob token 0 to nftAuctionContract
            nftContract.update_operators([
                sp.variant("add_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 0))
            ]).run(sender = bob)                

            ##  bob openAuction token 0 success, which is Joseph Wooten's works
            param = sp.record(token_id = 0, authorID = 0, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(100), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = bob, now = sp.timestamp(1630723485) )           

            ## alice does not has the token_id 0,ERROR
            param = sp.record(token_id = 0, authorID = 0, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(100), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = alice, now = sp.timestamp(1630723485), valid = False )           

            ## the authorID dosen't exist ,ERROR
            param = sp.record(token_id = 0, authorID = 100, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(100), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = bob, now = sp.timestamp(1630723485), valid = False )           
            ## the goods is exist but the status is not "Ended",ERROR
            param = sp.record(token_id = 0, authorID = 0, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(100), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = bob, now = sp.timestamp(1630723485), valid = False )           

            #  begin englishBidding 
            scenario.h3("duncan bids for the first time,SUCC")  
            ## duncan bids for the first time ,SUCC
            publicKey = "-----BEGIN PUBLIC KEY-----\
                        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC0zqoU5B2EGOhVoZNxOm2Fnyxu\
                        Lbtz8xJ0jMQpjLRCWuc7mMOup1n+c1L3juCmKM7ZdiZr1eOiAqyrZkWlIvtxdxhW\
                        pcJiRki4W6L73HF98dBUFnHmgGY3n+e/vO3nwWXqgyZ4b0f1+h8+o4eCd1mBdB8q\
                        q0ZYKFo8hM1fH+h/MwIDAQAB\
                        -----END PUBLIC KEY-----"
            nftAuctionContract.englishBidding(_token_id = 0, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(100), now = sp.timestamp(1630723495))
            scenario.verify(nftAuctionContract.balance == sp.mutez(100))

            ## alice bids for the second time,SUCC
            scenario.h3("alice bids for the second time,SUCC")  
            nftAuctionContract.englishBidding(_token_id = 0, _currentRsaPublicKey = publicKey).run(
                                sender = alice, amount = sp.mutez(200), now = sp.timestamp(1630723505))
            scenario.verify(nftAuctionContract.balance == sp.mutez(200))

            ## alice bids for the third time,FAIL
            scenario.h3("alice bids for the third time, FAIL")     
            nftAuctionContract.englishBidding(_token_id = 0, _currentRsaPublicKey = publicKey).run(
                                sender = alice, amount = sp.mutez(300), now = sp.timestamp(1630723510), valid = False)
                        
            ## duncan bids for the fourth time,FAIL
            scenario.h3("duncan bids for the fourth time, FAIL") 
            ## less amount  
            nftAuctionContract.englishBidding(_token_id = 0, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(200), now = sp.timestamp(1630723515), valid = False)
            ## wrong token
            nftAuctionContract.englishBidding(_token_id = 100, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(250), now = sp.timestamp(1630723515), valid = False)
                       
            ## duncan bids for the fifth time, SUCC
            scenario.h3("duncan bids for the fifth time, SUCC") 
            nftAuctionContract.englishBidding(_token_id = 0, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(350), now = sp.timestamp(1630723515))
            
            scenario.verify(nftAuctionContract.balance == sp.mutez(350))

            ##  close auction and delivery the token if has a bidder.
            scenario.h3("close auction and delivery the token if has a bidder. SUCC")  
            EncryptedSrcUrl = "GlE99f4jFUmopXswWrcd4w/xXz9rSpNxqD0c3FMfDPl80QcKkE14cpd9q9YgRdj52I72Xd2oIPVPNa2F/47wrxlSEvzQ\
                                PvHruWIeKujJEENImra3aaAfjH92LzV9FF96u+M+vyfo1KJyO+cfm+OGrDGaaxWDqG7FirV2/DLQrko="
            nftAuctionContract.closeAuctionWithDelivery(_token_id = 0, _EncryptedSrcUrl = EncryptedSrcUrl).run(sender = bob, now = sp.timestamp(1630723915))

            ## check the balance
            scenario.verify(nftContract.data.ledger[nftContract.ledger_key.make(duncan.address, 0)].balance == 1 )
            scenario.verify(nftAuctionContract.balance == sp.mutez(0))


            #  begin openAuction 
            scenario.h2("Begin openAuction token 1")  

            ## approve bob token 1 to nftAuctionContract
            nftContract.update_operators([
                sp.variant("add_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 1))
            ]).run(sender = bob)                

            ##  bob openAuction token 1 success, which is Joseph Wooten's works
            param = sp.record(token_id = 1, authorID = 0, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(1000), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = bob, now = sp.timestamp(1630723485) )           

            ##  close auction while there is no bidder.
            scenario.h3("close auction while there is no bidder.SUCC")  
            EncryptedSrcUrl = ""
            nftAuctionContract.closeAuctionWithDelivery(_token_id = 1, _EncryptedSrcUrl = EncryptedSrcUrl).run(sender = bob, now = sp.timestamp(1630723915))
            ## check the balance
            scenario.verify(nftContract.data.ledger[nftContract.ledger_key.make(bob.address, 1)].balance == 1 )
            scenario.verify(nftAuctionContract.balance == sp.mutez(0))

            #  begin openAuction 
            scenario.h2("Begin openAuction token 2")  
            ## approve bob token 2 to nftAuctionContract
            nftContract.update_operators([
                sp.variant("add_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 2))
            ]).run(sender = bob)                

            ##  bob openAuction token 2 success, which is Joseph Wooten's works
            param = sp.record(token_id = 2, authorID = 0, sellerAddress =  bob.address, auctionTypeEnglish = True, \
                              startTime = sp.timestamp(1630723485), stopTime = sp.timestamp(1630723485).add_seconds(60), \
                              startPrice = sp.mutez(1000000), minStep = sp.mutez(10))

            nftAuctionContract.openAuction(param).run(sender = bob, now = sp.timestamp(1630723485) )           

            #  the seller want to cancel auction,but FAIL
            scenario.h3("the seller want to cancel auction,but FAIL")  
            nftAuctionContract.cancelAuction(2).run(sender = bob, valid = False )

            ## duncan bids with little XTZ, FAIL
            scenario.h3("duncan bids with mutez(350) , FAIL") 
            nftAuctionContract.englishBidding(_token_id = 2, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(350), now = sp.timestamp(1630723515), valid = False )

            # ## duncan bids with enough XTZ, SUCC
            scenario.h3("duncan bids with mutez(1000000) , FAIL") 
            nftAuctionContract.englishBidding(_token_id = 2, _currentRsaPublicKey = publicKey).run(
                                sender = duncan, amount = sp.mutez(1000000), now = sp.timestamp(1630723515))

            # ## admin cancel the auction token 2,SUCC
            scenario.h3("admin cancel the auction,SUCC")  
            nftAuctionContract.cancelAuction(2).run(sender = admin)
            ## check the balance
            scenario.verify(nftContract.data.ledger[nftContract.ledger_key.make(bob.address, 2)].balance == 1 )
            scenario.verify(nftAuctionContract.balance == sp.mutez(0))            

            # ## admin cancel the auction token 0,FAIL
            scenario.h3("admin cancel the auction in Ended state,FAIL")  
            nftAuctionContract.cancelAuction(0).run(sender = admin, valid = False)


            ## remove apporval of bob token 0 to nftAuctionContract because bob has no token 0
            nftContract.update_operators([
                sp.variant("remove_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 0))
            ]).run(sender = bob)

            nftContract.update_operators([
                sp.variant("remove_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 1))
            ]).run(sender = bob)            

            nftContract.update_operators([
                sp.variant("remove_operator", nftContract.operator_param.make(
                    owner = bob.address,
                    operator = nftAuctionContract.address,
                    token_id = 2))
            ]).run(sender = bob)   

            

            return




        # another case: FT test
        scenario.h2("Initial Minting")
        scenario.p("The administrator mints 100 token-0's to Alice.")
        tok0_md = FA2.make_metadata(
            name = "The Token Zero",
            decimals = 2,
            symbol= "TK0" )
        c1.mint(address = alice.address,
                            amount = 100,
                            metadata = tok0_md,
                            token_id = 0).run(sender = admin)
        scenario.h2("Transfers Alice -> Bob")
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = bob.address,
                                                  amount = 10,
                                                  token_id = 0)
                                    ])
            ]).run(sender = alice)
        scenario.verify(
            c1.data.ledger[c1.ledger_key.make(alice.address, 0)].balance == 90)
        scenario.verify(
            c1.data.ledger[c1.ledger_key.make(bob.address, 0)].balance == 10)
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = bob.address,
                                                  amount = 10,
                                                  token_id = 0),
                                        sp.record(to_ = bob.address,
                                                  amount = 11,
                                                  token_id = 0)
                                    ])
            ]).run(sender = alice)
        scenario.verify(
            c1.data.ledger[c1.ledger_key.make(alice.address, 0)].balance == 90 - 10 - 11
        )
        scenario.verify(
            c1.data.ledger[c1.ledger_key.make(bob.address, 0)].balance
            == 10 + 10 + 11)
        if config.single_asset:
            return
        scenario.h2("More Token Types")
        tok1_md = FA2.make_metadata(
            name = "The Second Token",
            decimals = 0,
            symbol= "TK1" )
        c1.mint(address = bob.address,
                            amount = 100,
                            metadata = tok1_md,
                            token_id = 1).run(sender = admin)
        tok2_md = FA2.make_metadata(
            name = "The Token Number Three",
            decimals = 0,
            symbol= "TK2" )
        c1.mint(address = bob.address,
                            amount = 200,
                            metadata = tok2_md,
                            token_id = 2).run(sender = admin)
        scenario.h3("Multi-token Transfer Bob -> Alice")
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = bob.address,
                                    txs = [
                                        sp.record(to_ = alice.address,
                                                  amount = 10,
                                                  token_id = 0),
                                        sp.record(to_ = alice.address,
                                                  amount = 10,
                                                  token_id = 1)]),
                # We voluntarily test a different sub-batch:
                c1.batch_transfer.item(from_ = bob.address,
                                    txs = [
                                        sp.record(to_ = alice.address,
                                                  amount = 10,
                                                  token_id = 2)])
            ]).run(sender = bob)
        scenario.h2("Other Basic Permission Tests")
        scenario.h3("Bob cannot transfer Alice's tokens.")
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = bob.address,
                                                  amount = 10,
                                                  token_id = 0),
                                        sp.record(to_ = bob.address,
                                                  amount = 1,
                                                  token_id = 0)])
            ]).run(sender = bob, valid = False)
        scenario.h3("Admin can transfer anything.")
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = bob.address,
                                                  amount = 10,
                                                  token_id = 0),
                                        sp.record(to_ = bob.address,
                                                  amount = 10,
                                                  token_id = 1)]),
                c1.batch_transfer.item(from_ = bob.address,
                                    txs = [
                                        sp.record(to_ = alice.address,
                                                  amount = 11,
                                                  token_id = 0)])
            ]).run(sender = admin)
        scenario.h3("Even Admin cannot transfer too much.")
        c1.transfer(
            [
                c1.batch_transfer.item(from_ = alice.address,
                                    txs = [
                                        sp.record(to_ = bob.address,
                                                  amount = 1000,
                                                  token_id = 0)])
            ]).run(sender = admin, valid = False)
        scenario.h3("Consumer Contract for Callback Calls.")
        consumer = View_consumer(c1)
        scenario += consumer
        scenario.p("Consumer virtual address: "
                   + consumer.address.export())
        scenario.h2("Balance-of.")
        def arguments_for_balance_of(receiver, reqs):
            return (sp.record(
                callback = sp.contract(
                    Balance_of.response_type(),
                    receiver.address,
                    entry_point = "receive_balances").open_some(),
                requests = reqs))
        c1.balance_of(arguments_for_balance_of(consumer, [
            sp.record(owner = alice.address, token_id = 0),
            sp.record(owner = alice.address, token_id = 1),
            sp.record(owner = alice.address, token_id = 2)
        ]))
        scenario.verify(consumer.data.last_sum == 90)
        scenario.h2("Operators")
        if not c1.config.support_operator:
            scenario.h3("This version was compiled with no operator support")
            scenario.p("Calls should fail even for the administrator:")
            c1.update_operators([]).run(sender = admin, valid = False)
        else:
            scenario.p("This version was compiled with operator support.")
            scenario.p("Calling 0 updates should work:")
            c1.update_operators([]).run()
            scenario.h3("Operator Accounts")
            op0 = sp.test_account("Operator0")
            op1 = sp.test_account("Operator1")
            op2 = sp.test_account("Operator2")
            scenario.show([op0, op1, op2])
            scenario.p("Admin can change Alice's operator.")
            c1.update_operators([
                sp.variant("add_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op1.address,
                    token_id = 0)),
                sp.variant("add_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op1.address,
                    token_id = 2))
            ]).run(sender = admin)
            scenario.p("Operator1 can now transfer Alice's tokens 0 and 2")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = alice.address,
                                        txs = [
                                            sp.record(to_ = bob.address,
                                                      amount = 2,
                                                      token_id = 0),
                                            sp.record(to_ = op1.address,
                                                      amount = 2,
                                                      token_id = 2)])
                ]).run(sender = op1)
            scenario.p("Operator1 cannot transfer Bob's tokens")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = op1.address,
                                                      amount = 2,
                                                      token_id = 1)])
                ]).run(sender = op1, valid = False)
            scenario.p("Operator2 cannot transfer Alice's tokens")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = alice.address,
                                        txs = [
                                            sp.record(to_ = bob.address,
                                                      amount = 2,
                                                      token_id = 1)])
                ]).run(sender = op2, valid = False)
            scenario.p("Alice can remove their operator")
            c1.update_operators([
                sp.variant("remove_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op1.address,
                    token_id = 0)),
                sp.variant("remove_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op1.address,
                    token_id = 0))
            ]).run(sender = alice)
            scenario.p("Operator1 cannot transfer Alice's tokens any more")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = alice.address,
                                        txs = [
                                            sp.record(to_ = op1.address,
                                                      amount = 2,
                                                      token_id = 1)])
                ]).run(sender = op1, valid = False)
            scenario.p("Bob can add Operator0.")
            c1.update_operators([
                sp.variant("add_operator", c1.operator_param.make(
                    owner = bob.address,
                    operator = op0.address,
                    token_id = 0)),
                sp.variant("add_operator", c1.operator_param.make(
                    owner = bob.address,
                    operator = op0.address,
                    token_id = 1))
            ]).run(sender = bob)
            scenario.p("Operator0 can transfer Bob's tokens '0' and '1'")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = alice.address,
                                                      amount = 1,
                                                      token_id = 0)]),
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = alice.address,
                                                      amount = 1,
                                                      token_id = 1)])
                ]).run(sender = op0)
            scenario.p("Bob cannot add Operator0 for Alice's tokens.")
            c1.update_operators([
                sp.variant("add_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op0.address,
                    token_id = 0
                ))
            ]).run(sender = bob, valid = False)
            scenario.p("Alice can also add Operator0 for their tokens 0.")
            c1.update_operators([
                sp.variant("add_operator", c1.operator_param.make(
                    owner = alice.address,
                    operator = op0.address,
                    token_id = 0
                ))
            ]).run(sender = alice, valid = True)
            scenario.p("Operator0 can now transfer Bob's and Alice's 0-tokens.")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = alice.address,
                                                      amount = 1,
                                                      token_id = 0)]),
                    c1.batch_transfer.item(from_ = alice.address,
                                        txs = [
                                            sp.record(to_ = bob.address,
                                                      amount = 1,
                                                      token_id = 0)])
                ]).run(sender = op0)
            scenario.p("Bob adds Operator2 as second operator for 0-tokens.")
            c1.update_operators([
                sp.variant("add_operator", c1.operator_param.make(
                    owner = bob.address,
                    operator = op2.address,
                    token_id = 0
                ))
            ]).run(sender = bob, valid = True)
            scenario.p("Operator0 and Operator2 can transfer Bob's 0-tokens.")
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = alice.address,
                                                      amount = 1,
                                                      token_id = 0)])
                ]).run(sender = op0)
            c1.transfer(
                [
                    c1.batch_transfer.item(from_ = bob.address,
                                        txs = [
                                            sp.record(to_ = alice.address,
                                                      amount = 1,
                                                      token_id = 0)])
                ]).run(sender = op2)
            scenario.table_of_contents()

##
## ## Global Environment Parameters
##
## The build system communicates with the python script through
## environment variables.
## The function `environment_config` creates an `FA2_config` given the
## presence and values of a few environment variables.
def global_parameter(env_var, default):
    try:
        if os.environ[env_var] == "true" :
            return True
        if os.environ[env_var] == "false" :
            return False
        return default
    except:
        return default

def environment_config():
    return FA2_config(
        debug_mode = global_parameter("debug_mode", False),
        single_asset = global_parameter("single_asset", False),
        non_fungible = global_parameter("non_fungible", True),
        add_mutez_transfer = global_parameter("add_mutez_transfer", False),
        readable = global_parameter("readable", True),
        force_layouts = global_parameter("force_layouts", True),
        support_operator = global_parameter("support_operator", True),
        assume_consecutive_token_ids =
            global_parameter("assume_consecutive_token_ids", True),
        store_total_supply = global_parameter("store_total_supply", True),
        lazy_entry_points = global_parameter("lazy_entry_points", False),
        allow_self_transfer = global_parameter("allow_self_transfer", False),
        use_token_metadata_offchain_view = global_parameter("use_token_metadata_offchain_view", True),
    )

## ## Standard “main”
##
## This specific main uses the relative new feature of non-default tests
## for the browser version.
if "templates" not in __name__:
    add_test(environment_config())
    if not global_parameter("only_environment_test", False):
        add_test(FA2_config(debug_mode = True), is_default = not sp.in_browser)
        add_test(FA2_config(single_asset = True), is_default = not sp.in_browser)
        add_test(FA2_config(non_fungible = True, add_mutez_transfer = True),
                 is_default = not sp.in_browser)
        add_test(FA2_config(readable = False), is_default = not sp.in_browser)
        add_test(FA2_config(force_layouts = False),
                 is_default = not sp.in_browser)
        add_test(FA2_config(debug_mode = True, support_operator = False),
                 is_default = not sp.in_browser)
        add_test(FA2_config(assume_consecutive_token_ids = False)
                 , is_default = not sp.in_browser)
        add_test(FA2_config(store_total_supply = False)
                 , is_default = not sp.in_browser)
        add_test(FA2_config(add_mutez_transfer = True)
                 , is_default = not sp.in_browser)
        add_test(FA2_config(lazy_entry_points = True)
                 , is_default = not sp.in_browser)

    sp.add_compilation_target("FA2_MOZ_NFT", FA2(config = environment_config(),
                              metadata = sp.utils.metadata_of_url("ipfs://Qmf6tjsd7kwHESMJhCLYNHF7j6AdGNmtnBrcVC4aS87YwL"),
                              admin = sp.address("tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U")))
							  