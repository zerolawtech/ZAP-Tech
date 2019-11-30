# ZAP-Tech/tests

Unit testing of this project is performed with [Brownie](https://github.com/iamdefinitelyahuman/brownie).

To run the tests:

```bash
$ pytest tests/
```

A [dockerfile](Dockerfile) is available if you are experiencing issues.

## Organization

Tests for ZAP are sorted by the main contract being tested, then optionally by the main contract being interacted with and the methods being called.

## Subfolders

* `custodians`: Test folders for custodian contracts.
* `modules`: Test folders for module contracts.

## Test Folders

* `OrgCode`: Tests that target [OrgCode](../contracts/OrgCode.sol).
* `IDVerifierOrg`: Tests that target [IDVerifierOrg](../contracts/IDVerifierOrg.sol).
* `IDVerifierRegistrar`: Tests that target [IDVerifierRegistrar](../contracts/IDVerifierRegistrar.sol).
* `CertShare`: Tests that target [CertShare](../contracts/CertShare.sol).
* `BookShare`: Tests that target [BookShare](../contracts/BookShare.sol).
