# 1. about auction_NFT.py

The auction_NFT.py has two core contracts named NftAuctionMarket and FA2.

The NftAuctionMarket contract is used to exchange NFT.FA2 token to XTZ by auction.

The  FA2 contract is originated from FA2 template and has some optimization.

Below is the functions:

**(1) Registration contract**

Artists can register in the contract by calling"addAuthor" function in the NftAuctionMarket contract .  They can give detail informations as name, account, head portrait, email, phone ,description, token address when register to the contract. And They can update the informations by calling 

"updateAuthor"function.

**(2) IP Asset management contract**

FA2 contract can management IP assets named non-fungible tokens. IP assets can be minted, transfered, approved. Additional, token metadata can be updated by calling "set_token_metadata" function.

**(3) Basic store and authority**

Besides supporting NFT meta store URL , FA2 support access authority. Only the administrator can change FA2 metadata and token metadata.

**（4）IP exchange through blockchain**

Through NftAuctionMarket and FA2 contract, IP can be exchanged on the blockchain.

**(5) Single management mechanism**

An IP can be put on the shelf with the function "openAuction" in  the NftAuctionMarket contract. It can be off with the function "closeAuctionWithDelivery“ in the normal auction process. And can be canceled with the funciton ”cancelAuction“ in some exception condition by the admin only。

**（6）Account and human mapping**

The author with user account and TEZOS address mapping can be registered in the NftAuctionMarket contract. If an IP is on saled, a authorID will mapping to the IP. It's easy for buyers to get more information about the IP information.

**（7）Automation exchange rights on-chain**

With 3 steps of openAuction ->englishBidding->closeAuctionWithDelivery, an IP can automatic exchange rights on-chain. Because closeAuctionWithDelivery is introduced, so the exchange process can be controlled by the seller. When the seller calls the closeAuctionWithDelivery  function, he must give the encrypted source files to get the XTZ tokenz.

**(8) Advanced store with IPFS**

All the sources as the metadata, token metadata can be stored with IPFS, and recorded in the FA2 or NftAuctionMarket contract.

**(9) IP exchange market**

NFT assets list on the market,anyone select one ,and  add to their cart and exchange if they want.

**(10) Support music fans donation by coins**

a contract that support music fans donation by xtz for the works.

It can be sponsored a donation for specific works with the token_id and the authorID. Any one can donation an amount of XTZ with this contract. At last after the end time of this donation, the sponsor can with draw the amounts of  XTZ which is docated by fans.

**(11) Fans participation for voting**

a contract that anyone can set up a vote and others can vote for it. Any one can sponsor a voting for a specific works with registered author. And then any fans can participate for voting in the round. The most popular works can be founded though this method.

**(12) Ranking and selection mechanism**

After a successful english auction which has a valid bidder, the volume, the seller and the buyer are recorded. So it support ranking by exchang volume、sellers and buyers.

**(13) IP assets protection**

In the NFT contract, it is support to register the DCI certification which is published by China Copyright Administration. The rights can be protected in china and other areas.

**（14）Rights distribution**

[1] Rights distribution protocol

Integrated in the NFT asset contract, the holder can transfer a certain interest

[2] Different priorities of IP management

IP assets are divided into multiple rights and interests, which can be separately authorized and managed.

[3] Advanced IP Assets Registration

support IP property divided into different rights and the holder can control

**（15）Multi-agent co-management contract**

 NFT asset contract, assets can be managed and held by multiple people. 



# 2. Auction Process

![1.overal process](.\doc\1.overal process.png)

## 2.1 openAuction

**description:**

 administrater can update author information which is in the authorMap.

**definition:**

```
    @sp.entry_point     
    def openAuction(self, _param):
```

**process:**

![2. Open Auction](.\doc\2. Open Auction.png)

## 2.2 englishBidding

**description:**

 Any one bidding the goods with the english auction style.

note: if the buyer send the valid currentRSAPublicKey, the seller will delivery the source file with encrypted url.

