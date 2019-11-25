# SFT-Protocol/contracts

All solidity contract sources are inside this folder or one of it's subfolders.

## Subfolders

* `bases`: Inherited base contracts used by the core contracts.
* `custodians`: Custodian contracts.
* `interfaces`: Commonly used contract interfaces.
* `modules`: Optional modules that may be attached to core contracts as needed.
* `modules/bases`: Inherited base contracts used by optional modules.
* `open-zeppelin`: SafeMath.

## Contracts

* `OrgCode.sol`: Central contract that ties together tokens, verifiers, and custodians.
* `IDVerifierRegistrar.sol`: Verifier contract that may be shared across many orgs.
* `IDVerifierOrg.sol`: Streamlined verifier contract for use by a single org.
* `SecurityToken.sol`: Token contract derived from ERC-20 standard. Represents fungible, book-entry style securities.
* `NFToken.sol`: Token contract derived from ERC-20 standard. Represents non-fungible certificated securities.
