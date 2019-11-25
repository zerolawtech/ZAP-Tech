# SFT-Protocol/contracts/modules

Optional modules that may be attached to core contracts as needed.

## Subfolders

* `bases`: Inherited base contracts used by modules.

## Contracts

* `bases/Modular.sol`: Contains module base contracts. All modules **must** inherit one of these base contracts, or implement their functionality.
* `bases/Checkpoint.sol`: Base module for creating a single balance checkpoint for a token.
* `Dividend.sol`: Token module for paying out divedends denominated in ETH.
* `MultiCheckpoint.sol`: Issuer module for creating many checkpoints across multiple tokens.
* `VestedOptions.sol`: `BookShare` module for issuing vested stock options.