**definition:**

```
    @sp.entry_point     
    def englishBidding(self, _token_id, _currentRsaPublicKey):  
```

**process:**

![3. EnglishBidding](.\doc\3. EnglishBidding.png)

## 2.3 closeAuctionWithDelivery

**description:**

 After the stop time, the seller delivery the token and the source file to the latest bidder, and get the xtz

If no bidder,just close the auciton.

**definition:**

```
    @sp.entry_point     
    def closeAuctionWithDelivery(self, _token_id, _EncryptedSrcUrl):  
```

**process:**

![4. closeAuctionwithdelivery](.\doc\4. closeAuctionwithdelivery.png)

# 3. High Light to get source files of an encrypted method

This exchange process can delivery encrypted source files on th block chain. Any one can find the public key and the encrypted source files url, but only the buyer can get it. It a good practice to use RSA algorithm.

## 3.1 The bidder launches an english bidding

When the buyer finds a good artwork is on action, he/she can launch an english bidding calling the "englishBidding" function. The inputed parameters are the token id and the rsa publice key.

For example, visit http://web.chacuo.net/netrsakeypair  to get a pair of keys for RSA algorithm.

Public Key:

```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC0zqoU5B2EGOhVoZNxOm2Fnyxu
Lbtz8xJ0jMQpjLRCWuc7mMOup1n+c1L3juCmKM7ZdiZr1eOiAqyrZkWlIvtxdxhW
pcJiRki4W6L73HF98dBUFnHmgGY3n+e/vO3nwWXqgyZ4b0f1+h8+o4eCd1mBdB8q
q0ZYKFo8hM1fH+h/MwIDAQAB
-----END PUBLIC KEY-----
```

Private Key:

```
-----BEGIN PRIVATE KEY-----
MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBALTOqhTkHYQY6FWh
k3E6bYWfLG4tu3PzEnSMxCmMtEJa5zuYw66nWf5zUveO4KYoztl2JmvV46ICrKtm
RaUi+3F3GFalwmJGSLhbovvccX3x0FQWceaAZjef57+87efBZeqDJnhvR/X6Hz6j
h4J3WYF0HyqrRlgoWjyEzV8f6H8zAgMBAAECgYBHdnOVBECCSJHz3oP3Od+1857N
AXhYsNc3h7e0sG9C1skULiIRswWH468EN82k/vYaz28KKiTpkOMMb8TRK01z9VBO
mq0z9rwju6tUA+nvFRuip32B6ET6dWrBxQvlveyY9f9yQMP1g6gHafTbR+niFmRk
mi6iosvIDry1A+1Z4QJBAO+IBNLMpGhxgV/VDWU+sbJJqo7VJ+fUw5w1dodzl9uY
IwLqURbjZkoRhomTaR05y3ghydac0aDMMKiAe8B0nhECQQDBPQvLCSA2kcgqyafA
C/UkyQyByiIhT5NcB135np1Ss5cls9MjyxM8DRiHu0JojSzdUWdeGmQ2HVd9fqvi
H1UDAkEAsjaJIC2RxQNuNlbVeJaErxmQBGUjI6FxSC+e2Hhwa7ltkyWy30yhNkqD
xqgedNgjQmYhPcO/U9uX+EZfzHj3gQJBALyiwyhouDGNDkH2qPMouR43xSXOFJNA
AzILXwmWdS2OczYy3SJL03MDtbaKbsFxTyKdnLKYQMsyyX2QcmpC+9ECQQDOsF8F
02qaJeX5oqixssYs/erCNyiEm46NE+4mErTZfu3m49wR2kCF4nBc3ikqLN2XOvc/
RPJe4vt94FI8Augg
-----END PRIVATE KEY-----
```

## 3.2 The seller closes the auction with delivery encrypted source files url

The seller closes the auction with delivery encrypted source files url after the stop time. When he/she finds a valid bidder with it's public key. She/he calls the "closeAuctionWithDelivery" function to delivery encrypted source files url,  transfer the NFT token to the buyer, and get the XTZ from the contract.

