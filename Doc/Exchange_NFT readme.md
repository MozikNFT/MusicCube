### 1. contract deploy

#### （2）deployed FA2 MOZ/MOS contract

**[1] FA2_FT contract basic information**

administrator:  tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U

explorer address：

https://smartpy.io/explorer.html?address=KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU

to view storage detail：

https://better-call.dev/mainnet/KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU/operations



**<1> MOZ . 1000,0000.000000000000000000,  token id: 0**

account:  tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U  balance：100,0000,000000000000000000



**<2> MOS. 1,0000,0000.000000000000000000,  token id: 1 **

to: tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U

parameters：

```
Value: mint(sp.record(address = sp.address('tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U'), amount = 100000000000000000000000000, metadata = {'' : sp.bytes('0x697066733a2f2f516d6651397067445679657342454a70524443424e4e486837347a4e554d336a5955595a36787a73514c56724c55')}, token_id = 1))
```



#### （3）MOZ/MOS transfer

[1]  banker : tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr

MOZ transfer 90,0000.000000000000000000；

MOS transfer 100,0000.000000000000000000；

```
Value: transfer(sp.list([sp.record(from_ = sp.address('tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U'), txs = sp.list([sp.record(to_ = sp.address('tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr'), token_id = 0, amount = 900000000000000000000000)])), sp.record(from_ = sp.address('tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U'), txs = sp.list([sp.record(to_ = sp.address('tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr'), token_id = 1, amount = 1000000000000000000000000)]))]))
```



[2] huige account：

duncanwang account:  tz1grn9Fz98ASf6KgRopr43AZvodGQkggMwk

 transfer 100.000000000000000000个MOS，tokenid:1

[3]qiwei account ：13564607953 user ID：6792026095664648193 

add：tz1WnzQmnUhADmdDmXK7Uz8ztpPmTjA2KEYA   





#### （4）deploy FA2 NFT contract and publish token:0/1/2/3

administrator:  tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U

explorer address：

https://smartpy.io/explorer.html?address=KT1Nqrmo5815o1wUcPqSjKk4HLMVy6VDRdo8

to view storage detail：

https://better-call.dev/mainnet/KT1Nqrmo5815o1wUcPqSjKk4HLMVy6VDRdo8/operations



**<1> NFT@MOZIK,  token id: 0/**

to artist : tz1cUCeETnnVVcLb9b76zC7RwBUZAwFCc8fX



token metadata: 

```
0x697066733a2f2f516d547455446656736738794c54777a637242716e7675756e79776d504637744851776a676d594d647775725343

information：
{
  "name": "mozik's non-fungible tokens",
  "symbol": "NFT@MOZIK",
  "decimals": 0,
  "shouldPreferSymbol": true,
  "thumbnailUri": "ipfs://QmTYMWr7NC5a35WMTx6FutDKFysd4XiuJc86gb8UJnCqLU"
}
```



Initial Storage parameters：

```
{
    "prim": "Pair",
    "args": [
        {
            "prim": "Pair",
            "args": [
                {
                    "prim": "Pair",
                    "args": [
                        {
                            "string": "tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U"
                        },
                        {
                            "int": "0"
                        }
                    ]
                },
                {
                    "prim": "Pair",
                    "args": [
                        [],
                        [
                            {
                                "prim": "Elt",
                                "args": [
                                    {
                                        "string": ""
                                    },
                                    {
                                        "bytes": "697066733a2f2f516d6636746a7364376b774845534d4a68434c594e4846376a364164474e6d746e4272635643346153383759774c"
                                    }
                                ]
                            }
                        ]
                    ]
                }
            ]
        },
        {
            "prim": "Pair",
            "args": [
                {
                    "prim": "Pair",
                    "args": [
                        [],
                        {
                            "prim": "False"
                        }
                    ]
                },
                {
                    "prim": "Pair",
                    "args": [
                        [],
                        []
                    ]
                }
            ]
        }
    ]
}
```





#### （5）deploy EXCHANGE contract

administrator:  tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U

MOS equals to 1 USDT，one MOZ price is 0.046RMB=0.00713USDT， so mosPerMozHundred = 14022



explorer address：

https://smartpy.io/explorer.html?address=KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb

to view storage detail：

https://better-call.dev/mainnet/KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb/operations



**Initial Storage:**

```
{
    "prim": "Pair",
    "args": [
        {
            "prim": "Pair",
            "args": [
                {
                    "prim": "Pair",
                    "args": [
                        {
                            "string": "tz1c4Zma1UmkEfwmEsqYdMcVpFauhNCeKY3U"
                        },
                        {
                            "string": "tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr"
                        }
                    ]
                },
                {
                    "prim": "Pair",
                    "args": [
                        {
                            "string": "KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU"
                        },
                        {
                            "int": "1"
                        }
                    ]
                }
            ]
        },
        {
            "prim": "Pair",
            "args": [
                {
                    "prim": "Pair",
                    "args": [
                        {
                            "string": "KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU"
                        },
                        {
                            "int": "0"
                        }
                    ]
                },
                {
                    "prim": "Pair",
                    "args": [
                        [],
                        {
                            "prim": "Pair",
                            "args": [
                                {
                                    "int": "14022"
                                },
                                {
                                    "string": "KT1Nqrmo5815o1wUcPqSjKk4HLMVy6VDRdo8"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```



#### （6）with FA2 MOZ/MOS contract，banker add exchange as Operator

Owner： tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr

exchange： KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb



explorer address：

https://smartpy.io/explorer.html?address=KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU

to view storage detail：

https://better-call.dev/mainnet/KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU/operations



parameters：

```
Value: update_operators(sp.list([add_operator(sp.record(owner = sp.address('tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr'), operator = sp.address('KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb'), token_id = 0)), add_operator(sp.record(owner = sp.address('tz1eXdTsaQVbtRAW273gcQko4eH5DnusHaBr'), operator = sp.address('KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb'), token_id = 1))]))
```



#### （7）with  FA2 NFTcontract， approve TOKEN to EXCHANGE 

NFT owner: tz1cUCeETnnVVcLb9b76zC7RwBUZAwFCc8fX

approver：KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb

token id: 0,

explorer address：

https://smartpy.io/explorer.html?address=KT1Nqrmo5815o1wUcPqSjKk4HLMVy6VDRdo8

to view storage detail：

https://better-call.dev/mainnet/KT1Nqrmo5815o1wUcPqSjKk4HLMVy6VDRdo8/operations

parameters:

```
Value: update_operators(sp.list([add_operator(sp.record(owner = sp.address('tz1cUCeETnnVVcLb9b76zC7RwBUZAwFCc8fX'), operator = sp.address('KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb'), token_id = 0))]))
```



#### （8）with EXCHANGE contract， set salled of token id :0

NFT owner: tz1cUCeETnnVVcLb9b76zC7RwBUZAwFCc8fX



explorer address：

https://smartpy.io/explorer.html?address=KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb

to view storage detail：

https://better-call.dev/mainnet/KT19F3JXqrUAJHLnGgTqKgjwvgmk5uFM18tb/operations



**<1> TOKEN 0:  $350 valued MOZ amount：49088

```
_expectedTokenType：MOZ  //choice = “XTZ” or "MOZ"
_saleTokenID：0
_startTime：1627480800
_tokenAddress：KT1WFdKVCDYxMxWSp4YqWUcwJ6a3Qp3tYYGU
_value：49088.000000000000000000
```

