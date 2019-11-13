<h1>⌁⌁ZAP⌁⌁</h1> 
<h1>THE ZEROLAW org-AUGMENTATION PROTOCOL</h1>

<h2>1. Introduction</h2>

The ZeroLaw Augmentation Protocol (ZAP) is a general-purpose tech/law stack for augmenting any business entity or organization through the use of smart contracts and tokens deployed to Ethereum. It is non-rent-seeking, fully free and open source and is neither funded by nor requires the use of any protocol token. It is intended to be compatible with a range of legal compliance strategies or applicable legal regimes by providing tunable compliance parameters; it is even compatible with antilaw positions. ZAP’s compliance parameters may be tuned 'all the way up,' 'all the way down' or anywhere in between; thus, ZAP is suitable for any entity or organization, ranging from traditional corporations to anarchic, pseudonymous collectives. ZAP merges the vision of a borderless, decentralized future with the power to comply with existing legal requirements & best practices for doing business. ZAP has been developed by ZeroLaw, an independent law/technology team working to make technology and legal agreements interoperable. Anyone may contribute to the protocol. 

ZAP's highly modular architecture is divided into Components, with each Component being a tech/law dyad consisting of:
<ul>  
 <li>on the law side: legal agreements, statutes and/or rules expressed in natural language</li> 
 <li>on the tech side: a system of interlinked smart contracts coded in Solidity</li>
</ul>
 
 ZAP Orgs may differ significantly from one another depending on the type of entity or organization being augmented through the protocol. This paper aims to explain a prototypical ZAP implementation, with notes regarding how parameter settings might differ among Org types. 

<h3>Important Disclaimer - Please Read!</h3>

ZAP, this paper, the ZAP source code and the other ideas, documents and materials referenced herein or included in any ZeroLaw or ZAP software repository (the “**_ZeroLaw Materials_**”) are not intended to be, or to serve the purposes of, legal, accounting, tax, investment, or other advice or services. There is no attorney-client or other representational or fiduciary relationship between ZeroLaw or any person affiliated or otherwise connected with or representing ZeroLaw or who has or will contribute to the ZeroLaw Materials (each, a “**_ZeroLaw Participant_**”), on the one hand, and any reader, recipient or user of the ZeroLaw Materials (each, a “**_ZeroLaw User_**”), on the other hand. The ZeroLaw Materials are being provided on an as-is basis and for informational purposes only, and should be considered highly experimental and unreliable. Any use of the ZeroLaw Materials should be vetted with an attorney and other applicable professional advisors. No ZeroLaw Participant is making any statement, representation, warranty, guarantee, or assurance that any of the ZeroLaw Materials is suitable for any purpose or complies with any applicable law. No ZeroLaw Participant has promised or is undertaking to provide any assistance, service or guidance to any ZeroLaw User.

<h2>2. The Org Component</h2>

<h3>OrgLaw</h3>

The law of the Org is its spirit. The OrgLaw comprises the Org's constitutional or charter principles (whether or not expressed in a written document), and, if it is a state-chartered Org, the applicable authorizing legal regime. For example, if the Org is a Delaware corporation, its OrgLaw will be its certificate of incorporation and bylaws, together with the Delaware General Corporation Law. If the Org is a DAO*, then the OrgLaw may be an informal, mutable social contract or community understanding based on the members’ shared values along with any rules relating to partnerships or unincorporated associations that apply in relevant jurisdictions. 

The relationship between the OrgLaw and the OrgCode is complex, nuanced, and potentially bidirectional. The OrgLaw may define the rules, regulations and agreements that are to be implemented in the OrgCode. Alternatively, OrgLaw may consist of rules, regulations and/or agreements specifying a “code deference” approach to governance. Code deference approaches may be absolute or qualified and complete or partial.

<table>
  <tr>
   <td>Code Deference Approach
   </td>
   <td>Complete
   </td>
   <td>Partial
   </td>
  </tr>
  <tr>
   <td>Absolute
   </td>
   <td>
   "Code Is Law" For All Org Governance
   </td>
   <td>
   "Code Is Law" For Governance of Some Aspects of Org
   </td>
   </tr>
   <tr>
   <td>Qualified</td>
   <td>
   All Org Governance Defers to Code, Except in Limited Cases Like Consensus Attack, Court Orders, Etc.
   </td>
   <td>
   Some Aspects of Org Governance Defer to Code, Except in Limited Cases Like Consensus Attack, Court Orders, Etc.
   </td>
   </tr>
</table>