As example, if the source files url is:

```
link：https://pan.baidu.com/s/19hva39VMkOj3Cb1sfYE1jw 
code：jsz0
```

Visit http://tool.chacuo.net/cryptrsapubkey, use the public key above to encrypted the source files url, and get the result:

```
GlE99f4jFUmopXswWrcd4w/xXz9rSpNxqD0c3FMfDPl80QcKkE14cpd9q9YgRdj52I72Xd2oIPVPNa2F/47wrxlSEvzQPvHruWIeKujJEENImra3aaAfjH92LzV9FF96u+M+vyfo1KJyO+cfm+OGrDGaaxWDqG7FirV2/DLQrko=
```

## 3.3 The buyer decrypts the source files url

When the buyer get the NFT token which indicated by the temple wallet,  he can decrypt the source files url with the private key.

Because the private key is known only by the buyer, the original source files url is just get by the sellers and the buyer. 

As example, Visit http://tool.chacuo.net/cryptrsaprikey, use the private key to decrypt the source files url.



private key:

```
-----BEGIN PRIVATE KEY-----
MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBALTOqhTkHYQY6FWh
k3E6bYWfLG4tu3PzEnSMxCmMtEJa5zuYw66nWf5zUveO4KYoztl2JmvV46ICrKtm
RaUi+3F3GFalwmJGSLhbovvccX3x0FQWceaAZjef57+87efBZeqDJnhvR/X6Hz6j
h4J3WYF0HyqrRlgoWjyEzV8f6H8zAgMBAAECgYBHdnOVBECCSJHz3oP3Od+1857N
AXhYsNc3h7e0sG9C1skULiIRswWH468EN82k/vYaz28KKiTpkOMMb8TRK01z9VBO
mq0z9rwju6tUA+nvFRuip32B6ET6dWrBxQvlveyY9f9yQMP1g6gHafTbR+niFmRk
mi6iosvIDry1A+1Z4QJBAO+IBNLMpGhxgV/VDWU+sbJJqo7VJ+fUw5w1dodzl9uY
IwLqURbjZkoRhomTaR05y3ghydac0aDMMKiAe8B0nhECQQDBPQvLCSA2kcgqyafA
C/UkyQyByiIhT5NcB135np1Ss5cls9MjyxM8DRiHu0JojSzdUWdeGmQ2HVd9fqvi
H1UDAkEAsjaJIC2RxQNuNlbVeJaErxmQBGUjI6FxSC+e2Hhwa7ltkyWy30yhNkqD
xqgedNgjQmYhPcO/U9uX+EZfzHj3gQJBALyiwyhouDGNDkH2qPMouR43xSXOFJNA
AzILXwmWdS2OczYy3SJL03MDtbaKbsFxTyKdnLKYQMsyyX2QcmpC+9ECQQDOsF8F
02qaJeX5oqixssYs/erCNyiEm46NE+4mErTZfu3m49wR2kCF4nBc3ikqLN2XOvc/
RPJe4vt94FI8Augg
-----END PRIVATE KEY-----
```

encrypted the source files url:

```
GlE99f4jFUmopXswWrcd4w/xXz9rSpNxqD0c3FMfDPl80QcKkE14cpd9q9YgRdj52I72Xd2oIPVPNa2F/47wrxlSEvzQPvHruWIeKujJEENImra3aaAfjH92LzV9FF96u+M+vyfo1KJyO+cfm+OGrDGaaxWDqG7FirV2/DLQrko=
```

the original source files url:

```
link：https://pan.baidu.com/s/19hva39VMkOj3Cb1sfYE1jw 
code：jsz0
```

# 4. donation Process

![6.donation process](.\doc\6.donation process.png)

# 5. voting Process



![7.votiong process](.\doc\7.votiong process.png)

# 6.  multiple rights distribution



![multiple rights](.\doc\8.multiple rights.png)