For an example of qualified partial code deference, see [The Model DAO Charter](https://).

***A Word On “DAOs”** The term “DAO” is probably one of the most ambiguous and widely misused in the blockchain/DeFi community.  In this paper we use the term “DAO” to refer to a type of Org—meaning that a DAO is a code/law dyad, just like any other Org. The OrgLaw for a DAO may be anarchic, but that is still a form of social agreement which we regard as ultimately legalistic (and potentially binding) in nature. DAOs may also be subject to default laws included in their OrgLaw, even if the DAO members are unaware of such default laws—for examples, in common law jurisdictions DAOs may be general partnerships by default.  Unless otherwise expressly stated, we do **not** use the term “DAO” to refer solely to a smart contract that automates treasury, voting and liquidation functions for an Org—rather, we refer to such a smart contract as the OrgCode for a DAO, or as the 'DAO smart contract'. 

We also adopt the following DAO typology:

<ul>
    <li>'GrantDAOs'-> grant-giving (MolochDAO)</li> 
    <li>'VentureDAOs' -> venture capital (TheDAO by slock.it)</li>
    <li>'GovDAOs' -> protocol/DAPP governance (MakerDAO)</li>
    <li>'PACDAOs' -> political (YangDAOofficial)</li>
    <li>'ShadowDAOs' -> hacktivist/anon (?)</li>
</ul>

<h3>B. OrgCode</h3>

If the OrgLaw is the soul or mind of the Org, then the OrgCode is the Org’s CNS. The OrgCode consists of a smart contract deployed to Ethereum as an instance of[ IsssuingEntity.sol](https://github.com/zerolawtech/SFT-Protocol/blob/master/contracts/IssuingEntity.sol). Other smart contracts become part of the OrgCode by becoming connected to the OrgCode via the applicable[ association method](https://sft-protocol.readthedocs.io/en/latest/issuing-entity.html#associating-contracts), either through an owner- or administrator-controlled association process or through a more open process, depending on the configuration of the Org in question. The OrgCode then either implements or extends the OrgLaw by administering these ancillary smart contracts. For example:

<ul>
    <li>ShareCode contracts (i.e., instances of SecurityToken.sol or NFToken.sol) must be associated to the OrgCode before OrgShares can be transferred, so that the OrgCode can accurately track holder addresses</li>
    <li>IDcode contracts (i.e., instances of KYCIssuer.sol or KYCRegistrar.sol) must be associated to the OrgCode to provide any identity confirmation data that may be required by the ShareLaw before new addresses/persons can receive or send OrgShares</li>
    <li>Custodian contracts (i.e., instances of OwnedCustodian.sol or iBaseCustodian.sol) must be associated to the OrgCode in order to send or receive OrgShares, and the OrgCode is also where any applicable restrictions will be set on a custodian contract</li>
</ul>

The OrgCode is administered by a standard multi-sig permissioning scheme inherited from[ MultiSig.sol](https://sft-protocol.readthedocs.io/en/latest/multisig.html#multisig). The owner(s) of the OrgCode (one or more Ethereum addresses declared as owners in the OrgCode constructor) may access any administrative function of the OrgCode. Owners may also delegate administrative function access to one or more additional authorities (one or more Ethereum addresses declared as authorities through the .addAuthority method). Authorities are approved by owners on an administrative-function-by-administrative-function basis via the function _signatures parameter of .addAuthority; such _signatures may include any administrative function other than the .addAuthority method itself, which can only be called by owners. Both owner and authority rights to can be tied to a multisig threshold via the _threshold parameter. Authority permissioning may additionally be time-limited via the _approvedUntil parameter. The parameters for existing owners and authorities can be modified later via various specialized methods. The same permissioning scheme can be extended to the Org's custom modules (see Section 5 below).

This scheme is very powerful and flexible, accommodating a wide array of potential use cases and compliance techniques. For example, an Org that is a corporation could configure each issuance of an OrgShare token to be authorized by two addresses respectively controlled by the President and Secretary of the corporation. This would mirror the two-officer signature requirement for stock certificates imposed by most states’ corporation statutes.

<h2>3. The Shares Component & IDVerifier Component</h2>

<h3>A. ShareLaw</h3>

<h4>i. Intro to ShareLaw</h4>

On the social/legal layer, OrgShares are transferable legal rights pertaining to the Org. You can think of OrgShares as the reification of the rights conferred upon particular Org participants by the OrgShare.

Below are some illustrative examples, for various Org types, of how the ShareLaw of those Org types could be/often would be configured:

<table>
  <tr>
   <td>Org Type
   </td>
   <td>OrgShare Type
   </td>
   <td>ShareLaw
   </td>
  </tr>
  <tr>
   <td>Corporation (DE)
   </td>
   <td>Capital Stock
   </td>
   <td>DGCL
<p>
Certificate of Incorporation
<p>
Bylaws
<p>
U.S. Federal Securities Laws
<p>
Ordinary Income Tax (mostly)
   </td>
  </tr>
  <tr>
   <td>LLC (DE)
   </td>
   <td>Membership Interests
   </td>
   <td>DLLCA
<p>
Operating Agreement
<p>
U.S. federal securities laws 
<p>
Partnership Income Tax (mostly)
<p>
 
<p>
 
   </td>
  </tr>
  <tr>
   <td>GrantDAO (e.g.—MolochDAO)
   </td>
   <td>Investment club membership?
<p>
Coop interest?
<p>
General partnership interest?
   </td>
   <td>Quorum-less majority voting
<p>
Ragequit
<p>
Rough social norms & floating delegations communicated through member-only channels
<p>
Gift Tax?
   </td>
  </tr>
  <tr>
   <td>VentureDAO (e.g. TheDAO)
   </td>
   <td>investment contract interest in decentralized venture fund
   </td>
   <td>misc. governance arrangements
<p>
Misc voting
<p>
Securities Laws
<p>
Unclear taxation—likely partnership
   </td>
  </tr>
  <tr>
   <td>Other DAOs
   </td>
   <td>Misc.
   </td>
   <td>Misc.
   </td>
  </tr>
</table>

<h4>ii. Share Instruments</h4>

In the immediately preceding section, we discussed how the ShareLaw divides determines the type of OrgShares—for example, whether the OrgShares are capital stock, club memberships, investment contracts, or something else. However, those types of categories are essentially classifications of types of rights—they are very abstract. The ShareLaw does not stop there—it also classifies types of OrgShare _instruments_.

Instruments are methods of representing, and evidencing ownership over, OrgShares. Although the distinctions among types of instruments may appear dry and technical, they are critical from a legal perspective. Many other security token protocols ignore this issue and do not clearly and consistently treat tokens as belonging to a defined category of legal instruments. Under corporate and commercial law, the type of instrument by which an OrgShare is transferred will determine what formalities need to be followed with respect to transactions such as transferring ownership of the OrgShare or pledging the OrgShare as collateral for a loan.

Under the Uniform Commercial Code, there are three types of securities instruments:
<ul>
    <li>certificated</li>
    <li>uncertificated (aka “book-entry”)</li>
    <li>account-based/entitlement-based</li>
</ul>

It is critical that the instrument type for each OrgShare be explicit so that each person transacting in the OrgShare knows what type of instrument he or she is dealing with. For example, if a lender is extending credit to a shareholder and taking a security interest in the OrgShare as collateral, the lender cannot know how to perfect its rights to foreclose on the OrgShare in an event of default unless it knows the instrument type of the corresponding token: if the token is a securities certificate, then the lender can take possession of the token and be assured of having a first-priority security interest; on the other hand, if the token is a book-entry representation of the OrgShare, then the lender must notify the Org to ensure that the Org notes the encumbrance on the Org’s books and does not make alternative transfers.

As further discussed below under “ShareCode,” ZAP accommodates blockchain equivalents to all three types of instrument. Although each instrument type has pros and cons, and such pros and cons may differ depending on the relevant type of Org in question, in general ZeroLaw believes tokens functioning as securities certificates are work better on a public permissionless blockchain because they create the opportunity for finer (and potentially more liberal) transferability tuning and chain-of-title analysis, which can be vitally important in securities transactions. The lending example above leads to one illustration of how the certificated model is a far more natural fit for blockchain, as people will naturally wish to view possession of a token representing an OrgShare or the locking up of that token in a multisig smart contract as a form of possession of a securities certificate in token form that ought to create a senior, perfected security interest in the OrgShare as collateral.  For a very in-depth discussion of this topic, _see_ “_[Representation of Corporate Capital Stock via Cryptographically Secured Blockchain Tokens: Motivations and Potential Implementations](https://gabrielshapiro.wordpress.com/2018/10/28/2/)”_ by Gabriel Shapiro.

<h4>iii. Transfer Restrictions</h4>

An Org may desire to (or, depending on the applicable law, may be required to), limit the transferability of OrgShares. OrgShare transfer restrictions constitute part of the ShareLaw, and such aspects of the ShareLaw may in many cases be programmatically enforced in the ShareCode.

There are three main types of transfer restrictions:

<ul>
    <li>identity-based</li>
    <li>transaction-based</li>
    <li>vesting-based (may be time-based, service-based or milestone-based vesting);</li>
</ul>

Transfer restrictions typically arise from four main sources of law (or a combination thereof):

<ul>
    <li>securities laws (if the OrgShares are securities)</li>
    <li>general regulatory requirements such as export/sanctions controls, money transmitter laws, etc.</li>
    <li>legal contract or other private agreement</li>
    <li>misc. commercial laws and property laws</li>
</ul>

Transfer restrictions will typically apply at one of the following levels of granularity (or a combination thereof):

<ul>
    <li>all OrgShares;</li>
    <li>all OrgShares of a given class or series;</li>
    <li>specific OrgShares</li>
    <li>any/all OrgShares held by or on behalf of a specific individual or entity (or a single address associated to a given individual/entity) or smart contract</li>
</ul>

Transfer restrictions will typically apply in one or both of the following markets:

<ul>
    <li>primary market (Org → shareholder)</li>
    <li>secondary market (shareholder-->shareholder or shareholder-->Org)</li>
</ul>

Below are some illustrative examples, for various Org types, of common transferability restrictions


<table>
  <tr>
   <td>
     Transfer Restriction
   </td>
   <td>
    Type(s)
   </td>
   <td>
    Law Source
   </td>
   <td>
    Granularity
   </td>
   <td>
    Market
   </td>
  </tr>
  <tr>
   <td>
    not owned/transferable until <service has been provided through/milestone has been achieved at> time <em>T</em>
   </td>
   <td>
    vesting
   </td>
   <td>
    contract law
   </td>
   <td>
    specific OrgShares
   </td>
   <td>
    primary & secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable if post-transfer Org would have more than 499 unaccredited shareholders or more than 1,999 total shareholders
   </td>
   <td>
    transaction-based & identity-based
   </td>
   <td>
    SEC Rule 12g-1
   </td>
   <td>
    all equity securities OrgShares
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable to an unaccredited investor in a private placement where issuer is relying on Rule 506(c)
   </td>
   <td>
    Identity-based & transaction-based
   </td>
   <td>
    SEC Rule 506(c)
   </td>
   <td>
    specific OrgShares or all OrgShares of a class/series
   </td>
   <td>
    primary
   </td>
  </tr>
  <tr>
   <td>
    if a “restricted security,” not transferable during first 12 months after issuance, except to qualified institutional buyer (QIB)
   </td>
   <td>
    transaction-based w/ identity-based exception
   </td>
   <td>
    SEC Regulation D & Rule 144
<p>

    Rule 144A
   </td>
   <td>
    specific securities OrgShares
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    no transfer by an affiliate of the issuer unless disclosure requirements, volume limitations, and manner of sale conditions have been met, except to QIBs
   </td>
   <td>
    identity-based w/ identity-based exception
   </td>
   <td>
    SEC Regulation D
<p>

    Rule 144
   </td>
   <td>
    any/all securities OrgShares held by or on behalf of a specific holder
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable except in compliance with ROFR and co-sale procedures
   </td>
   <td>
    transaction-based
   </td>
   <td>
    ROFR and Co-Sale Agreement
   </td>
   <td>
    typically all OrgShares or all OrgShares of a given class/series; sometimes further limited to large holders only
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable to individuals/entities appearing on OFAC’s<a href="https://www.treasury.gov/ofac/downloads/sdnlist.pdf"> specially designated and blocked persons (SDN) list</a>
   </td>
   <td>
    identity-based
   </td>
   <td>
    misc sanctions regulations and executive orders
   </td>
   <td>
    all OrgShares
   </td>
   <td>
    primary and secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable in a manner utilizing OrgShares as a convertible virtual currency
   </td>
   <td>
    transaction-based
   </td>
   <td>
    money services business regulations
   </td>
   <td>
    all OrgShares
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    not transferable to a known DEX or other exchange address, or third party custodian, that is not a registered securities exchange or ATS or registered broker/dealer
   </td>
   <td>
    identity-based
   </td>
   <td>
    securities laws
   </td>
   <td>
    all securities OrgShares
   </td>
   <td>
    primary and secondary
   </td>
  </tr>
  <tr>
   <td>
    no transfer by a holder subject to an injunction not to make the transfer (could be bankruptcy-related, divorce-related, etc.)
   </td>
   <td>
    identity-based
   </td>
   <td>
    misc. laws
   </td>
   <td>
    any/all OrgShares held by or on behalf of a specific holder
   </td>
   <td>
    secondary
   </td>
  </tr>
  <tr>
   <td>
    no transfer of a share encumbered by a perfected first-priority lien, except to the lienholder
   </td>
   <td>
    transaction-based w/ identity-based exception
   </td>
   <td>
    private agreement
<p>

    misc. property laws
   </td>
   <td>
    specific OrgShares
   </td>
   <td>
    secondary
   </td>
  </tr>
</table>


An Org may not wish to or be required to implement all types of transfer restrictions.  Nevertheless, a robust general-purpose Org augmentation protocol must be **able to** accommodate all such transfer restrictions and more. Otherwise, a protocol will effectively be requiring Orgs to choose between taking advantage of the efficiencies of the protocol and non-compliance (or high risk of non-compliance) with applicable law. On the other hand, the protocol should not assume that every Org will need to comply with all such transfer restrictions and should recognize that, consistent with the politics and ideals of decentralization, Org administrators should minimize their power to censor transactions to the greatest extent possible without violating the law. Therefore, while transfer restrictions & associated permissioning schemes must be possible, they must also be optional and tunable. This is the approach embodied in ZAP.  

<h4>iv. Identity-Based Restrictions</h4>

As noted above, many potential transfer restrictions are identity-based. Complying with such transfer restrictions will require an off-chain identity documentation process capable of verifying that a particular prospective Shareholder is a certain person in the real world, the Ethereum addresses belonging to that person, the legal jurisdictions relevant to that person and that the person satisfies any applicable “accreditation requirements” and does not appear on (or reside in a country that appears on) any applicable sanctions lists. Many ID verification services exist, including ones that verify the “accredited investor” status of investors under U.S. federal securities law. We anticipate that, over time, vendors who provide such services will supplement them with blockchain-specific subservices, such as maintaining lists of Ethereum addresses associated with DEXs or centralized exchanges which an Org may desire to prevent from receiving OrgShares.  

The Org’s chosen off-chain verification processes provide the content for whitelists and blacklists.

Whitelists are essential when OrgShares should only be issued and/or transferred to certain types of person. Let us consider an example relating to both primary market and secondary market transactions: the restriction of transfers on OrgShares that are securities sold in a SEC Rule 506(c) private placement. To qualify for Rule 506(c), the issuer must verify that all of the primary purchasers of the OrgShares are “accredited investors.” When those OrgShares are sold, they will initially be “restricted securities”—meaning that the purchasers cannot resell the OrgShares until 12 months from the date of the initial sale. However, the 12-month restriction, in turn, has an identity-based exception: the OrgShares may be resold to persons who are verified to be “qualified institutional buyers” (QIBs). Thus, the Org’s whitelist should include both verified “accredited investors” and verified “QIBs”. These whitelists could either be compiled by the Org itself (or a service provider acting on behalf of the Org), and thus essentially be private, Org-specific whitelists, or they could be master lists directly or indirectly licensed to the Org by vendors who specialize in compiling and maintaining such lists.

Blacklists are perhaps even more important. While it is theoretically possible for OrgShares to be freely tradeable in general (for example, if the OrgShares are not securities, or if they are SEC-registered securities), it will nevertheless nearly always be true that at least certain types of persons should be excluded from owning OrgShares. Consider some examples: Orgs subject to U.S. jurisdiction will be prohibited from transacting business with persons listed on OFAC’s[ specially designated and blocked persons (SDN) list](https://www.treasury.gov/ofac/downloads/sdnlist.pdf),  and would be well advised to comply with those prohibitions; similar lists exist in most other jurisdictions. 

Other reasons for blacklisting may be more Org-specific. For example, a commercial Org may wish to prevent its competitors from acquiring its OrgShares. An Org whose OrgShares are securities may wish to take reasonable precautions to reduce the likelihood that the OrgShares will be transferred to known custodial cryptocurrency exchanges or cryptocurrency DEXs that are not legally permitted to facilitate trading of securities. If the OrgShare is a non-security under EU law but would be a security under U.S. law, then the Org may wish to blacklist any person known to be a U.S. citizen or resident. If the OrgShare is a security issued by a U.S. issuer under a Regulation S exemption, then the Org may wish to blacklist all U.S citizens and residents for a period of 12 months to prevent flowback and remain eligible for the exemption.

So far, we have mainly discussed commercial and regulatory reasons why identity verification, whitelisting and blacklisting can matter. However, even ShadowDAOs might require the power to whitelist and blacklist persons as part of practicing good OpSec and maintaining cultural consistency. For example, a hacktivist cooperative may wish to restrict transfers of its Shares to nation-state actors or ideologically opposed groups. The “rating” process for such a ShadowDAO may be binary—you’re either in or you’re out—but a form of minimal ID-verification may be needed to confirm that the person in control of a particular forum handle is also in control of a particular Ethereum address. 

Similarly, a DAO organized around local politics may wish to ensure that Shares can only be held by residents of the applicable municipality. If a group of developers is selling a token intended not to be a security, then that group may wish to only allow transfers of that token to individuals who pass a series of Q&As and tests proving that they are not buying for investment purposes, as contemplated by the Brooklyn Project’s[ Consumer Token Framework](https://collaborate.thebkp.com/project/BKP/document/1/version/2). Alternatively, if a DAO or similar association wishes to allow free transferability, then that principle may be enshrined in its ShareLaw, and there will be no whitelists or blacklists. Thus, the ShareLaw Component, including the identity verification aspects thereof, augments, rather than limits, Orgs’ autonomy.

<h3>B. SharesCode</h3>

<h4>i. OrgShare Instruments as Tokens</h4>

On the tech layer, OrgShares are represented as tokens on Ethereum, with each token having programmatically tunable levels of transferability. The tokens are thus transferable instruments representing OrgShares, and can be classified as certificates, book entries or entitlements.

ZAP represents certificated shares as non-fungible tokens (NFTs) issued by an instance of[ NFToken.sol](https://github.com/zerolawtech/SFT-Protocol/blob/master/contracts/NFToken.sol). Just as paper stock certificates issued by a corporation have unique identifying numbers, each ‘token-cert’ is uniquely identifiable by ID#. This enables powerful and useful functionality: for example, imposing share-specific transfer restrictions, or tracing the provenance of particular shares in a mixed account. 

Although token-certs are instruments representing OrgShares, there is a layer of separation between them and the Org. Just as paper stock certificates can change hands without the corporation that issued them either being on notice of, approving or recognizing, the transfer, so, too, token certs can be transferred independently from the Org (assuming the absence of on-chain transfer restrictions) without the Org needing to know the identity of the transferee or approve such transfer in advance. Just as a paper stock certificate can be stolen or destroyed without the true owner of the stock losing his or her legal ownership rights in the stock, so too, if a token certificate is transferred accidentally, or the owner loses the key or has it stolen, this does not entail a change in ownership rights over the corresponding OrgShares. 

This layer of separation between the Org and the token certificates representing OrgShares has many implications. On the one hand, it allows OrgShareholders greater immediate property rights over their OrgShares, since they can be transferred quite freely. On the other hand, transferees run a  greater degree of risk in such transactions than they do in purchases of book-entry shares. Whereas a book-entry share transfer inherently requires the Org's approval, a transfer of a token certificate does not. In theory, this means that the transfer could be prohibited by the Org without the would-be transferee knowing it, in which case the would-be transferee might have paid for the OrgShares but not be entitled to exercise ownership rights with respect to the OrgShares. 

Even when the transfer of OrgShares is legal, the Org will likely take the position that if a token certificate representing an OrgShare has been transferred to a new address, the holder of that OrgShare will not be able to vote on Org issues or received Org dividends until completing the appropriate ID verification procedure. These issues can be mitigated to an extent by careful planning and coding, but never completely—unlike a cryptonative asset like BTC or ETH, the tokens are a representation of an OrgShare, not identical with an OrgShare, and thus it is possible in corner cases for the symbol to become detached from the legal rights it is supposed to symbolize.

ZAP can also represent OrgShares in book-entry form. ZAP represents book-entry shares as fungible tokens issued by an instance of[ SecurityToken.sol](https://github.com/zerolawtech/SFT-Protocol/blob/master/contracts/SecurityToken.sol). Under that approach, the Ethereum blockchain becomes the Org’s official share ledger and transfers of the tokens represent official changes to the OrgShare's ledger. If the Org is a corporation, this approach is explicitly permitted under the Wyoming and Delaware corporate statutes (with Wyoming’s version of the statute even allowing for transfers to be recorded as changes in owners represented as Ethereum address rather owners represented as the legal names of persons). 

Since the blockchain is meant to be the Org’s official share ledger, the degree of separation between the Org and the secondary market that exists with token-certs does not really exist under the book-entry approach. The Org will be deemed to have approved or given official effect to any transfer of an OrgShare that gets recorded on the blockchain. Therefore, the Org will likely want to adopt the tightest possible transfer restrictions and institute manual review procedures to ensure that it is not officially recording a prohibited transfer of OrgShares.  This is more cumbersome than the certificated system described above, but does offer an advantage to third parties who might be considering acquiring OrgShares—they can know from the state of the blockchain that the Org regards the history of transfers as valid.

Although in general we believe the main benefit to deploying an Org on Ethereum is the resulting disintermediation, and thus anticipate that few Orgs will tend to represent their OrgShares through account-based/entitlement-based instruments, ZAP nevertheless has the capability of doing so. ZAP represents entitlement-based OrgShares as tokens held by a special type of custodial smart contract deployed as an instance of OwnedCustodian.sol or IBaseCustodian.sol. Such OrgShares may also be conceptualized as simply being token-certs that are held by a custodian or book entries that are marked as giving authority to custodians. For more on custodial smart contracts, see  below.  

<h4>ii. Code-Enforced Share Transfer Restrictions</h4>

Transfer restrictions can be encoded in the smart contract rules governing transfer of the tokens representing the OrgShares, and thus enforced programmatically. This reduces monitoring and enforcement costs and can thus facilitate freer transfer even of restricted securities than might otherwise be feasible.

Direct transfer restrictions are set by the owner or another appropriately permissioned authority of the Org smart contract (an instance of IssuingEntity.sol). Such restrictions can be set at various levels of granularity:

<ul>
    <li>identity-based transfer restrictions—i.e., restrictions on all OrgShares held by a particular shareholder or custodian—are set by calling IssuingEntity.setEntityRestriction(bytes32 _id, bool _restricted), where bytes32_id is the unique HashID of the restricted holder (_see below_ under “ID Verification” for more on HashIDs)</li>
    <li>restrictions on all of the OrgShares or all of the OrgShares of a given class or series—i.e., restrictions on particular OrgShares, regardless of who holds them—are set by calling IssuingEntity.setTokenRestriction(address _token, bool _restricted)</li>
</ul>

It is also possible to impose various other types of transfer restrictions indirectly. An Org may define a limit on the number of unique shareholders it will have. Such a limit may be defined on a per-Org, per-country and/or per-accreditation-type basis.

For example, if the OrgShares are equity securities and the Org is a pre-IPO company that has or will be expected to have $10M+ in assets, the Org will want to prohibit any transfer of OrgShares that would result in the Org having more than 499 unaccredited shareholders or more than 1,999 overall to prevent itself from having to “go public” prematurely under SEC Rule 12g-1 / Section 12(g)(1) of the Securities Exchange Act of 1934. Such investor limits have the same effect as transfer restrictions because programmatically prevent transfers that would cause the Org to violate the applicable condition. An example of a situation in which restrictions by country would be important would be where an Org wishes to take advantage of Regulation S so that a particular issuance of OrgShares is not covered by U.S. law and thus programmatically prohibits all transfers of OrgShares to U.S. citizens and U.S permanent residents, either indefinitely or for a period of time (e.g., the 12-month anti-flowback period for equity securities under Tier ____ of Regulation S).

Shareholder counts and limits are stored in uint32[8] arrays. The first entry in each array is the sum of all the remaining entries. The remaining entries correspond to the count or limit for each accreditation level. Setting an investor limit to 0 means no limit is imposed. The issuer must explicitly approve each country from which investors are allowed to purchase tokens. It is possible for an issuer to set a limit that is lower than the current investor count. When a limit is met or exceeded existing investors are still able to receive tokens, but new investors are blocked.

Investor limits are configured with setter functions called on the OrgCode (the Org’s instance of IssuingEntity.sol).

The setter method IssuingEntity.setCountry(uint16 _country, bool _permitted, uint8 _minRating, uint32[8] _limits) approves or prohibits a country’s citizens or permanent residents from being shareholders and sets investor limits within that country. Its parameters are as follows:

<ul>
    <li>_country: The code of the country to modify</li>
    <li>_permitted: Permission bool</li>
    <li>_minRating: The minimum rating required for an investor in this country to hold tokens. Cannot be zero.</li>
    <li>_limits: A uint32[8] array of investor limits for this country which essentially supplies investor limits in a destructured variable assignment. The seven positions in the array correspond to the seven possible shareholder accreditation types. If there are fewer than seven possible accreditation types, the remainder will be set to “0”. For example, for U.S. issuers, there are likely to be three accreditation types—unaccredited, accredited and QIB—and thus four of the array elements would typically be 0.</li>
</ul>

IssuingEntity.setCountries(uint16[] _country, uint8[] _minRating, uint32[] _limit) is a similar setter method that enables approving many countries (with corresponding per-country investor limits) at once without per-country differences in limitations that vary based on the shareholder’s accreditation level.

The setter method IssuingEntity.setInvestorLimits(uint32[8] _limits) sets total shareholder limits for the Org by accreditation type, irrespective of country. This is likely to be the most common setter method used by early, pre-public ZAP orgs. For example, a U.S.-based Org whose OrgShares are equity securities would call issuer.setInvestorLimits with argument [1999, 499, 0, 0, 0, 0, 0, 0]—meaning that OrgShare transfers which would result in the Org having more than 1,999 shareholders overall (inclusive of accredited shareholders) or more than 499 unaccredited shareholders will be programmatically blocked. Thus, the Org would prevent itself from prematurely becoming an Exchange-Act-reporting company under SEC Rule 12g-1/Section 12(g)(1) of the Exchange Act.

An important caveat: In configuring its transfer restrictions, an Org will be relying upon various assumptions that tie into its off-chain identity verification procedures—for example, it will assume that the representations made by prospective shareholders during the identity verification process (e.g. that they are buying shares for their own account and have sole control over an Ethereum address) are accurate. While these process-backed assumptions are not perfect, they are ultimately no more risky or uncertain than the working assumptions adopted by ordinary off-chain companies today. Indeed, one can argue that the risks for on-chain Orgs are lower, since ordinary companies cannot programmatically enforce their investor limits but must rely solely on contractual covenants to avoid gaining more investors than they intended.

Such assumptions may be more or less conservative, depending on the Org’s preferences. For example, a conservative Org may wish to assume that it reach $10M in assets at any time, and thus always set shareholder limits below the Rule 12g-1 thresholds. Another Org could might be willing to grow its shareholder base beyond those limits on the assumption that it will not reach $10M in assets. As a general purpose Org augmentation protocol, ZAP is designed to accommodate a wide array of risk preference choices.

<h4>iii. ID Verification</h4>

The technology-based components of the ID verification process will typically consist of three tools:

<ul>
    <li>an encrypted off-chain database of personally identifiable information (PII) regarding current and prospective Org members, which may include each such person’s:
        <ul>
            <li>full legal name</li>
            <li>country and region (encoded under the[ ISO 3166 standard](https://sft-protocol.readthedocs.io/en/latest/data-standards.html) for storage in KYCIssuer.sol or KYCRegistrar.sol)</li>
            <li>rating (non-accredited, accredited, QIB, etc.—varies by issuer & jurisdiction—will be represented by an arbitrary uint8 in KYCIssuer.sol or KYCRegistrar.sol)</li>
            <li>tax ID #</li>
            <li>one or more public Ethereum addresses</li>
            <li>a required renewal date (will be represented in epoch time in KYCIssuer.sol or KYCRegistrar.sol)</li>
            <li>the KECCAK256 hash of a subset of the foregoing PII (the IDHash)</li>
        </ul>
    </li>
    <li>an Org-specific smart contract (deployed as an instance of <span style="text-decoration:underline;">KYCIssuer.sol</span>) which, for each Org member, stores a mapping of that Org member’s IDHash to the Org member’s country code, region code, rating code (reflecting “accredited” status or lack thereof), required renewal date and Ethereum address(es) (RegistryData)</li>
    <li>an inter-Org smart contract (deployed as an instance of KYCRegistrar.sol) which stores the RegistryData of current and prospective members of many Orgs—such inter-Org registrars would likely be deployed and maintained by independent third parties running businesses related to securities tokens; for example, professional transfer agents or investor-accreditation-check services</li>
</ul>


KYCIssuer.sol and KYCRegistrar.sol essentially function as on-chain whitelists, but they only store IDHashes. Without access to the information contained in the private off-chain database of personally identifiable information, it would be impossible to correlate a particular IDHash with a particular person. Nonetheless, it is possible that the on-chain registrar smart contracts will be subject to GDPR or other privacy regulations, and the public nature and practical irreversibility of Ethereum may thus place the ZAP protocol at risk of being non-compliant, depending on the details of the Org. We anticipate that zero-knowledge proof and other techniques will eventually be added to address these issues. 

IDBase.getID is a public function of KYCIssuer.sol and KYCRegistrar.sol which accepts an IDHash as an argument. Thus, anyone can call IDBase.getID(<IDHash>) to determine the Ethereum address(es) and legal jurisdictions associated with an IDHash in the applicable smart contract registry.

KYCIssuer.sol and KYCRegistrar.sol are both “owned” smart contracts, with “owner” being an administrative role assignable to one or more Ethereum addresses at the time of deployment. In the case of KYCIssuer.sol, the owner will be the OrgCode (the smart contract deployed as an instance of IssuingEntity.sol for the applicable Org). The owner of KYCRegistrar.sol will be an arbitrary Ethereum address, which is likely to be controlled by a third party maintaining both an off-chain database and the registrar smart contract as a paid service.

Additional authorities (beyond “owner”) can be permissioned to call one or more administrative functions of the ID smart contract, either generally or solely with respect to persons located in one or more countries covered by that authority. In the case of KYCIssuer.sol, such permissioning will piggyback on the authority scheme of IssuingEntity.sol; in the case of KYCRegistrar.sol, authorities will be added directly. This granularity would enable a ZAP Org to appoint different transfer agents in different countries, each with the authority to perform administrative functions pertaining to and only to investors subject to the transfer agent’s jurisdictions. Although such functionality may not be important for the smaller, privately controlled Orgs that are likely to be the initial users of ZAP, they will be critical when ZAP Orgs are global public entities with shareholders in many jurisdictions, each with its own ever-shifting laws, rules and regulations.

The ownership and authority schemes in KYCIssuer.sol and KYCRegistrar.sol can be combined with a standard <span style="text-decoration:underline;">MultiSig Implementation</span> to impose M-of-N multisig rules regarding the combination of owners or authorities that is necessary to add new persons to the whitelist or add or remove restrictions from persons who are already on the whitelist.  

<h2>4. The Custodial Component</h2>

<h3>A. Custodial Law </h3>

In the traditional financial world, custodians for securities and other assets are commonplace. Although blockchain offers the opportunity for more direct interactions between an Org and its shareholders than is typical for many public companies, we nevertheless recognize that custodial arrangements will continue to have a role even for blockchain-augmented Orgs. Therefore, ZAP seeks to trust-minimize custodial arrangements to the greatest extent possible.

Custodial arrangements may be necessary or desirable in a number of contexts. For example,  Section 17(f) of the Investment Company Act requires registered management companies to custody their securities with a securities custodian such as a qualified bank, national securities exchange or securities depository. We envision a future in which digital securities deployed to public blockchains are ubiquitous and Orgs enter into triparty agreements with the investment companies who own the OrgShares and the qualified securities custodians who hold the OrgShares on behalf of the investment companies. These agreements could provide that custody of the OrgShares is maintained in transparent, trust-reduced custodial smart contracts that give both the Org and the investment companies relevant administrative powers such as the ability to ensure that the custodian does not violate transfer restrictions applicable to specific OrgShares. Eventually, such smart contract arrangements could become so feature-rich and reliable that they might lead to changes in law--for example, Section 17(f) might be amended to eliminate the requirement for a third-party custodian if an appropriate smart contract is used to safeguard the investment companies' assets as well or better than trusted custodial intermediaries. 
 
<h3>B. Custodial Code</h3>
 
Custodial smart contracts are approved to hold tokens representing OrgShares on behalf of multiple investors. Each custodial contract must be individually approved by an Org’s owners or administrators (through an association of the custodial smart contract with the OrgCode) before receiving tokens.

There are two broad categories of custodial smart contracts:

<ul>
    <li>>**Owned** custodial smart contracts are instances of OwnedCustodian.sol; they are controlled and maintained by a known legal entity such as a registered securities broker/dealer or a centralized securities exchange or cryptocurrency exchange.</li>
    <li>**Autonomous** custodial smart contracts are instances of IBaseCustodian.sol; they are autonomous in that once deployed there is no authority capable of exercising control over the contract. Autonomous custodial smart contracts will be useful for escrow arrangements, implementation of privacy protocols and the operation of decentralized exchanges.</li>
</ul>

As discussed above, an Org may need to carefully limit the number of investors it has in order to avoid opting into expensive regulatory regimes. For this reason, ZAP embodies conservative assumptions regarding how ownership of custodied OrgShares is counted. When an investor transfers a balance into a custodian it does not increase or decrease the overall investor count; instead the investor is now included in the list of beneficial owners represented by the custodian. Even if the investor now has a balance of 0 in their own wallet, they will still be included in the Org’s investor count.

<h4>i. Custodial Token Transfers</h4>

There are three types of token transfers related to Custodians.

<ul>
    <li>**Inbound**: transfers from an investor into the Custodian contract</li>
    <li>**Outbound**: transfers out of the Custodian contract to an investor’s wallet</li>
    <li>**Internal**: transfers involving a change of ownership within the Custodian contract. This is the only type of transfer that involves a change of ownership of the token, however no tokens actually move</li>
</ul>
Importantly, internal transfers are subject to the same permissioning regime established by the OrgCode. 

Permissioning checks for custodial transfers are identical to those of normal transfers. **TokenBase.checkTransferCustodian(_address _cust_, _address _from_, _address _to_, _uint256 _value_)** checks if a custodian internal transfer of tokens is permitted and returns **true** if the transfer is permitted. If the transfer is not permitted, the call will revert with the reason given in the error string.


**SecurityToken.transferCustodian(_address[2] _addr_, _uint256 _value_)** modifies investor counts and ownership records based on an internal transfer of ownership within the Custodian contract.


<h2>5. Misc. Additional Legal Considerations & Org Modules </h2>

<h3>A. Introduction to ZAP Modules</h3>

ZAP supports custom modules. Modules can be dynamically attached and detached from the OrgCode via IssuingEntity.attachModule(address _target, address _module) and IssuingEntity.detachModule(address _target, address _module). ZAP’s modularity is designed to maximize gas efficiency - modules may be detached as soon as they are no longer needed, and may even adjust their own hook points or detach themselves during the course of their lifecycle.
 
 There is no limit to the ways that OrgLaw can be encoded and programmatically enforced through such modules. For example, the current version of ZAP includes:

<ul>
    <li>the Waterfall Module (Waterfall.sol), a venture-capital-style preferred stock module that will honor the liquidation preferences and conversion features of preferred stock in a dividend, merger or other distribution event</li>
    <li>the Dividend Module (Dividend.sol), a module for automated distribution of dividends to OrgShare holders</li>
    <li>the Options Module (VestedOptions.sol), a module for automated vesting and exercise of stock options</li>
    <li>the Governance Module (Governance.sol), a minimal voting/governance module allowing for the supply of OrgShares to be throttled by a mandatory vote of current shareholders</li>
</ul>

Other possibilities including adding modules to handle crowdsales, country/time based token locks, automated right-of-first refusal procedures, complex shareholder votes, tender offer execution and bond redemption. 

<h3>B. Venture Capital Considerations & Preferred Stock Liquidation Module</h3>

Blockchain-based smart contracts, paired with tokenized OrgShares, create a powerful tool for venture-backed companies with complex preferred stock capital structures, partnerships with tiered distribution waterfalls and any Org with mezzanine debt. As envisioned by Vice Chancellor J. Travis Laster of the Delaware Court of Chancery:

  >By accurately programming different classes or series of preferred stock [to] carry different voting rights, conversion rights, payment rights, and other features…up front, a complex capital structure can be administered automatically, without human intervention. If, for example, the corporation wishes to issue additional shares, but a particular series of preferred stock has a blocking right, then the stock ledger could be coded to prevent the shares from being issued unless the requisite vote is received. Smart contracting technology also could be used to implement conversion provisions and would simplify the often difﬁcult task of calculating conversion rates, particularly when anti-dilution formulas come into play. If the features were programmed accurately up front, then the calculations would take place automatically.
 
ZAP is working toward realizing this vision in a number of ways. 

The experimental Waterfall Module, [Waterfall.sol](https://github.com/iamdefinitelyahuman/ZAP-Tech/blob/waterfall/contracts/modules/Waterfall.sol), encodes the distribution rules for a corporate-style Org's entire capital structure: common stock, common stock options, and any number of series of preferred stock. This enables automatic and trust-reduced distribution to all OrgShareholders of their respective portions of any and all dividends, merger consideration and liquidation proceeds that the Org might have occasion to pay out to OrgShareholders.

Preferred stock will typically be convertible to common stock at some ratio and have a 'liquidation preference' that is hard-coded at the time of issuance and taken into account by the Waterfall Module in allocating distributions. Varieties of preferred stock recognized by the Waterfall Module include fully participating, partially participating and non-participating preferred stock; given a distribution amount, the Waterfall Module will determine whether the preferred stock should be treated on a preferred-stock basis or an as-converted-to-common-stock basis (i.e., which treatment will result in a greater payment to the preferred stock) and allocate the distribution amount accordingly. The Waterfall Module can also pay out stock options on a net-exercise basis by deducting the exercise price of the option from the otherwise applicable per-share merger consideration.  

For example, if the Org is a 'target' Org to be acquired by an 'acquirer' Org in a statutory merger pursuant to which the acquirer Org becomes the owner of all OrgShares, the acquirer Org would deposit the merger consideration in the form of ETH, DAI or another Ethereum-based cryptocurrency to the address of a smart contract escrow. The merger consideration would then automatically be divvied-up in accordance with the liquidation priorities of the different stockholders, with preferred stockholders at the top of the stack and common stockholders at the bottom--unless the preferred stock is getting paid on an as-converted-to-common-stock basis or is participating, in which case the preferred stock would be pari passu with the common stock for all or a portion of the merger consideration. The allocated amounts would be distributed to the addresses where the stockholders held the token-certificates representing the various issued and outstanding shares of capital stock or stock options. 

Today in regular M&A deal execution, these processes require a cadre of lawyers, transfer agents, escrow agents and payment agents. The roles of these intermediaries and trust holes, and the manual and error-prone processes they rely upon, could be dramatically reduced or, in certain cases, even completely eliminated with ZAP. Alternatively, the Waterfall Module can be used simply to calculate the relevant amounts in a transparent and trust-reduced manner, and distribution could then be handled on a more ad hoc basis--entirely on-chain, entirely off-chain, or partially on-chain & off-chain. This should be the future; it just makes sense. 

The Governance Module, [Governance.sol](https://github.com/zerolawtech/SFT-Protocol/blob/master/contracts/modules/Governance.sol), is a minimal proof of concept that may be used as a starting point for enabling OrgShareholders to vote on governance issues.  It can be combined with a checkpoint module to build whatever specific setup is required by an Org. Although the current version is modest in scope, it provides a critical function for corporate-style Orgs--namely, requiring OrgShareholder approval before increasing the number of shares of a given class or series of stock that the corporation is authorized to issue. This vote is also legally required in the case of corporations, and takes the form of stockholders voting on a proposed amendment to the corporation's certificate of incorporation. With ZAP, that vote can be held on chain.
  
<h3>C. Unique Challenges Posed by the Contractual Nature of OrgShares</h3>

OrgShares are bundles of legal rights associated with a blockchain token that functions as a transferable instrument. Unlike with typical ERC20 tokens on Ethereum or other 'bearer instruments' such as protocol tokens, persons in markets for stock, membership interests or other types of shares, or even debt instruments like bonds, typically consider it important to ensure that buyers and sellers of the instrument understand that the instrument represents a bundle of legal rights and the nature and limitations of those legal rights. 

In traditional equity markets, purchasers of securities typically have sufficient information to evaluate their investment decision because: (1) they are buying from a stock exchange or broker-dealer where all the assets available are typically shares of corporate common stock having very similar terms; (2) the shares in question are those of very well known public corporations who are registered with the SEC and all of whose governance documents (certificate of incorporation, bylaws, etc.) can be accessed by anyone on[ https://www.sec.gov/edgar/](https://www.sec.gov/edgar/); and (3) they are piggybacking off of the due diligence and analysis conducted by a wide variety of market “gatekeepers” such as attorneys, underwriters, securities analysts, stock exchanges like NASDAQ and NYSE, broker/dealers, proxy advisory firms like ISS, institutional shareholders and the SEC, any or all of which would be apt to identify and publicize any particularly off-market features (like CEO voting control in the case of companies like Facebook). One might consider traditional securities markets, interfaces and intermediaries as providing a kind of custom UX which puts the buyer of a security on notice regarding the nature of the instrument and associated rights. As a result of this custom UX, it would be surprising if, for example, a person bought a share of Apple common stock but believed they were buying a bond or a cash credit for the Apple store. In the unlikely event such confusion were to occur, it would almost certainly be a result of 'user error' in the un-ironic sense--a kind of willful blindness to the information available.   

In contrast, tokens on Ethereum typically do not represent bundles of legal rights and trade freely through any Ethereum wallet or Ethereum software client rather than solely through broker-dealers with fiduciary and disclosure obligations. Transactions in ordinary ERC20 tokens may occur through a variety of interfaces and instrumentalities, whether on a p2p basis or by means of centralized cryptocurrency exchanges (e.g. Binance, Kraken and Coinbase) or decentralized exchange smart contracts (e.g., Uniswap and 0x). In general, a user transacting through such interfaces could reasonably believe the token they are buying is a cryptonative asset rather than a contractual right. 


Although user confusion is always undesirable, when it comes to transactions in securities instruments, it could be disastrous. No company should want to sell its shares to a person who thinks those shares are a utility token. This could lead to significant confusion--for example, a buyer might not be on notice that the token it holds could be converted into another token pursuant to a merger transaction under applicable law. A buyer might not know that it needs to contact the issuer and supply a Form W-9 in order to receive dividends on the share. A buyer might not understand that it has the right to vote on certain corporate transactions, or might not receive proxy statements explaining the proposals to be voted upon. 

Thus, along with blockchain’s tremendous potential for decentralizing transactions and opening new markets comes a resulting vacuum of infrastructure and best practices within those markets. If the OrgShares of pre-IPO Orgs become tokenized and freely transferable on a trust-reduced basis, the informational mechanisms that exist for traditional public equities will not be available to ensure that purchasers of these OrgShares are fully informed. 

The Org and its members should care about this issue, for several reasons. Most importantly, the Org and its members will not want to face lawsuits from individuals who believed they were acquiring a token that had different economic or legal features than the OrgShare does. The Org will also want to ensure that any limitations of legal liability, transfer restrictions or other contractual arrangements involved in membership in the Org are specifically consented to by each OrgShare holder; otherwise there is a risk they will not be legally enforceable against the OrgShare member—in the context where transfer restrictions and may be automatically enforced, this is arguably even more important, since the purchaser will literally be unable to perform certain kinds of transactions with the token. Finally, as discussed in more detail below, treating the tokens representing OrgShares consistently with their intended function of being contractual instruments will mitigate the risk of them being deemed convertible virtual currencies and the Org being regulated as a money services business.

An additional concern is that money transmission is a highly regulated activity. Regulation of money transmission and regulation of securities instruments historically have been handled under completely separate and mutually exclusive statutory regimes. With blockchain, however, the distinctions between securities and money are eroding, creating the potential that a single token may be simultaneously regulated as both a security and a currency, and a single token issuer may be regulated both as a securities issuer and a financial institution. For example, the U.S. Financial Crimes Enforcement Network (FinCEN)'s recent guidance memorandum entitled ["Application of FinCEN’s Regulations to Certain Business Models Involving Convertible Virtual Currencies"](https://www.fincen.gov/sites/default/files/2019-05/FinCEN%20CVC%20Guidance%20FINAL.pdf) contains the following somewhat surprising guidance, which establishes how secondary trading of OrgShares may subject unwitting Orgs to all the same regulations as bonafide money transmitters like PayPal merely if the token certificates representing the OrgShares trade too freely and become used as general substitutes for value: 

>money transmission could involve...the issuance and subsequent acceptance and transmission of a digital token that evidenced ownership of a certain amount of a commodity, security, or futures contract...\[I]f assets that other regulatory frameworks define as commodities, securities, or futures contracts were to be specifically issued or later repurposed to serve as a currency substitute, then the asset itself could be a type of value that substitutes for currency, the transfer of which could constitute money transmission. Therefore...money transmission may occur when a person (or an agent, or a mechanical or software agency owned or operated by such person) not exempt from MSB status:...issues physical or digital tokens evidencing ownership of commodities, securities, or futures contracts that serve as value that substitutes for currency in money transmission transactions

Idealistically, one might bemoan the fragmentary and myopic nature of these regulations, as well as their political motivations, but for practical purposes an Org would be well advised to seek to avoid being deemed a money transmitter and solely function as a partnership actively co-managed by all partners or as a securities issuer with a mix of active managers and passive investors. In doing so, Orgs will need to ensure that there are appropriate 'frictions' that put users on notice that they are buying an OrgShare, not a currency. 

Addressing these issues creates a unique challenge for blockchain-augmented Orgs: namely, how can the Org ensure that a person who has the UX of simply transacting with one token among many knows that the token they are transacting in is not a cryptonative asset, not a utility token, but rather is a very specific OrgShare with very specific legal rights and limitations attached? To achieve this in the context of public unpermissioned blockchains, new information channels and consent mechanisms will be required. However, these mechanisms should be designed in a way that preserves the peer-to-peer, trust-reducing virtues of blockchain by avoiding the reintroduction of gatekeepers and intermediaries; otherwise, what is the point of using a blockchain at all?
  
In an ordinary client-server architecture, the solution would be simple—force users to buy through your app and present them with the appropriate contract to sign as part of the transaction flow. An Org may try to approximate something similar in the blockchain context by creating its own custom interface or wallet for reading from/writing to the Ethereum blockchain and interacting with Ethereum nodes, and such an interface could provide context-specific UX supplying current and prospective Org members with useful notices about the legal terms of the OrgShares, transfer restrictions applicable to OrgShares and other material information. An Org may also publicly encourage persons transacting in OrgShares to do so only through the Org's official wallet so that they understand the nature of the rights associated with the token they are transacting in. However, because of the permissionless, decentralized architecture of Ethereum, an Org can never be certain that all OrgShare transactions will occur through the Org's official interface. Buyers or sellers of OrgShares may still use the Go-Ethereum client, Parity client, any wallet, or any other means of interacting with the Ethereum blockchain and network; in such cases, the Org will have no control over the user experience, and there will be a risk that persons buying the token will not understand that it is an OrgShare and carries certain rights as well as certain limitations such as transfer restrictions.  

ZAP thus addresses this issue in at least two ways:

<ul>
 <li>ZAP trust-minimizes the authentication of legal documents pertaining to the Org. The Org admins can record the hash of a legal document (e.g., the Org’s certificate of incorporation, or a Shareholders’ Agreement) to the blockchain via the OrgCode (the Org’s instance of IssuingEntity.sol). Current or prospective shareholders who receive the document through potentially compromised or secondhand sources can then verify that the hash of the document matches the recorded hash available from the OrgCode.  This process can also assist with version control, since Org governance documents may frequently be amended and shareholder will want to ensure they are working from the most current version.</li>
    
 <li>In a future version of ZAP, we intend to add a module that enables Orgs to gate sales/purchases of OrgShares in the secondary market with an automated escrow process. This would enable issuers to ensure that the contractual terms of OrgShares are agreed upon by future buyers, without representatives of the Org needing to manually permission each OrgShare transaction. Each OrgShare purchase/sale could be required to be effected through a smart contract escrow. The OrgShare tokens and the purchase price (any Ethereum-compatible tokens) would be deposited into the escrow smart contract. The would-be purchaser would be directed to a website to e-sign an acknowledgement of having received disclosures regarding the nature of the OrgShares. The hash of that acknowledgement and the purchaser's Ethereum address could then be recorded to the smart contract escrow, evidencing that the information had been received and the acknowledgement signed, whereupon the OrgShare tokens would be automatically transferred to the address of the purchaser and the token-denominated purchase price would be automatically transferred to the address of the seller out of the smart contract escrow. The smart contract escrow could also be configured to permit termination by the would-be seller if the required documents are not proffered by the would-be purchaser within some specified period--e.g. 48 hours. Upon a termination,  the OrgShare tokens and purchase price tokens would revert to the original owners, minus a penalty to be paid by the would-be purchaser for failure to deliver the documents within the required time. In effect, this arrangement would simulate a traditional share purchase agreement which is signed by the parties on one date and then provides for a later 'closing date' triggered when various conditions precedent--such as the signing of additional documents by one or more parties--have been satisfied. This is a 'smart contract' along the lines originally proposed by Nick Szabo--i.e., a mechanism for automated and trust-reducing the performance-or-breach structure of a share purchase agreement.</li> 
  </ul>